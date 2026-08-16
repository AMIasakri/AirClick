"""
ماژول کنترل موس - حرکت نسبی برای پایداری
"""

import pyautogui
import time
import sys
import os
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MOUSE_SETTINGS
from utils.helpers import log_message


class MouseController:
    """کنترل موس با حرکت نسبی و anchor برای جلوگیری از پرش"""

    def __init__(self):
        log_message("در حال راه‌اندازی MouseController...")

        self.action_cooldown = MOUSE_SETTINGS['action_cooldown']
        self.movement_speed = MOUSE_SETTINGS['movement_speed']
        self.dead_zone = MOUSE_SETTINGS['dead_zone']
        self.smoothing = MOUSE_SETTINGS['smoothing_factor']
        self.relative_mode = MOUSE_SETTINGS.get('relative_mode', True)

        self.screen_width, self.screen_height = pyautogui.size()
        self.current_x = self.screen_width // 2
        self.current_y = self.screen_height // 2

        self.position_history = deque(maxlen=5)
        self.smooth_x = float(self.current_x)
        self.smooth_y = float(self.current_y)

        self.last_tip_x = None
        self.last_tip_y = None
        self.tracking_active = False

        self.last_action_time = 0

        log_message(f"📺 Screen: {self.screen_width}x{self.screen_height}")
        pyautogui.FAILSAFE = False
        pyautogui.MINIMUM_DURATION = 0.01
        log_message("✅ MouseController ready (relative mode)")

    def move(self, tip_x, tip_y, frame_width, frame_height, reanchor=False):
        """حرکت موس - نسبی یا مطلق"""
        if self.relative_mode:
            return self._move_relative(tip_x, tip_y, frame_width, frame_height, reanchor)
        return self._move_absolute(tip_x, tip_y, frame_width, frame_height)

    def _move_relative(self, tip_x, tip_y, frame_width, frame_height, reanchor=False):
        if reanchor or not self.tracking_active:
            self.last_tip_x = tip_x
            self.last_tip_y = tip_y
            self.tracking_active = True
            return self.current_x, self.current_y

        dx = tip_x - self.last_tip_x
        dy = tip_y - self.last_tip_y
        self.last_tip_x = tip_x
        self.last_tip_y = tip_y

        if abs(dx) < self.dead_zone and abs(dy) < self.dead_zone:
            return self.current_x, self.current_y

        scale_x = (self.screen_width / frame_width) * self.movement_speed
        scale_y = (self.screen_height / frame_height) * self.movement_speed

        target_x = self.smooth_x + dx * scale_x
        target_y = self.smooth_y + dy * scale_y

        target_x = max(0, min(self.screen_width - 1, target_x))
        target_y = max(0, min(self.screen_height - 1, target_y))

        self.smooth_x = self.smooth_x * (1 - self.smoothing) + target_x * self.smoothing
        self.smooth_y = self.smooth_y * (1 - self.smoothing) + target_y * self.smoothing

        self.current_x = int(self.smooth_x)
        self.current_y = int(self.smooth_y)

        pyautogui.moveTo(self.current_x, self.current_y, duration=0)
        return self.current_x, self.current_y

    def _move_absolute(self, tip_x, tip_y, frame_width, frame_height):
        target_x = int(tip_x * self.screen_width / frame_width)
        target_y = int(tip_y * self.screen_height / frame_height)

        target_x = max(0, min(self.screen_width - 1, target_x))
        target_y = max(0, min(self.screen_height - 1, target_y))

        self.position_history.append((target_x, target_y))

        if len(self.position_history) >= 3:
            positions = list(self.position_history)
            avg_x = sum(p[0] for p in positions) / len(positions)
            avg_y = sum(p[1] for p in positions) / len(positions)
            filtered = [
                (px, py) for px, py in positions
                if abs(px - avg_x) < 100 and abs(py - avg_y) < 100
            ]
            if filtered:
                target_x = int(sum(p[0] for p in filtered) / len(filtered))
                target_y = int(sum(p[1] for p in filtered) / len(filtered))

        self.smooth_x = self.smooth_x * (1 - self.smoothing) + target_x * self.smoothing
        self.smooth_y = self.smooth_y * (1 - self.smoothing) + target_y * self.smoothing

        self.current_x = int(self.smooth_x)
        self.current_y = int(self.smooth_y)

        pyautogui.moveTo(self.current_x, self.current_y, duration=0.01)
        return self.current_x, self.current_y

    def click_left(self):
        if self._can_act():
            pyautogui.click(button='left')
            self.last_action_time = time.time()
            log_message("LEFT CLICK")
            return True
        return False

    def click_right(self):
        if self._can_act():
            pyautogui.click(button='right')
            self.last_action_time = time.time()
            log_message("RIGHT CLICK")
            return True
        return False

    def click_middle(self):
        if self._can_act():
            pyautogui.middleClick()
            self.last_action_time = time.time()
            log_message("🖱️ MIDDLE CLICK")
            return True
        return False

    def get_position(self):
        return self.current_x, self.current_y

    def _can_act(self):
        return time.time() - self.last_action_time >= self.action_cooldown

    def pause_tracking(self):
        """توقف ردیابی بدون تغییر موقعیت موس - برای بازگشت دست"""
        self.tracking_active = False
        self.last_tip_x = None
        self.last_tip_y = None

    def reset(self):
        self.pause_tracking()
        self.position_history.clear()
