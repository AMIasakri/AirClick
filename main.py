"""
AirClick - کنترل موس با دو دست
دست راست = حرکت موس (حرکت نسبی)
دست چپ = اشاره پایین: کلیک چپ | وسط پایین: کلیک راست
"""

import cv2
import sys
import os
import time
import tkinter as tk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import CAMERA_SETTINGS, DISPLAY_SETTINGS, COLORS, MOUSE_SETTINGS
from core.hand_tracker import HandTracker
from core.gesture_recognizer import GestureRecognizer
from core.mouse_controller import MouseController
from utils.helpers import log_message, get_fps


class HelpWindow:
    @staticmethod
    def show():
        root = tk.Tk()
        root.title("AirClick - راهنما")
        root.geometry("500x560")
        root.resizable(False, False)
        root.configure(bg='#0a0a1a')
        root.attributes('-topmost', True)

        header = tk.Frame(root, bg='#0a0a1a')
        header.pack(fill='x', pady=18)

        tk.Label(header, text="AIRCLICK PRO",
                 font=("Segoe UI", 20, "bold"), fg="#e94560", bg='#0a0a1a').pack()
        tk.Label(header, text="کنترل موس با دو دست",
                 font=("Segoe UI", 10), fg="#888899", bg='#0a0a1a').pack()

        tk.Frame(root, height=2, bg='#e94560').pack(fill='x', padx=30, pady=8)

        gestures_frame = tk.Frame(root, bg='#0a0a1a')
        gestures_frame.pack(pady=8, padx=20, fill='x')

        sections = [
            ("دست راست — حرکت موس", "#51cf66", [
                ("☝️  فقط اشاره بالا", "حرکت موس (نسبی)", "#51cf66"),
                ("🖐️  همه انگشتان باز", "آماده", "#4fc3f7"),
            ]),
            ("دست چپ — کلیک", "#ff922b", [
                ("👇  اشاره پایین", "کلیک چپ", "#ff6b6b"),
                ("🖕  وسط پایین (اشاره بالا)", "کلیک راست", "#ffd43b"),
            ]),
        ]

        for title, title_color, items in sections:
            tk.Label(gestures_frame, text=title,
                     font=("Segoe UI", 11, "bold"), fg=title_color, bg='#0a0a1a').pack(pady=(12, 6), anchor='w')
            for gesture, action, color in items:
                row = tk.Frame(gestures_frame, bg='#12122a')
                row.pack(pady=3, fill='x')
                tk.Label(row, text=gesture, font=("Segoe UI", 10),
                         fg="#ffffff", bg='#12122a', width=22, anchor='w').pack(side='left', padx=10, pady=6)
                tk.Label(row, text=action, font=("Segoe UI", 9),
                         fg=color, bg='#12122a').pack(side='right', padx=10)

        tk.Frame(root, height=1, bg='#2a2a4a').pack(fill='x', padx=30, pady=12)

        tips = [
            "💡 نور کافی داشته باش",
            "🖱️ موس با حرکت نسبی جابه‌جا می‌شود — پرش نمی‌کند",
            "🟢 دست راست = حرکت  |  🟠 دست چپ = کلیک",
            "⌨️  q = خروج  |  h = راهنما",
        ]
        for tip in tips:
            tk.Label(root, text=tip, font=("Segoe UI", 9),
                     fg="#666688", bg='#0a0a1a').pack(pady=2)

        tk.Button(root, text="بستن", command=root.destroy,
                  font=("Segoe UI", 10, "bold"), bg="#e94560",
                  fg="white", padx=40, pady=8, relief='flat',
                  activebackground="#c73652", cursor="hand2").pack(pady=18)

        root.mainloop()


