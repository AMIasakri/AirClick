"""
رندر UI حرفه‌ای برای AirClick
"""

import cv2
import numpy as np
import time
import math

from config.settings import COLORS


class OverlayRenderer:
    """رسم overlay، HUD، و افکت‌های بصری"""

    def __init__(self):
        self.pulse_phase = 0.0
        self.click_ripples = []
        self.flash_until = 0.0
        self.flash_label = ""
        self.flash_color = COLORS['box_click']

    def tick(self):
        self.pulse_phase = (self.pulse_phase + 0.12) % (2 * math.pi)

    def trigger_click_flash(self, label, color):
        self.flash_until = time.time() + 0.55
        self.flash_label = label
        self.flash_color = color

    def add_ripple(self, x, y, color):
        self.click_ripples.append({'x': x, 'y': y, 'r': 8, 'color': color, 'alpha': 1.0})

    def draw_vignette(self, frame, strength=0.35):
        h, w = frame.shape[:2]
        y, x = np.ogrid[:h, :w]
        cx, cy = w / 2, h / 2
        mask = np.sqrt(((x - cx) / cx) ** 2 + ((y - cy) / cy) ** 2)
        mask = np.clip(mask ** 1.6, 0, 1)
        mask = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 30)
        dark = (frame.astype(np.float32) * (1 - mask[:, :, None] * strength)).astype(np.uint8)
        return dark

    def draw_panel(self, frame, x1, y1, x2, y2, alpha=0.82, border_color=None):
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), COLORS['panel_bg'], -1)
        if border_color:
            cv2.rectangle(overlay, (x1, y1), (x2, y2), border_color, 1, cv2.LINE_AA)
        return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    def draw_pill(self, frame, text, x, y, color, scale=0.42):
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)
        pad_x, pad_y = 10, 5
        x1, y1 = x, y - th - pad_y
        x2, y2 = x + tw + pad_x * 2, y + pad_y
        sub = frame.copy()
        cv2.rectangle(sub, (x1, y1), (x2, y2), color, -1, cv2.LINE_AA)
        cv2.addWeighted(sub, 0.25, frame, 0.75, 0, frame)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1, cv2.LINE_AA)
        cv2.putText(frame, text, (x + pad_x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, COLORS['text_primary'], 1, cv2.LINE_AA)

    def draw_hand_box(self, frame, box, color, hand_label, status, live=True):
        (x1, y1), (x2, y2) = box
        pulse = 0.5 + 0.5 * math.sin(self.pulse_phase)
        thickness = 2 if live else 1
        glow = tuple(int(c * (0.7 + 0.3 * pulse)) for c in color) if live else color

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            cv2.rectangle(frame, (x1 + dx, y1 + dy), (x2 + dx, y2 + dy),
                          (0, 0, 0), thickness + 1, cv2.LINE_AA)

        cv2.rectangle(frame, (x1, y1), (x2, y2), glow, thickness, cv2.LINE_AA)

        corner = 22
        for cx, cy, sx, sy in [
            (x1, y1, 1, 1), (x2, y1, -1, 1),
            (x1, y2, 1, -1), (x2, y2, -1, -1),
        ]:
            cv2.line(frame, (cx, cy), (cx + sx * corner, cy), color, 3, cv2.LINE_AA)
            cv2.line(frame, (cx, cy), (cx, cy + sy * corner), color, 3, cv2.LINE_AA)

        tag = hand_label if live else f"{hand_label} (mem)"
        cv2.putText(frame, tag, (x1, max(y1 - 10, 16)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, color, 1, cv2.LINE_AA)
        cv2.putText(frame, status, (x1, y2 + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, glow, 1, cv2.LINE_AA)

    def draw_crosshair(self, frame, tip, color):
        x, y = tip
        size = 16
        cv2.line(frame, (x - size, y), (x + size, y), (0, 0, 0), 3, cv2.LINE_AA)
        cv2.line(frame, (x, y - size), (x, y + size), (0, 0, 0), 3, cv2.LINE_AA)
        cv2.line(frame, (x - size, y), (x + size, y), color, 1, cv2.LINE_AA)
        cv2.line(frame, (x, y - size), (x, y + size), color, 1, cv2.LINE_AA)
        cv2.circle(frame, (x, y), 7, color, 2, cv2.LINE_AA)
        cv2.circle(frame, (x, y), 2, (255, 255, 255), -1, cv2.LINE_AA)

    def draw_landmarks_glow(self, frame, landmarks, color):
        if not landmarks:
            return frame
        h, w, _ = frame.shape
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17),
        ]
        for i, j in connections:
            x1, y1 = int(landmarks[i].x * w), int(landmarks[i].y * h)
            x2, y2 = int(landmarks[j].x * w), int(landmarks[j].y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 0), 3, cv2.LINE_AA)
            cv2.line(frame, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

        for idx, lm in enumerate(landmarks):
            cx, cy = int(lm.x * w), int(lm.y * h)
            r = 7 if idx in (4, 8, 12, 16, 20) else 4
            cv2.circle(frame, (cx, cy), r + 2, (0, 0, 0), -1, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), r, color, -1, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), r, (255, 255, 255), 1, cv2.LINE_AA)
        return frame

    def draw_zones(self, frame, split_x, top_bar, bottom_bar):
        h, w = frame.shape[:2]
        zone = frame.copy()
        cv2.rectangle(zone, (0, top_bar), (split_x, h - bottom_bar), (40, 80, 40), -1)
        cv2.rectangle(zone, (split_x, top_bar), (w, h - bottom_bar), (80, 50, 30), -1)
        frame[:] = cv2.addWeighted(zone, 0.10, frame, 0.90, 0)

        for y in range(top_bar, h - bottom_bar, 14):
            cv2.line(frame, (split_x, y), (split_x, min(y + 7, h - bottom_bar)),
                     (180, 180, 210), 1, cv2.LINE_AA)

        cv2.putText(frame, "MOUSE / DRAG", (split_x // 2 - 55, top_bar + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLORS['box_right'], 1, cv2.LINE_AA)
        cv2.putText(frame, "CLICK / SCROLL", (split_x + split_x // 2 - 55, top_bar + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLORS['box_left'], 1, cv2.LINE_AA)

    def draw_header(self, frame, fps=None):
        h, w = frame.shape[:2]
        frame = self.draw_panel(frame, 0, 0, w, 52, alpha=0.78, border_color=COLORS['panel_border'])

        cv2.putText(frame, "AIRCLICK PRO", (18, 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.78, COLORS['accent'], 2, cv2.LINE_AA)

        cv2.line(frame, (200, 14), (200, 38), COLORS['panel_border'], 1, cv2.LINE_AA)
        cv2.putText(frame, "Hand Control System", (212, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLORS['text_muted'], 1, cv2.LINE_AA)

        if fps is not None:
            self.draw_pill(frame, f"{fps:.0f} FPS", w - 110, 32, COLORS['success'])

        cv2.putText(frame, "q:Exit  h:Help  d:Debug", (w - 210, 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, COLORS['text_muted'], 1, cv2.LINE_AA)
        return frame

    def draw_footer(self, frame, mode, mode_color, right_gesture, left_gesture,
                    hand_separation=None, hands_too_close=False):
        h, w = frame.shape[:2]
        frame = self.draw_panel(frame, 0, h - 56, w, h, alpha=0.78, border_color=COLORS['panel_border'])

        self.draw_pill(frame, f"Mode: {mode}", 14, h - 18, mode_color, scale=0.44)
        self.draw_pill(frame, f"R: {right_gesture}", 170, h - 18, COLORS['box_right'], scale=0.40)
        self.draw_pill(frame, f"L: {left_gesture}", 360, h - 18, COLORS['box_left'], scale=0.40)

        if hand_separation is not None:
            sep_color = COLORS['danger'] if hands_too_close else COLORS['text_muted']
            cv2.putText(frame, f"Gap: {int(hand_separation)}px", (w // 2 - 45, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, sep_color, 1, cv2.LINE_AA)

        if time.time() < self.flash_until:
            cv2.putText(frame, self.flash_label, (w - 200, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, self.flash_color, 2, cv2.LINE_AA)

        return frame

    def draw_gesture_hud(self, frame):
        h, w = frame.shape[:2]
        panel_w = 210
        x1, y1, x2, y2 = w - panel_w - 12, 62, w - 12, 290
        frame = self.draw_panel(frame, x1, y1, x2, y2, alpha=0.72, border_color=COLORS['accent'])

        cv2.putText(frame, "GESTURES", (x1 + 12, y1 + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, COLORS['accent_light'], 1, cv2.LINE_AA)

        items = [
            ("R: Index up", "Move", COLORS['box_right']),
            ("R: V sign", "Drag", COLORS['box_drag']),
            ("L: Index down", "Left click", COLORS['box_click']),
            ("L: Middle down", "Right click", COLORS['warning']),
            ("L: Fist", "Middle click", COLORS['text_muted']),
            ("L: Index+Mid down", "Double click", COLORS['accent_light']),
            ("L: Ring down", "Scroll", COLORS['box_scroll']),
        ]
        y = y1 + 44
        for label, action, color in items:
            cv2.circle(frame, (x1 + 18, y - 5), 4, color, -1, cv2.LINE_AA)
            cv2.putText(frame, label, (x1 + 28, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, COLORS['text_primary'], 1, cv2.LINE_AA)
            cv2.putText(frame, action, (x1 + 28, y + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.32, color, 1, cv2.LINE_AA)
            y += 30
        return frame

    def draw_debug_panel(self, frame, debug_info):
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = 12, 62, 280, 62 + len(debug_info) * 18 + 24
        frame = self.draw_panel(frame, x1, y1, x2, y2, alpha=0.75, border_color=COLORS['warning'])
        cv2.putText(frame, "DEBUG", (x1 + 10, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, COLORS['warning'], 1, cv2.LINE_AA)
        y = y1 + 40
        for line in debug_info:
            cv2.putText(frame, line, (x1 + 10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, COLORS['text_primary'], 1, cv2.LINE_AA)
            y += 18
        return frame

    def draw_center_message(self, frame, text, color):
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        sub = frame.copy()
        cv2.rectangle(sub, (cx - tw // 2 - 20, cy - th - 16),
                      (cx + tw // 2 + 20, cy + 16), COLORS['panel_bg'], -1)
        frame[:] = cv2.addWeighted(sub, 0.6, frame, 0.4, 0)
        cv2.putText(frame, text, (cx - tw // 2, cy + th // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2, cv2.LINE_AA)

    def draw_warning_banner(self, frame, text):
        h, w = frame.shape[:2]
        sub = frame.copy()
        cv2.rectangle(sub, (w // 2 - 180, 58), (w // 2 + 180, 88), (0, 60, 200), -1)
        frame[:] = cv2.addWeighted(sub, 0.55, frame, 0.45, 0)
        cv2.putText(frame, text, (w // 2 - 170, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)

    def update_ripples(self, frame):
        alive = []
        for ripple in self.click_ripples:
            ripple['r'] += 3
            ripple['alpha'] -= 0.06
            if ripple['alpha'] > 0:
                color = ripple['color']
                cv2.circle(frame, (ripple['x'], ripple['y']), ripple['r'],
                           color, 2, cv2.LINE_AA)
                alive.append(ripple)
        self.click_ripples = alive

    def render(self, frame, state):
        self.tick()
        frame = self.draw_vignette(frame, strength=0.22)

        h, w = frame.shape[:2]
        split_x = w // 2
        self.draw_zones(frame, split_x, 52, 56)

        if state.get('right_box'):
            self.draw_hand_box(
                frame, state['right_box'], state.get('right_color', COLORS['box_right']),
                "MOUSE", state.get('right_gesture', ''), state.get('right_live', False),
            )
        if state.get('left_box'):
            self.draw_hand_box(
                frame, state['left_box'], state.get('left_color', COLORS['box_left']),
                "CLICK", state.get('left_gesture', ''), state.get('left_live', False),
            )

        if state.get('cursor_tip'):
            self.draw_crosshair(frame, state['cursor_tip'], COLORS['cursor_point'])

        if state.get('right_landmarks') and state.get('show_landmarks'):
            self.draw_landmarks_glow(frame, state['right_landmarks'], COLORS['box_right'])
        if state.get('left_landmarks') and state.get('show_landmarks'):
            self.draw_landmarks_glow(frame, state['left_landmarks'], COLORS['box_left'])

        self.update_ripples(frame)

        fps = state.get('fps')
        frame = self.draw_header(frame, fps=fps if state.get('show_fps') else None)

        mode_colors = {
            "MOVING": COLORS['success'],
            "DRAGGING": COLORS['box_drag'],
            "READY": COLORS['box_left'],
            "ANCHOR": COLORS['warning'],
            "SCROLLING": COLORS['box_scroll'],
            "LOCKED": COLORS['text_muted'],
        }
        mode = state.get('mode', 'LOCKED')
        frame = self.draw_footer(
            frame, mode, mode_colors.get(mode, COLORS['text_muted']),
            state.get('right_gesture', 'WAITING'),
            state.get('left_gesture', 'WAITING'),
            state.get('hand_separation'),
            state.get('hands_too_close', False),
        )

        frame = self.draw_gesture_hud(frame)

        if state.get('show_debug') and state.get('debug_info'):
            frame = self.draw_debug_panel(frame, state['debug_info'])

        if mode == "LOCKED" and state.get('hand_was_detected'):
            self.draw_center_message(frame, "NO HANDS", COLORS['danger'])

        if state.get('hands_too_close'):
            self.draw_warning_banner(frame, "Hands too close - spread apart!")

        return frame
