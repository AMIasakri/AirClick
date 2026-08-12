"""
تنظیمات اصلی پروژه AirClick
همه‌ی پارامترهای قابل تنظیم در این فایل متمرکز شده‌اند
"""

# ==================== تنظیمات دوربین ====================
CAMERA_SETTINGS = {
    'camera_id': 0,              # شماره دوربین (معمولاً 0 برای وب‌کم)
    'frame_width': 640,          # پهنای تصویر
    'frame_height': 480,         # ارتفاع تصویر
    'fps': 30,                   # فریم بر ثانیه
    'flip_frame': True,          # آینه‌کردن تصویر
}

# ==================== تنظیمات MediaPipe ====================
MEDIAPIPE_SETTINGS = {
    'max_num_hands': 1,          # حداکثر تعداد دست‌ها (فقط یک دست)
    'min_detection_confidence': 0.7,   # حداقل اطمینان تشخیص (0.0 تا 1.0)
    'min_tracking_confidence': 0.5,    # حداقل اطمینان ردیابی (0.0 تا 1.0)
    'static_image_mode': False,        # حالت تصویر ثابت (False برای ویدیو)
}

# ==================== تنظیمات ماوس ====================
MOUSE_SETTINGS = {
    'smoothing_factor': 0.6,     # ضریب نرم‌سازی حرکت (0.0 تا 1.0)
                                 # عدد بیشتر = نرم‌تر ولی با تأخیر بیشتر
    'action_cooldown': 0.3,      # زمان جلوگیری از کلیک چندباره (ثانیه)
    'movement_speed': 1.0,       # ضریب سرعت حرکت (1.0 = عادی)
}

# ==================== تنظیمات نمایش ====================
DISPLAY_SETTINGS = {
    'show_fps': True,            # نمایش FPS روی صفحه
    'show_landmarks': False,     # نمایش نقاط کلیدی دست (فقط کادر نشان داده می‌شه)
    'box_padding': 20,           # فاصله‌ی کادر از دست (پیکسل)
    'font_scale': 0.7,           # اندازه‌ی فونت
    'font_thickness': 2,         # ضخامت فونت
}

# ==================== تنظیمات رنگ‌ها (BGR) ====================
COLORS = {
    'box_idle': (0, 255, 0),     # سبز - حالت آماده
    'box_moving': (255, 165, 0), # نارنجی - حالت حرکت
    'box_click': (0, 0, 255),    # قرمز - حالت کلیک
    'box_error': (0, 0, 255),    # قرمز - خطا
    'text_white': (255, 255, 255), # سفید
    'text_yellow': (0, 255, 255),  # زرد
    'cursor_point': (0, 255, 255), # زرد - نقطه‌ی نشانگر
}

# ==================== تنظیمات حرکات ====================
GESTURE_SETTINGS = {
    # آستانه‌های تشخیص انگشت‌ها
    'finger_threshold': 0.3,     # نسبت فاصله‌ی نوک به مفصل وسط
    'thumb_threshold': 0.1,      # آستانه‌ی تشخیص شست
    
    # نام حرکات (برای نمایش)
    'gesture_names': {
        'all_open': '🖐️ آماده',
        'only_index': '🖱️ حرکت',
        'index_folded_middle_open': '🖱️ کلیک چپ',
        'index_middle_open': '🖱️ کلیک راست',
        'fist': '🖱️ کلیک وسط',
        'unknown': '🔍 در حال تشخیص...',
        'waiting': '⏳ در انتظار دست...'
    }
}

# ==================== تنظیمات لاگ ====================
LOG_SETTINGS = {
    'enable_logging': True,      # فعال‌سازی لاگ
    'log_file': 'logs/airclick.log',  # مسیر فایل لاگ
    'log_level': 'INFO',         # سطح لاگ: DEBUG, INFO, WARNING, ERROR
}

# ==================== کلاس تنظیمات (برای دسترسی آسان) ====================
class Config:
    """کلاس دسترسی به تنظیمات به صورت آبجکت"""
    
    @staticmethod
    def get_camera():
        return CAMERA_SETTINGS
    
    @staticmethod
    def get_mediapipe():
        return MEDIAPIPE_SETTINGS
    
    @staticmethod
    def get_mouse():
        return MOUSE_SETTINGS
    
    @staticmethod
    def get_display():
        return DISPLAY_SETTINGS
    
    @staticmethod
    def get_colors():
        return COLORS
    
    @staticmethod
    def get_gestures():
        return GESTURE_SETTINGS
    
    @staticmethod
    def get_log():
        return LOG_SETTINGS