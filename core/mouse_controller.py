"""
ماژول کنترل موس
"""

import pyautogui
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import log_message


class MouseController:
    """کلاس کنترل موس"""
    
    def __init__(self):
        log_message("در حال راه‌اندازی MouseController...")
        
        self.action_cooldown = 0.3
        self.smooth_factor = 0.7
        
        self.last_action_time = 0
        self.screen_width, self.screen_height = pyautogui.size()
        self.current_x = self.screen_width // 2
        self.current_y = self.screen_height // 2
        
        # فیلتر نرم‌سازی
        self.smooth_x = self.current_x
        self.smooth_y = self.current_y
        
        # وضعیت کلیک
        self.is_pressed = False
        
        log_message(f"📺 Screen: {self.screen_width}x{self.screen_height}")
        pyautogui.FAILSAFE = False
        pyautogui.MINIMUM_DURATION = 0.02
        log_message("✅ MouseController ready")
    
    def move(self, x, y, frame_width, frame_height):
        target_x = int(x * self.screen_width / frame_width)
        target_y = int(y * self.screen_height / frame_height)
        
        target_x = max(0, min(self.screen_width - 1, target_x))
        target_y = max(0, min(self.screen_height - 1, target_y))
        
        # فیلتر نرم‌سازی
        self.smooth_x = int(self.smooth_x * 0.3 + target_x * 0.7)
        self.smooth_y = int(self.smooth_y * 0.3 + target_y * 0.7)
        
        self.current_x = self.smooth_x
        self.current_y = self.smooth_y
        
        pyautogui.moveTo(self.current_x, self.current_y, duration=0.01)
        return self.current_x, self.current_y
    
    def click_down(self):
        if not self.is_pressed:
            pyautogui.mouseDown()
            self.is_pressed = True
            log_message("🖱️ Mouse DOWN")
            return True
        return False
    
    def click_up(self):
        if self.is_pressed:
            pyautogui.mouseUp()
            self.is_pressed = False
            log_message("🖱️ Mouse UP")
            return True
        return False
    
    def click_left(self):
        if self._can_act():
            pyautogui.click()
            self.last_action_time = time.time()
            log_message("🖱️ Left Click")
            return True
        return False
    
    def click_right(self):
        if self._can_act():
            pyautogui.rightClick()
            self.last_action_time = time.time()
            log_message("🖱️ Right Click")
            return True
        return False
    
    def click_middle(self):
        if self._can_act():
            pyautogui.middleClick()
            self.last_action_time = time.time()
            log_message("🖱️ Middle Click")
            return True
        return False
    
    def get_position(self):
        return self.current_x, self.current_y
    
    def _can_act(self):
        return time.time() - self.last_action_time >= self.action_cooldown
    
    def reset(self):
        self.smooth_x = self.current_x
        self.smooth_y = self.current_y
        if self.is_pressed:
            pyautogui.mouseUp()
            self.is_pressed = False