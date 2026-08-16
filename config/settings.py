"""
تنظیمات اصلی پروژه AirClick - بهینه شده برای تشخیص راحت‌تر
"""

# ==================== تنظیمات دوربین ====================
CAMERA_SETTINGS = {
    'camera_id': 0,
    'frame_width': 640,
    'frame_height': 480,
    'flip_frame': True,
}

# ==================== تنظیمات MediaPipe (بهینه شده) ====================
MEDIAPIPE_SETTINGS = {
    'max_num_hands': 2,
    'min_detection_confidence': 0.5,  # کاهش از 0.7 به 0.5 برای تشخیص راحت‌تر
    'min_tracking_confidence': 0.3,   # کاهش از 0.5 به 0.3 برای ردیابی بهتر
    'static_image_mode': False,
}

# ==================== تنظیمات ماوس ====================
MOUSE_SETTINGS = {
    'smoothing_factor': 0.65,
    'action_cooldown': 0.25,
    'movement_speed': 1.8,       # حساسیت حرکت نسبی
    'dead_zone': 2,              # پیکسل - فیلتر لرزش
    'relative_mode': True,       # حرکت نسبی (جلوگیری از پرش موس)
}

# ==================== تنظیمات نمایش ====================
DISPLAY_SETTINGS = {
    'show_fps': True,
    'show_landmarks': True,
    'box_padding': 25,
}

# ==================== تنظیمات رنگ‌ها ====================
COLORS = {
    'box_right': (0, 255, 0),       # سبز - دست راست
    'box_left': (0, 165, 255),      # نارنجی - دست چپ
    'box_click': (0, 0, 255),       # قرمز - کلیک
    'cursor_point': (0, 255, 255),  # زرد
}

# ==================== تنظیمات حرکات ====================
GESTURE_SETTINGS = {
    'gesture_names': {
        'all_open': 'READY',
        'only_index': 'MOVING',
        'index_folded_middle_open': 'LEFT CLICK',
        'middle_folded_index_open': 'RIGHT CLICK',
        'index_middle_open': 'RIGHT CLICK',
        'fist': 'MIDDLE CLICK',
        'unknown': 'DETECTING...',
    }
}