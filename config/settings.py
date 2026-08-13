"""
تنظیمات اصلی پروژه AirClick
"""

# ==================== تنظیمات دوربین ====================
CAMERA_SETTINGS = {
    'camera_id': 0,
    'frame_width': 640,
    'frame_height': 480,
    'flip_frame': True,
}

# ==================== تنظیمات MediaPipe ====================
MEDIAPIPE_SETTINGS = {
    'max_num_hands': 2,          # تشخیص دو دست
    'min_detection_confidence': 0.7,
    'min_tracking_confidence': 0.5,
    'static_image_mode': False,
}

# ==================== تنظیمات ماوس ====================
MOUSE_SETTINGS = {
    'smoothing_factor': 0.6,
    'action_cooldown': 0.5,
    'movement_speed': 1.0,
}

# ==================== تنظیمات نمایش ====================
DISPLAY_SETTINGS = {
    'show_fps': True,
    'show_landmarks': True,
    'box_padding': 20,
}

# ==================== تنظیمات رنگ‌ها (BGR) ====================
COLORS = {
    'box_idle': (0, 255, 0),       # سبز
    'box_moving': (0, 255, 0),     # سبز
    'box_click': (0, 165, 255),    # نارنجی
    'box_error': (0, 0, 255),      # قرمز
    'cursor_point': (0, 255, 255), # زرد
}

# ==================== تنظیمات حرکات ====================
GESTURE_SETTINGS = {
    'gesture_names': {
        'all_open': 'READY',
        'only_index': 'MOVING',
        'index_folded_middle_open': 'LEFT CLICK',
        'index_middle_open': 'RIGHT CLICK',
        'fist': 'MIDDLE CLICK',
        'unknown': 'DETECTING...',
    }
}