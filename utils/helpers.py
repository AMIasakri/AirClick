"""
توابع کمکی عمومی برای پروژه AirClick
"""

import math
import cv2
from datetime import datetime


def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def get_bounding_box(landmarks, w, h, padding=20):
    x_coords = [lm.x for lm in landmarks]
    y_coords = [lm.y for lm in landmarks]
    
    x_min = int(min(x_coords) * w) - padding
    x_max = int(max(x_coords) * w) + padding
    y_min = int(min(y_coords) * h) - padding
    y_max = int(max(y_coords) * h) + padding
    
    x_min = max(0, x_min)
    x_max = min(w, x_max)
    y_min = max(0, y_min)
    y_max = min(h, y_max)
    
    return (x_min, y_min), (x_max, y_max)


def log_message(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def get_fps(start_time, frame_count):
    import time
    elapsed = time.time() - start_time
    if elapsed == 0:
        return 0
    return frame_count / elapsed