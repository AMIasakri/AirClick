"""
AirClick - کنترل موس با دو دست
دست موس = حرکت | دست کلیک = کلیک‌ها
"""

import cv2
import sys
import os
import time
import tkinter as tk
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import CAMERA_SETTINGS, DISPLAY_SETTINGS, COLORS, MOUSE_SETTINGS
from core.hand_tracker import HandTracker
from core.gesture_recognizer import GestureRecognizer, GestureStabilizer
from core.mouse_controller import MouseController
from ui.overlay import OverlayRenderer
from utils.helpers import log_message, get_fps


class HelpWindow:
    @staticmethod
    def show():
        root = tk.Tk()
        root.title("AirClick - راهنما")
        root.geometry("500x600")
        root.resizable(False, False)
        root.configure(bg='#0a0a1a')
        root.attributes('-topmost', True)

        tk.Label(root, text="AIRCLICK PRO", font=("Segoe UI", 20, "bold"),
                 fg="#e94560", bg='#0a0a1a').pack(pady=(18, 4))
        tk.Label(root, text="کنترل موس با دو دست", font=("Segoe UI", 10),
                 fg="#888899", bg='#0a0a1a').pack()
        tk.Frame(root, height=2, bg='#e94560').pack(fill='x', padx=30, pady=8)

        sections = [
            ("دست موس (سمت چپ تصویر)", "#51cf66", [
                ("☝️  فقط اشاره بالا", "حرکت موس"),
                ("✌️  اشاره + وسط بالا", "Drag"),
            ]),
            ("دست کلیک (سمت راست تصویر)", "#ff922b", [
                ("👇  اشاره پایین", "کلیک چپ"),
                ("🖕  وسط پایین", "کلیک راست"),
                ("✊  مشت", "کلیک وسط"),
                ("✌️↓  اشاره+وسط پایین", "دابل کلیک"),
                ("💍  حلقه پایین", "اسکرول"),
            ]),
        ]
        for title, color, items in sections:
            tk.Label(root, text=title, font=("Segoe UI", 11, "bold"),
                     fg=color, bg='#0a0a1a').pack(pady=(10, 4), anchor='w', padx=20)
            for gesture, action in items:
                row = tk.Frame(root, bg='#12122a')
                row.pack(pady=2, fill='x', padx=20)
                tk.Label(row, text=gesture, font=("Segoe UI", 10), fg="#fff",
                         bg='#12122a', width=22, anchor='w').pack(side='left', padx=10, pady=5)
                tk.Label(row, text=action, font=("Segoe UI", 9),
                         fg=color, bg='#12122a').pack(side='right', padx=10)

        for tip in ["💡 نور کافی داشته باش", "↔️  دست‌ها را از هم فاصله بده",
                    "⌨️  q=خروج | h=راهنما | d=دیباگ"]:
            tk.Label(root, text=tip, font=("Segoe UI", 9),
                     fg="#666688", bg='#0a0a1a').pack(pady=2)

        tk.Button(root, text="بستن", command=root.destroy, font=("Segoe UI", 10, "bold"),
                  bg="#e94560", fg="white", padx=40, pady=8, relief='flat',
                  cursor="hand2").pack(pady=16)
        root.mainloop()