class AirClick:
    def __init__(self):
        log_message("=" * 50)
        log_message("AirClick Pro Starting...")
        log_message("=" * 50)

        self.hand_tracker = HandTracker()
        self.gesture_recognizer = GestureRecognizer()
        self.mouse_controller = MouseController()

        self.frame_width = CAMERA_SETTINGS['frame_width']
        self.frame_height = CAMERA_SETTINGS['frame_height']
        self.show_fps = DISPLAY_SETTINGS['show_fps']
        self.show_landmarks = DISPLAY_SETTINGS['show_landmarks']
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
        self.right_hand_was_moving = False
        self.cursor_tip = None

        self.mouse_locked = False
        self.hand_was_detected = False

        self.cap = cv2.VideoCapture(CAMERA_SETTINGS['camera_id'])
        if not self.cap.isOpened():
            log_message("Camera not found!", "ERROR")
            sys.exit(1)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

        log_message(f"Camera: {self.frame_width}x{self.frame_height}")
        self.print_help()

    def print_help(self):
        print("\n" + "=" * 50)
        print("  AIRCLICK PRO - TWO HAND CONTROL")
        print("=" * 50)
        print("  RIGHT HAND (green):")
        print("     Index up only  ->  Move mouse (relative)")
        print("  LEFT HAND (orange):")
        print("     Index down     ->  Left click")
        print("     Middle down    ->  Right click")
        print("-" * 50)
        print("  q = Exit    h = Help")
        print("=" * 50 + "\n")

    def run(self):
        self.running = True

        cv2.namedWindow("AirClick", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("AirClick", 680, 540)
        cv2.setWindowProperty("AirClick", cv2.WND_PROP_TOPMOST, 1)

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            processed = self.process_frame(frame)
            processed = self.draw_overlay(processed)

            cv2.imshow("AirClick", processed)
            self.frame_count += 1

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break
            if key == ord('h'):
                import threading
                threading.Thread(target=HelpWindow.show, daemon=True).start()

        self.cleanup()

    def process_frame(self, frame):
        self.hand_tracker.process_frame(frame)

        self.left_hand_index = -1
        self.right_hand_index = -1
        self.cursor_tip = None

        for i in range(self.hand_tracker.get_hand_count()):
            hand_type = self.hand_tracker.get_hand_type(i)
            if hand_type == 'Left':
                self.left_hand_index = i
            elif hand_type == 'Right':
                self.right_hand_index = i

        any_hand = self.left_hand_index != -1 or self.right_hand_index != -1

        if self.right_hand_index != -1:
            self._process_right_hand(frame)
        else:
            self.right_hand_was_moving = False
            self.mouse_controller.pause_tracking()

        if self.left_hand_index != -1:
            self._process_left_hand(frame)

        if not any_hand:
            self._handle_no_hands(frame)
        else:
            self.hand_was_detected = True
            if self.mouse_locked:
                self.mouse_locked = False

        return frame

    def _process_right_hand(self, frame):
        live = self.hand_tracker.is_hand_live(self.right_hand_index)
        fingers = self.hand_tracker.get_fingers_status(self.right_hand_index)
        if not fingers:
            return

        self.current_gesture_right = self.gesture_recognizer.recognize(fingers)

        index_up = fingers[1]
        others_up = fingers[2:]
        is_moving = index_up and not any(others_up)

        if is_moving and live:
            h, w, _ = frame.shape
            tip = self.hand_tracker.get_index_tip((h, w, 3), self.right_hand_index, live_only=True)
            if tip:
                reanchor = not self.right_hand_was_moving
                self.mouse_controller.move(
                    tip[0], tip[1],
                    self.frame_width, self.frame_height,
                    reanchor=reanchor,
                )
                self.cursor_tip = tip
                self.mouse_mode = "MOVING"
        elif is_moving and not live:
            self.mouse_mode = "ANCHOR"
        else:
            self.mouse_controller.pause_tracking()
            if live:
                self.mouse_mode = "READY"

        self.right_hand_was_moving = is_moving and live

        box = self.hand_tracker.get_bounding_box(self.right_hand_index)
        if box:
            self._draw_hand_region(
                frame, box, COLORS['box_right'],
                "RIGHT", live,
                self.current_gesture_right,
            )
            if self.show_landmarks and live:
                self.hand_tracker.draw_landmarks(frame, COLORS['cursor_point'], self.right_hand_index)

        if self.cursor_tip:
            self._draw_crosshair(frame, self.cursor_tip, COLORS['cursor_point'])

    def _process_left_hand(self, frame):
        live = self.hand_tracker.is_hand_live(self.left_hand_index)
        fingers = self.hand_tracker.get_click_fingers_status(self.left_hand_index)
        if not fingers:
            return

        self.current_gesture_left = self.gesture_recognizer.recognize(fingers)
        current_time = time.time()

        if live:
            index_up, middle_up = fingers[1], fingers[2]
            cooldown_ok = current_time - self.last_click_time > self.click_cooldown

            left_gesture = not index_up and middle_up
            right_gesture = not middle_up and index_up

            if left_gesture and not self.left_click_active and cooldown_ok:
                if self.mouse_controller.click_left():
                    self.last_click_time = current_time
                    self.last_click_type = 'left'

            if right_gesture and not self.right_click_active and cooldown_ok:
                if self.mouse_controller.click_right():
                    self.last_click_time = current_time
                    self.last_click_type = 'right'

            self.left_click_active = left_gesture
            self.right_click_active = right_gesture
        else:
            self.left_click_active = False
            self.right_click_active = False

        box = self.hand_tracker.get_bounding_box(self.left_hand_index)
        if box:
            flash = current_time - self.last_click_time < 0.4
            if flash and self.last_click_type == 'left':
                color = COLORS['box_click']
                label = "LEFT CLICK"
            elif flash and self.last_click_type == 'right':
                color = (0, 165, 255)
                label = "RIGHT CLICK"
            else:
                color = COLORS['box_left']
                label = self.current_gesture_left

            self._draw_hand_region(frame, box, color, "LEFT", live, label)

            if self.show_landmarks and live:
                self.hand_tracker.draw_landmarks(frame, color, self.left_hand_index)

    def _handle_no_hands(self, frame):
        if self.hand_was_detected and not self.mouse_locked:
            self.mouse_locked = True
            log_message("Mouse locked (no hands)")

        self.mouse_controller.pause_tracking()
        self.left_click_active = False
        self.right_click_active = False
        self.right_hand_was_moving = False
        self.current_gesture_right = "WAITING"
        self.current_gesture_left = "WAITING"
        self.mouse_mode = "LOCKED"

    def _draw_hand_region(self, frame, box, color, hand_label, live, status):
        (x1, y1), (x2, y2) = box
        thickness = 2 if live else 1
        line_type = cv2.LINE_AA

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            cv2.rectangle(frame, (x1 + dx, y1 + dy), (x2 + dx, y2 + dy), (0, 0, 0), thickness + 1, line_type)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness, line_type)

        corner = 18
        for cx, cy, sx, sy in [
            (x1, y1, 1, 1), (x2, y1, -1, 1),
            (x1, y2, 1, -1), (x2, y2, -1, -1),
        ]:
            cv2.line(frame, (cx, cy), (cx + sx * corner, cy), color, 3, line_type)
            cv2.line(frame, (cx, cy), (cx, cy + sy * corner), color, 3, line_type)

        tag = f"{hand_label}" if live else f"{hand_label} (mem)"
        cv2.putText(frame, tag, (x1, max(y1 - 8, 14)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, line_type)
        cv2.putText(frame, status, (x1, y2 + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, line_type)

    def _draw_crosshair(self, frame, tip, color):
        x, y = tip
        size = 14
        cv2.line(frame, (x - size, y), (x + size, y), color, 1, cv2.LINE_AA)
        cv2.line(frame, (x, y - size), (x, y + size), color, 1, cv2.LINE_AA)
        cv2.circle(frame, (x, y), 6, color, 2, cv2.LINE_AA)
        cv2.circle(frame, (x, y), 2, (255, 255, 255), -1, cv2.LINE_AA)

    def draw_overlay(self, frame):
        h, w = frame.shape[:2]
        overlay = frame.copy()

        cv2.rectangle(overlay, (0, 0), (w, 42), (10, 10, 20), -1)
        cv2.rectangle(overlay, (0, h - 48), (w, h), (10, 10, 20), -1)
        frame = cv2.addWeighted(overlay, 0.75, frame, 0.25, 0)

        cv2.putText(frame, "AIRCLICK PRO", (14, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (233, 69, 96), 2, cv2.LINE_AA)

        if self.show_fps:
            fps = get_fps(self.start_time, self.frame_count)
            cv2.putText(frame, f"{fps:.0f} FPS", (w - 90, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(frame, "q:Exit  h:Help", (w - 130, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (120, 120, 140), 1, cv2.LINE_AA)

        mode_colors = {
            "MOVING": (81, 207, 102),
            "READY": (79, 195, 247),
            "ANCHOR": (255, 200, 100),
            "LOCKED": (100, 100, 120),
        }
        mode_color = mode_colors.get(self.mouse_mode, (150, 150, 150))
        cv2.putText(frame, f"Mode: {self.mouse_mode}", (14, h - 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, mode_color, 1, cv2.LINE_AA)

        right_text = f"R: {self.current_gesture_right}"
        left_text = f"L: {self.current_gesture_left}"
        cv2.putText(frame, right_text, (180, h - 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLORS['box_right'], 1, cv2.LINE_AA)
        cv2.putText(frame, left_text, (360, h - 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLORS['box_left'], 1, cv2.LINE_AA)

        if self.last_click_type and time.time() - self.last_click_time < 0.5:
            click_label = "LEFT CLICK" if self.last_click_type == 'left' else "RIGHT CLICK"
            click_color = COLORS['box_click'] if self.last_click_type == 'left' else (0, 165, 255)
            cv2.putText(frame, click_label, (w - 160, h - 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, click_color, 1, cv2.LINE_AA)

        if self.mouse_mode == "LOCKED" and self.hand_was_detected:
            cx, cy = w // 2, h // 2
            cv2.putText(frame, "NO HANDS", (cx - 70, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (80, 80, 200), 2, cv2.LINE_AA)
            cv2.putText(frame, "Mouse position preserved", (cx - 120, cy + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 140), 1, cv2.LINE_AA)

        return frame

    def cleanup(self):
        log_message("Cleaning up...")
        try:
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
