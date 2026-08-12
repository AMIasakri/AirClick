"""
ماژول تشخیص حرکات دست
تشخیص حرکات مختلف بر اساس وضعیت انگشتان
"""

import sys
import os

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import GESTURE_SETTINGS
from utils.helpers import log_message


class GestureRecognizer:
    """
    کلاس تشخیص حرکات دست
    تشخیص حرکت بر اساس وضعیت ۵ انگشت
    """
    
    def __init__(self):
        """راه‌اندازی اولیه"""
        log_message("در حال راه‌اندازی GestureRecognizer...")
        self.gesture_names = GESTURE_SETTINGS['gesture_names']
        self.last_gesture = None
        self.gesture_count = 0
        log_message("✅ GestureRecognizer راه‌اندازی شد")
    
    def recognize(self, fingers):
        """
        تشخیص حرکت بر اساس وضعیت انگشتان
        
        Args:
            fingers: لیست ۵ عضوی [شست, اشاره, وسط, حلقه, کوچک]
                    True = بالا, False = پایین
        
        Returns:
            str: نام حرکت تشخیص داده شده
        """
        if not fingers or len(fingers) != 5:
            return self.gesture_names['unknown']
        
        thumb, index, middle, ring, pinky = fingers
        
        # 1. حالت آماده: همه انگشتان باز
        if all(fingers):
            return self.gesture_names['all_open']
        
        # 2. حرکت موس: فقط انگشت اشاره بالا
        if index and not middle and not ring and not pinky:
            return self.gesture_names['only_index']
        
        # 3. کلیک چپ: اشاره خم + وسط صاف (حرکت مورد نظر تو)
        # اشاره خم = False, وسط صاف = True
        if not index and middle and not ring and not pinky:
            return self.gesture_names['index_folded_middle_open']
        
        # 4. کلیک راست: اشاره و وسط بالا
        if index and middle and not ring and not pinky:
            return self.gesture_names['index_middle_open']
        
        # 5. کلیک وسط: مشت (همه بسته)
        if not any(fingers):
            return self.gesture_names['fist']
        
        # 6. حالت ناشناخته
        return self.gesture_names['unknown']
    
    def get_gesture_name(self, gesture_key):
        """
        دریافت نام نمایشی حرکت
        
        Args:
            gesture_key: کلید حرکت
        
        Returns:
            str: نام نمایشی
        """
        return self.gesture_names.get(gesture_key, self.gesture_names['unknown'])
    
    def is_moving(self, gesture):
        """بررسی اینکه آیا حرکت موس است"""
        return gesture == self.gesture_names['only_index']
    
    def is_left_click(self, gesture):
        """بررسی اینکه آیا کلیک چپ است"""
        return gesture == self.gesture_names['index_folded_middle_open']
    
    def is_right_click(self, gesture):
        """بررسی اینکه آیا کلیک راست است"""
        return gesture == self.gesture_names['index_middle_open']
    
    def is_middle_click(self, gesture):
        """بررسی اینکه آیا کلیک وسط است"""
        return gesture == self.gesture_names['fist']
    
    def is_ready(self, gesture):
        """بررسی اینکه آیا در حالت آماده است"""
        return gesture == self.gesture_names['all_open']
    
    def reset(self):
        """بازنشانی وضعیت"""
        self.last_gesture = None
        self.gesture_count = 0


# ==================== تست سریع ====================
if __name__ == "__main__":
    print("🧪 GestureRecognizer Test...")
    
    recognizer = GestureRecognizer()
    
    # تست با حالت‌های مختلف
    test_cases = [
        ([True, True, True, True, True], "All Open - Ready"),
        ([False, True, False, False, False], "Only Index - Moving"),
        ([False, False, True, False, False], "Index Folded + Middle Open - Left Click"),
        ([False, True, True, False, False], "Index + Middle - Right Click"),
        ([False, False, False, False, False], "Fist - Middle Click"),
        ([True, False, True, False, True], "Unknown")
    ]
    
    print("\n📋 Testing gestures:")
    print("-" * 50)
    
    for fingers, description in test_cases:
        gesture = recognizer.recognize(fingers)
        print(f"  Fingers: {fingers}")
        print(f"  → {description}: {gesture}")
        print("-" * 50)
    
    print("\n✅ Test finished")