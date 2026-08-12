"""
توابع کمکی عمومی برای پروژه AirClick
شامل توابع محاسباتی، تبدیلات و عملیات عمومی
"""

import math
import cv2
import numpy as np
from datetime import datetime


def calculate_distance(point1, point2):
    """
    محاسبه‌ی فاصله‌ی اقلیدسی بین دو نقطه
    
    Args:
        point1: tuple (x1, y1)
        point2: tuple (x2, y2)
    
    Returns:
        float: فاصله بین دو نقطه
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def get_bounding_box(landmarks, w, h, padding=20):
    """
    محاسبه‌ی کادر دور دست با استفاده از تمام نقاط
    
    Args:
        landmarks: لیست نقاط کلیدی دست از MediaPipe
        w: عرض تصویر
        h: ارتفاع تصویر
        padding: فاصله‌ی اضافی دور کادر (پیکسل)
    
    Returns:
        tuple: (x1, y1), (x2, y2) گوشه‌های کادر
    """
    x_coords = [lm.x for lm in landmarks]
    y_coords = [lm.y for lm in landmarks]
    
    x_min = int(min(x_coords) * w) - padding
    x_max = int(max(x_coords) * w) + padding
    y_min = int(min(y_coords) * h) - padding
    y_max = int(max(y_coords) * h) + padding
    
    # محدود کردن به ابعاد تصویر
    x_min = max(0, x_min)
    x_max = min(w, x_max)
    y_min = max(0, y_min)
    y_max = min(h, y_max)
    
    return (x_min, y_min), (x_max, y_max)


def scale_coordinates(x, y, src_width, src_height, dst_width, dst_height):
    """
    مقیاس‌سازی مختصات از یک صفحه به صفحه‌ی دیگر
    
    Args:
        x, y: مختصات در صفحه‌ی مبدا
        src_width, src_height: ابعاد صفحه‌ی مبدا
        dst_width, dst_height: ابعاد صفحه‌ی مقصد
    
    Returns:
        tuple: (new_x, new_y) مختصات در صفحه‌ی مقصد
    """
    new_x = int(x * dst_width / src_width)
    new_y = int(y * dst_height / src_height)
    return new_x, new_y


def clamp(value, min_value, max_value):
    """
    محدود کردن یک مقدار بین دو حد
    
    Args:
        value: مقدار ورودی
        min_value: حداقل
        max_value: حداکثر
    
    Returns:
        value: مقدار محدود شده
    """
    return max(min_value, min(max_value, value))


def get_fps(start_time, frame_count):
    """
    محاسبه‌ی FPS
    
    Args:
        start_time: زمان شروع (از time.time())
        frame_count: تعداد فریم‌ها
    
    Returns:
        float: FPS
    """
    import time
    elapsed = time.time() - start_time
    if elapsed == 0:
        return 0
    return frame_count / elapsed


def draw_text_with_background(frame, text, position, font_scale, color, thickness, bg_color=None, padding=5):
    """
    نمایش متن با پس‌زمینه روی تصویر
    
    Args:
        frame: تصویر
        text: متن
        position: موقعیت (x, y)
        font_scale: اندازه‌ی فونت
        color: رنگ متن (BGR)
        thickness: ضخامت
        bg_color: رنگ پس‌زمینه (اختیاری)
        padding: فاصله‌ی پس‌زمینه از متن
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    if bg_color:
        x, y = position
        # رسم مستطیل پس‌زمینه
        cv2.rectangle(frame, 
                     (x - padding, y - text_height - padding),
                     (x + text_width + padding, y + padding),
                     bg_color, -1)
    
    # رسم متن
    cv2.putText(frame, text, position, font, font_scale, color, thickness)


def log_message(message, level="INFO"):
    """
    ثبت پیام در کنسول با زمان
    
    Args:
        message: پیام
        level: سطح پیام (INFO, WARNING, ERROR, DEBUG)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def is_point_in_box(point, box_top_left, box_bottom_right):
    """
    بررسی اینکه آیا نقطه داخل کادر است
    
    Args:
        point: tuple (x, y)
        box_top_left: tuple (x1, y1)
        box_bottom_right: tuple (x2, y2)
    
    Returns:
        bool: True اگر داخل کادر باشد
    """
    x, y = point
    x1, y1 = box_top_left
    x2, y2 = box_bottom_right
    return x1 <= x <= x2 and y1 <= y <= y2


def get_center_of_box(box_top_left, box_bottom_right):
    """
    محاسبه‌ی مرکز کادر
    
    Args:
        box_top_left: tuple (x1, y1)
        box_bottom_right: tuple (x2, y2)
    
    Returns:
        tuple: (center_x, center_y)
    """
    x1, y1 = box_top_left
    x2, y2 = box_bottom_right
    return ((x1 + x2) // 2, (y1 + y2) // 2)