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
    'max_num_hands': 2,
    'min_detection_confidence': 0.45,
    'min_tracking_confidence': 0.35,
    'static_image_mode': False,
}

# ==================== تنظیمات دست ====================
HAND_SETTINGS = {
    'min_hand_separation': 100,
    'movement_latch': True,
    'movement_index_bend': 0.065,
    'use_spatial_roles': True,
    'enhance_frame': False,
}

# ==================== تنظیمات عملکرد ====================
PERFORMANCE_SETTINGS = {
    'camera_buffer_size': 1,
    'skip_enhance_frame': True,
}

# ==================== تنظیمات ماوس ====================
MOUSE_SETTINGS = {
    'smoothing_factor': 0.50,
    'action_cooldown': 0.20,
    'left_click_cooldown': 0.12,
    'right_click_cooldown': 0.35,
    'other_click_cooldown': 0.25,
    'menu_mode_duration': 10.0,
    'menu_mode_dead_zone': 1,
    'movement_speed': 2.0,
    'dead_zone': 2,
    'relative_mode': True,
    'scroll_speed': 3,
    'scroll_dead_zone': 8,
    'double_click_interval': 0.35,
    'gesture_stability_frames': 3,
}

# ==================== تنظیمات نمایش ====================
DISPLAY_SETTINGS = {
    'show_fps': True,
    'show_landmarks': True,
    'show_hand_mesh': True,
    'mesh_line_thickness': 1,
    'mesh_glow_strength': 0.10,
    'show_debug': False,
    'box_padding': 25,
    'window_width': 680,
    'window_height': 540,
}

# ==================== رنگ‌ها (BGR) ====================
COLORS = {
    'box_right': (0, 255, 0),
    'box_left': (0, 165, 255),
    'box_click': (0, 0, 255),
    'box_drag': (255, 180, 60),
    'box_scroll': (200, 100, 255),
    'cursor_point': (0, 255, 255),
    'panel_bg': (18, 18, 32),
    'panel_border': (60, 60, 90),
    'text_primary': (240, 240, 250),
    'text_muted': (140, 140, 160),
    'accent': (96, 69, 233),
    'accent_light': (180, 130, 255),
    'success': (102, 207, 81),
    'warning': (43, 146, 255),
    'danger': (80, 80, 200),
}

# ==================== تنظیمات حرکات ====================
GESTURE_SETTINGS = {
    'gesture_names': {
        'all_open': 'READY',
        'only_index': 'MOVING',
        'index_middle_up': 'DRAG',
        'index_folded_middle_open': 'LEFT CLICK',
        'middle_folded_index_open': 'RIGHT CLICK',
        'index_middle_folded': 'DOUBLE CLICK',
        'ring_folded_scroll': 'SCROLL',
        'fist': 'MIDDLE CLICK',
        'unknown': 'DETECTING...',
        'waiting': 'WAITING',
    }
}