class AirClick:
    def __init__(self):
        log_message("=" * 50)
        log_message("AirClick Pro Starting...")
        log_message("=" * 50)

        self.hand_tracker = HandTracker()
        self.gesture_recognizer = GestureRecognizer()
        self.click_gesture_stabilizer = GestureStabilizer(
            MOUSE_SETTINGS.get('gesture_stability_frames', 3),
        )
        self.mouse_controller = MouseController()
        self.overlay_renderer = OverlayRenderer()

        self.frame_width = CAMERA_SETTINGS['frame_width']
        self.frame_height = CAMERA_SETTINGS['frame_height']
        self.show_fps = DISPLAY_SETTINGS['show_fps']
        self.show_landmarks = DISPLAY_SETTINGS['show_landmarks']
        self.show_debug = DISPLAY_SETTINGS['show_debug']
        self.click_cooldown = MOUSE_SETTINGS['action_cooldown']

        self.running = False
        self.frame_count = 0
        self.start_time = time.time()

        self.left_hand_index = -1
        self.right_hand_index = -1
        self.current_gesture_right = "WAITING"
        self.current_gesture_left = "WAITING"
        self.mouse_mode = "LOCKED"

        self.last_click_time = 0
        self.last_click_type = None
        self.left_click_active = False
        self.right_click_active = False
        self.middle_click_active = False
        self.double_click_active = False
        self.scroll_active = False
        self.drag_active = False

        self.movement_latched = False
        self.cursor_tip = None
        self.hand_was_detected = False
        self.hands_too_close = False
        self.debug_info = []

        self.cap = cv2.VideoCapture(CAMERA_SETTINGS['camera_id'])
        if not self.cap.isOpened():
            log_message("Camera not found!", "ERROR")
            sys.exit(1)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        log_message(f"Camera: {self.frame_width}x{self.frame_height}")

    def run(self):
        self.running = True
        win_w = DISPLAY_SETTINGS.get('window_width', 680)
        win_h = DISPLAY_SETTINGS.get('window_height', 540)

        cv2.namedWindow("AirClick", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("AirClick", win_w, win_h)
        cv2.setWindowProperty("AirClick", cv2.WND_PROP_TOPMOST, 1)

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    log_message("Could not read a frame from the camera.", "ERROR")
                    break

                frame = cv2.flip(frame, 1)
                self.process_frame(frame)
                display = self.draw_overlay(frame)

                cv2.imshow("AirClick", display)
                self.frame_count += 1

                key = cv2.waitKey(1) & 0xFF
                if key in (ord('q'), 27):
                    break
                if key == ord('h'):
                    threading.Thread(target=HelpWindow.show, daemon=True).start()
                if key == ord('d'):
                    self.show_debug = not self.show_debug
        finally:
            self.cleanup()

    def process_frame(self, frame):
        self.hand_tracker.process_frame(frame)

        self.right_hand_index = self.hand_tracker.get_mouse_hand_index()
        self.left_hand_index = self.hand_tracker.get_click_hand_index()
        self.cursor_tip = None
        self.hands_too_close = self.hand_tracker.hands_too_close

        any_hand = self.left_hand_index != -1 or self.right_hand_index != -1

        if self.right_hand_index != -1:
            self._process_mouse_hand(frame)
        else:
            self._reset_mouse_hand()

        if self.left_hand_index != -1:
            self._process_click_hand(frame)
        else:
            self._reset_click_hand()

        if not any_hand:
            self._handle_no_hands()
        else:
            self.hand_was_detected = True

        self._update_debug_info()

    def _process_mouse_hand(self, frame):
        if self.hands_too_close:
            self._reset_mouse_hand()
            self.mouse_mode = "LOCKED"
            return

        live = self.hand_tracker.is_hand_live(self.right_hand_index)
        fingers = self.hand_tracker.get_fingers_status(self.right_hand_index)
        if not fingers:
            return

        is_drag = self.hand_tracker.is_drag_gesture(self.right_hand_index)
        can_move = self.hand_tracker.is_pointer_gesture(
            self.right_hand_index, latched=self.movement_latched,
        )

        if is_drag:
            self.current_gesture_right = "DRAG"
        elif can_move:
            self.current_gesture_right = "MOVING"
        else:
            self.current_gesture_right = self.gesture_recognizer.recognize(fingers)

        h, w, _ = frame.shape

        if is_drag and live:
            if not self.drag_active:
                self.mouse_controller.start_drag('left')
                self.drag_active = True
            tip = self.hand_tracker.get_index_tip((h, w, 3), self.right_hand_index, live_only=True)
            if tip:
                self.mouse_controller.move(
                    tip[0], tip[1], w, h,
                    reanchor=not self.movement_latched,
                )
                self.cursor_tip = tip
                self.movement_latched = True
            self.mouse_mode = "DRAGGING"
        elif is_drag:
            self.mouse_mode = "ANCHOR"
        else:
            if self.drag_active:
                self.mouse_controller.stop_drag()
                self.drag_active = False

            if can_move and live:
                tip = self.hand_tracker.get_index_tip((h, w, 3), self.right_hand_index, live_only=True)
                if tip:
                    self.mouse_controller.move(
                        tip[0], tip[1], w, h,
                        reanchor=not self.movement_latched,
                    )
                    self.cursor_tip = tip
                    self.movement_latched = True
                self.mouse_mode = "MOVING"
            elif can_move:
                self.mouse_mode = "ANCHOR"
            else:
                self.movement_latched = False
                self.mouse_controller.pause_tracking()
                self.mouse_mode = "READY" if live else self.mouse_mode

        box = self.hand_tracker.get_bounding_box(self.right_hand_index)
        if box:
            if self.show_landmarks and live:
                self.hand_tracker.draw_landmarks(
                    frame, COLORS['cursor_point'], self.right_hand_index,
                    show_mesh=DISPLAY_SETTINGS.get('show_hand_mesh', True),
                )

    def _process_click_hand(self, frame):
        if self.hands_too_close:
            self._reset_click_hand()
            return

        live = self.hand_tracker.is_hand_live(self.left_hand_index)
        fingers = self.hand_tracker.get_click_fingers_status(self.left_hand_index)
        if not fingers:
            return

        raw_gesture = self.gesture_recognizer.recognize_click_hand(fingers)
        stable_gesture = self.click_gesture_stabilizer.update(raw_gesture)
        gesture = stable_gesture
        self.current_gesture_left = (
            stable_gesture or self.gesture_recognizer.gesture_names['unknown']
        )
        now = time.time()
        cooldown_ok = now - self.last_click_time > self.click_cooldown

        if live and gesture is not None:
            if self.gesture_recognizer.is_scroll(gesture):
                h, _, _ = frame.shape
                center_y = self.hand_tracker.get_hand_center_y(self.left_hand_index, h)
                if center_y is not None:
                    self.mouse_controller.scroll(center_y, reanchor=not self.scroll_active)
                    self.scroll_active = True
                    self.mouse_mode = "SCROLLING"
            elif self.scroll_active:
                self.mouse_controller.stop_scroll()
                self.scroll_active = False

            if self.gesture_recognizer.is_left_click(gesture) and not self.left_click_active and cooldown_ok:
                self._fire_click('left', self.mouse_controller.click_left)
            if self.gesture_recognizer.is_right_click(gesture) and not self.right_click_active and cooldown_ok:
                self._fire_click('right', self.mouse_controller.click_right)
            if self.gesture_recognizer.is_middle_click(gesture) and not self.middle_click_active and cooldown_ok:
                self._fire_click('middle', self.mouse_controller.click_middle)
            if self.gesture_recognizer.is_double_click(gesture) and not self.double_click_active and cooldown_ok:
                self._fire_click('double', self.mouse_controller.click_double)

            self.left_click_active = self.gesture_recognizer.is_left_click(gesture)
            self.right_click_active = self.gesture_recognizer.is_right_click(gesture)
            self.middle_click_active = self.gesture_recognizer.is_middle_click(gesture)
            self.double_click_active = self.gesture_recognizer.is_double_click(gesture)
        else:
            self.left_click_active = False
            self.right_click_active = False
            self.middle_click_active = False
            self.double_click_active = False
            if self.scroll_active:
                self.mouse_controller.stop_scroll()
                self.scroll_active = False

        box = self.hand_tracker.get_bounding_box(self.left_hand_index)
        if box:
            flash = now - self.last_click_time < 0.4
            if flash and self.last_click_type == 'left':
                color, label = COLORS['box_click'], "LEFT CLICK"
            elif flash and self.last_click_type == 'right':
                color, label = (0, 165, 255), "RIGHT CLICK"
            elif flash and self.last_click_type == 'middle':
                color, label = (180, 180, 180), "MIDDLE CLICK"
            elif flash and self.last_click_type == 'double':
                color, label = (200, 100, 255), "DOUBLE CLICK"
            elif self.scroll_active:
                color, label = (200, 100, 200), "SCROLL"
            else:
                color, label = COLORS['box_left'], self.current_gesture_left

            if self.show_landmarks and live:
                self.hand_tracker.draw_landmarks(
                    frame, color, self.left_hand_index,
                    show_mesh=DISPLAY_SETTINGS.get('show_hand_mesh', True),
                )

    def _fire_click(self, click_type, method):
        method()
        self.last_click_time = time.time()
        self.last_click_type = click_type

    def _reset_mouse_hand(self):
        if self.drag_active:
            self.mouse_controller.stop_drag()
            self.drag_active = False
        self.movement_latched = False
        self.mouse_controller.pause_tracking()
        self.current_gesture_right = "WAITING"

    def _reset_click_hand(self):
        self.click_gesture_stabilizer.reset()
        self.left_click_active = False
        self.right_click_active = False
        self.middle_click_active = False
        self.double_click_active = False
        if self.scroll_active:
            self.mouse_controller.stop_scroll()
            self.scroll_active = False
        self.current_gesture_left = "WAITING"

    def _handle_no_hands(self):
        self._reset_mouse_hand()
        self._reset_click_hand()
        self.mouse_mode = "LOCKED"

    def _update_debug_info(self):
        self.debug_info = [
            f"Mouse: {self.right_hand_index}  Click: {self.left_hand_index}",
            f"Mode: {self.mouse_mode}  L: {self.current_gesture_left}",
        ]
        if self.left_hand_index != -1:
            f = self.hand_tracker.get_click_fingers_status(self.left_hand_index)
            if f:
                self.debug_info.append(f"Fingers: idx={f[1]} mid={f[2]} rng={f[3]} pnk={f[4]}")

    def _draw_hand_region(self, frame, box, color, hand_label, live, status):
        (x1, y1), (x2, y2) = box
        thickness = 2 if live else 1
        lt = cv2.LINE_AA

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            cv2.rectangle(frame, (x1 + dx, y1 + dy), (x2 + dx, y2 + dy), (0, 0, 0), thickness + 1, lt)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness, lt)

        corner = 18
        for cx, cy, sx, sy in [(x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)]:
            cv2.line(frame, (cx, cy), (cx + sx * corner, cy), color, 3, lt)
            cv2.line(frame, (cx, cy), (cx, cy + sy * corner), color, 3, lt)

        tag = hand_label if live else f"{hand_label} (mem)"
        cv2.putText(frame, tag, (x1, max(y1 - 8, 14)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, lt)
        cv2.putText(frame, status, (x1, y2 + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, lt)

    def _draw_crosshair(self, frame, tip, color):
        x, y = tip
        size = 14
        cv2.line(frame, (x - size, y), (x + size, y), color, 1, cv2.LINE_AA)
        cv2.line(frame, (x, y - size), (x, y + size), color, 1, cv2.LINE_AA)
        cv2.circle(frame, (x, y), 6, color, 2, cv2.LINE_AA)
        cv2.circle(frame, (x, y), 2, (255, 255, 255), -1, cv2.LINE_AA)

    def draw_overlay(self, frame):
        def hand_state(index):
            if index == -1:
                return None, False
            return self.hand_tracker.get_bounding_box(index), self.hand_tracker.is_hand_live(index)

        right_box, right_live = hand_state(self.right_hand_index)
        left_box, left_live = hand_state(self.left_hand_index)
        left_color = COLORS['box_left']
        if time.time() - self.last_click_time < 0.4:
            left_color = {
                'left': COLORS['box_click'],
                'right': (0, 165, 255),
                'middle': (180, 180, 180),
                'double': (200, 100, 200),
            }.get(self.last_click_type, left_color)
        elif self.scroll_active:
            left_color = COLORS['box_scroll']

        state = {
            'right_box': right_box,
            'right_color': (0, 180, 255) if self.drag_active else COLORS['box_right'],
            'right_gesture': self.current_gesture_right,
            'right_live': right_live,
            'left_box': left_box,
            'left_color': left_color,
            'left_gesture': self.current_gesture_left,
            'left_live': left_live,
            'cursor_tip': self.cursor_tip,
            'right_landmarks': None,
            'left_landmarks': None,
            'show_landmarks': False,
            'show_fps': self.show_fps,
            'fps': get_fps(self.start_time, self.frame_count),
            'mode': self.mouse_mode,
            'hand_separation': self.hand_tracker.hand_separation,
            'hands_too_close': self.hands_too_close,
            'show_debug': self.show_debug,
            'debug_info': self.debug_info,
            'hand_was_detected': self.hand_was_detected,
        }
        return self.overlay_renderer.render(frame, state)

    def _draw_hand_zones(self, frame):
        h, w = frame.shape[:2]
        split_x = w // 2
        zone_overlay = frame.copy()

        cv2.rectangle(zone_overlay, (0, 42), (split_x, h - 48), (0, 60, 0), -1)
        cv2.rectangle(zone_overlay, (split_x, 42), (w, h - 48), (0, 40, 80), -1)
        frame = cv2.addWeighted(zone_overlay, 0.12, frame, 0.88, 0)

        for y in range(42, h - 48, 16):
            cv2.line(frame, (split_x, y), (split_x, min(y + 8, h - 48)), (180, 180, 200), 1, cv2.LINE_AA)

        cv2.putText(frame, "MOUSE", (split_x // 2 - 35, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLORS['box_right'], 1, cv2.LINE_AA)
        cv2.putText(frame, "CLICK", (split_x + split_x // 2 - 28, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLORS['box_left'], 1, cv2.LINE_AA)

        if self.hand_tracker.hand_separation is not None:
            sep_color = (0, 80, 255) if self.hands_too_close else (120, 120, 140)
            cv2.putText(frame, f"Gap: {int(self.hand_tracker.hand_separation)}px",
                        (split_x - 40, h - 58), cv2.FONT_HERSHEY_SIMPLEX, 0.4, sep_color, 1, cv2.LINE_AA)

        return frame

    def cleanup(self):
        log_message("Cleaning up...")
        self.running = False
        try:
            self.mouse_controller.reset()
            self.hand_tracker.release()
            self.cap.release()
            cv2.destroyAllWindows()
        except Exception:
            pass
        log_message("AirClick stopped.")


if __name__ == "__main__":
    try:
        app = AirClick()
        app.run()
    except KeyboardInterrupt:
        log_message("Interrupted")
    except Exception as e:
        log_message(f"Error: {e}", "ERROR")
    finally:
        cv2.destroyAllWindows()
