"""
ماژول تشخیص حرکات دست
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import GESTURE_SETTINGS
from utils.helpers import log_message


class GestureRecognizer:
    """کلاس تشخیص حرکات دست"""
    
    def __init__(self):
        log_message("در حال راه‌اندازی GestureRecognizer...")
        self.gesture_names = GESTURE_SETTINGS['gesture_names']
        log_message("✅ GestureRecognizer راه‌اندازی شد")
    
    def recognize(self, fingers):
        if not fingers or len(fingers) != 5:
            return self.gesture_names['unknown']
        
        thumb, index, middle, ring, pinky = fingers
        
        # همه باز - آماده
        if all(fingers):
            return self.gesture_names['all_open']
        
        # فقط اشاره - حرکت
        if index and not middle and not ring and not pinky:
            return self.gesture_names['only_index']
        
        # اشاره خم + بقیه بالا - کلیک چپ
        if not index and middle and not ring and not pinky:
            return self.gesture_names['index_folded_middle_open']
        
        # وسط خم + اشاره بالا - کلیک راست
        if index and not middle:
            return self.gesture_names['middle_folded_index_open']
        
        # مشت - کلیک وسط
        if not any(fingers):
            return self.gesture_names['fist']
        
        return self.gesture_names['unknown']
    
    def is_moving(self, gesture):
        return gesture == self.gesture_names['only_index']
    
    def is_left_click(self, gesture):
        return gesture == self.gesture_names['index_folded_middle_open']
    
    def is_right_click(self, gesture):
        return gesture in (
            self.gesture_names['middle_folded_index_open'],
            self.gesture_names['index_middle_open'],
        )
    
    def is_middle_click(self, gesture):
        return gesture == self.gesture_names['fist']
    
    def is_ready(self, gesture):
        return gesture == self.gesture_names['all_open']