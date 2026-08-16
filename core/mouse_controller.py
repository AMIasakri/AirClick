"""
ماژول کنترل موس - حرکت نسبی، drag، scroll
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
    """کنترل موس با حرکت نسبی و پشتیبانی از drag/scroll"""

    def __init__(self):
        log_message("در حال راه‌اندازی MouseController...")

        self.action_cooldown = MOUSE_SETTINGS['action_cooldown']
        self.movement_speed = MOUSE_SETTINGS['movement_speed']
        self.dead_zone = MOUSE_SETTINGS['dead_zone']
        self.smoothing = MOUSE_SETTINGS['smoothing_factor']
        self.relative_mode = MOUSE_SETTINGS.get('relative_mode', True)
        self.scroll_speed = MOUSE_SETTINGS.get('scroll_speed', 3)
        self.scroll_dead_zone = MOUSE_SETTINGS.get('scroll_dead_zone', 8)
        self.double_click_interval = MOUSE_SETTINGS.get('double_click_interval', 0.35)

        self.screen_width, self.screen_height = pyautogui.size()
        self.current_x = self.screen_width // 2
        self.current_y = self.screen_height // 2

        self.position_history = deque(maxlen=5)
        self.smooth_x = float(self.current_x)
        self.smooth_y = float(self.current_y)

        self.last_tip_x = None
        self.last_tip_y = None
        self.tracking_active = False
        self.drag_active = False
        self.drag_button = 'left'

        self.last_scroll_y = None
        self.scroll_active = False

        self.last_action_time = 0
        self.last_click_time = 0
        self.pending_single_click = False

        pyautogui.FAILSAFE = False
        pyautogui.MINIMUM_DURATION = 0.01
        log_message(f"Screen: {self.screen_width}x{self.screen_height}")
        log_message("MouseController ready")

    def move(self, tip_x, tip_y, frame_width, frame_height, reanchor=False):
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

    def start_drag(self, button='left'):
        if not self.drag_active and self._can_act():
            pyautogui.mouseDown(button=button)
            self.drag_active = True
            self.drag_button = button
            self.last_action_time = time.time()
            log_message(f"DRAG START ({button})")
            return True
        return False

    def stop_drag(self):
        if self.drag_active:
            pyautogui.mouseUp(button=self.drag_button)
            log_message("DRAG END")
            self.drag_active = False
            self.last_action_time = time.time()
            return True
        return False

    def scroll(self, hand_y, reanchor=False):
        if reanchor or not self.scroll_active:
            self.last_scroll_y = hand_y
            self.scroll_active = True
            return 0

        dy = hand_y - self.last_scroll_y
        self.last_scroll_y = hand_y

        if abs(dy) < self.scroll_dead_zone:
            return 0

        clicks = int(dy / self.scroll_dead_zone) * self.scroll_speed
        if clicks != 0:
            pyautogui.scroll(-clicks)
            log_message(f"SCROLL {clicks}")
        return clicks

    def stop_scroll(self):
        self.scroll_active = False
        self.last_scroll_y = None

    def click_left(self):
        pyautogui.click(button='left')
        self.last_action_time = time.time()
        self.last_click_time = time.time()
        log_message("LEFT CLICK")
        return True

    def click_right(self):
        pyautogui.click(button='right')
        self.last_action_time = time.time()
        self.last_click_time = time.time()
        log_message("RIGHT CLICK")
        return True

    def click_middle(self):
        pyautogui.middleClick()
        self.last_action_time = time.time()
        self.last_click_time = time.time()
        log_message("MIDDLE CLICK")
        return True

    def click_double(self):
        pyautogui.doubleClick()
        self.last_action_time = time.time()
        self.last_click_time = time.time()
        log_message("DOUBLE CLICK")
        return True

    def get_position(self):
        return self.current_x, self.current_y

    def _can_act(self):
        return time.time() - self.last_action_time >= self.action_cooldown

    def pause_tracking(self):
        if self.drag_active:
            self.stop_drag()
        self.tracking_active = False
        self.last_tip_x = None
        self.last_tip_y = None

    def reset(self):
        self.pause_tracking()
        self.stop_scroll()
        self.position_history.clear()
