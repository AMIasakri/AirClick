"""
ماژول کنترل موس
مدیریت حرکت و کلیک‌های موس با استفاده از PyAutoGUI
"""

import pyautogui
import time
import sys
import os

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MOUSE_SETTINGS
from utils.helpers import log_message
from utils.filters import ExponentialMovingAverage


class MouseController:
    """
    کلاس کنترل موس
    مدیریت حرکت، کلیک‌ها و نرم‌سازی حرکات
    """
    
    def __init__(self):
        """راه‌اندازی اولیه"""
        log_message("در حال راه‌اندازی MouseController...")
        
        # تنظیمات
        self.smoothing_factor = MOUSE_SETTINGS['smoothing_factor']
        self.action_cooldown = MOUSE_SETTINGS['action_cooldown']
        
        # فیلترهای نرم‌سازی
        self.smooth_x = ExponentialMovingAverage(self.smoothing_factor)
        self.smooth_y = ExponentialMovingAverage(self.smoothing_factor)
        
        # زمان آخرین عمل
        self.last_action_time = 0
        
        # اندازه صفحه
        self.screen_width, self.screen_height = pyautogui.size()
        log_message(f"📺 Screen size: {self.screen_width}x{self.screen_height}")
        
        # غیرفعال کردن Failsafe برای حرکت روان‌تر
        pyautogui.FAILSAFE = False
        
        log_message("✅ MouseController راه‌اندازی شد")
    
    def move(self, x, y, frame_width, frame_height):
        """
        حرکت موس به مختصات مشخص
        
        Args:
            x, y: مختصات در تصویر (0 تا 640, 0 تا 480)
            frame_width, frame_height: ابعاد تصویر
        """
        # مقیاس‌سازی به صفحه نمایش
        screen_x = int(x * self.screen_width / frame_width)
        screen_y = int(y * self.screen_height / frame_height)
        
        # محدود کردن به صفحه
        screen_x = max(0, min(self.screen_width - 1, screen_x))
        screen_y = max(0, min(self.screen_height - 1, screen_y))
        
        # اعمال فیلتر نرم‌سازی
        smooth_x = self.smooth_x.update(screen_x)
        smooth_y = self.smooth_y.update(screen_y)
        
        # حرکت موس
        pyautogui.moveTo(smooth_x, smooth_y)
        
        return smooth_x, smooth_y
    
    def click_left(self):
        """کلیک چپ"""
        if self._can_act():
            pyautogui.click()
            self.last_action_time = time.time()
            log_message("🖱️ Left Click")
            return True
        return False
    
    def click_right(self):
        """کلیک راست"""
        if self._can_act():
            pyautogui.rightClick()
            self.last_action_time = time.time()
            log_message("🖱️ Right Click")
            return True
        return False
    
    def click_middle(self):
        """کلیک وسط"""
        if self._can_act():
            pyautogui.middleClick()
            self.last_action_time = time.time()
            log_message("🖱️ Middle Click")
            return True
        return False
    
    def double_click(self):
        """دوبار کلیک"""
        if self._can_act():
            pyautogui.doubleClick()
            self.last_action_time = time.time()
            log_message("🖱️ Double Click")
            return True
        return False
    
    def scroll(self, amount):
        """
        اسکرول
        
        Args:
            amount: مقدار اسکرول (مثبت = بالا، منفی = پایین)
        """
        pyautogui.scroll(amount)
    
    def _can_act(self):
        """
        بررسی اینکه آیا می‌توان عمل کرد (جلوگیری از کلیک چندباره)
        
        Returns:
            bool: True اگر می‌توان عمل کرد
        """
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            return True
        return False
    
    def reset(self):
        """بازنشانی فیلترها"""
        self.smooth_x.reset()
        self.smooth_y.reset()
        self.last_action_time = 0


# ==================== تست سریع ====================
if __name__ == "__main__":
    print("🧪 MouseController Test...")
    
    controller = MouseController()
    
    print("\n📋 Testing mouse control:")
    print("-" * 50)
    print("⏳ Moving mouse to center of screen...")
    
    # حرکت موس به مرکز صفحه
    controller.move(
        controller.screen_width // 2,
        controller.screen_height // 2,
        controller.screen_width,
        controller.screen_height
    )
    
    time.sleep(1)
    
    print("🖱️ Testing clicks (wait 2 seconds between clicks)...")
    
    # تست کلیک‌ها
    time.sleep(1)
    print("  → Left Click")
    controller.click_left()
    
    time.sleep(2)
    print("  → Right Click")
    controller.click_right()
    
    time.sleep(2)
    print("  → Middle Click")
    controller.click_middle()
    
    print("\n✅ Test finished")