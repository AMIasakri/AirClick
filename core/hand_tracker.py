"""
ماژول تشخیص دست با حافظه و پایداری بالا
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import sys
import os
import numpy as np
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MEDIAPIPE_SETTINGS
from utils.helpers import log_message


class HandTracker:
    """کلاس تشخیص دست با حافظه و پایداری بالا"""
    
    def __init__(self):
        log_message("در حال راه‌اندازی HandTracker...")
        
        self.max_num_hands = MEDIAPIPE_SETTINGS['max_num_hands']
        self.min_detection_confidence = MEDIAPIPE_SETTINGS['min_detection_confidence']
        self.min_tracking_confidence = MEDIAPIPE_SETTINGS['min_tracking_confidence']
        
        model_path = 'hand_landmarker.task'
        if not os.path.exists(model_path):
            log_message("⚠️ مدل پیدا نشد! در حال دانلود...")
            self._download_model()
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.max_num_hands,
            min_hand_detection_confidence=self.min_detection_confidence,
            min_hand_presence_confidence=self.min_tracking_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # لیست‌های اصلی
        self.hands_detected = []
        self.all_landmarks = []
        self.all_bounding_boxes = []
        self.all_fingers_status = []
        self.hand_types = []
        
        # ====== حافظه برای پایداری ======
        self.memory = {
            'right': {
                'position': None,  # آخرین موقعیت شناخته شده
                'box': None,       # آخرین کادر
                'fingers': None,   # آخرین وضعیت انگشتان
                'lost_frames': 0,  # تعداد فریم‌های از دست رفته
                'history': deque(maxlen=5)  # تاریخچه موقعیت‌ها
            },
            'left': {
                'position': None,
                'box': None,
                'fingers': None,
                'lost_frames': 0,
                'history': deque(maxlen=5)
            }
        }
        
        self.max_lost_frames = 3  # حافظه کوتاه فقط برای نمایش، نه کنترل موس
        
        log_message("✅ HandTracker راه‌اندازی شد (با حافظه و پایداری)")
    
    def _download_model(self):
        import urllib.request
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        log_message(f"📥 در حال دانلود مدل...")
        urllib.request.urlretrieve(url, 'hand_landmarker.task')
        log_message("✅ مدل دانلود شد!")
    
    def _enhance_frame(self, frame):
        """بهبود کیفیت تصویر"""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge((l, a, b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        return enhanced
    
    def _smooth_position(self, hand_type, new_x, new_y):
        """نرم‌سازی موقعیت با استفاده از تاریخچه"""
        if hand_type not in self.memory:
            return new_x, new_y
        
        history = self.memory[hand_type]['history']
        history.append((new_x, new_y))
        
        if len(history) >= 3:
            # میانگین وزنی - فریم‌های جدیدتر وزن بیشتری دارند
            weights = [1, 2, 3][-len(history):]
            weighted_avg_x = 0
            weighted_avg_y = 0
            total_weight = 0
            
            for i, (hx, hy) in enumerate(history):
                weight = weights[i] if i < len(weights) else 1
                weighted_avg_x += hx * weight
                weighted_avg_y += hy * weight
                total_weight += weight
            
            return weighted_avg_x / total_weight, weighted_avg_y / total_weight
        
        return new_x, new_y
    
    def process_frame(self, frame):
        """پردازش فریم با حافظه"""
        enhanced_frame = self._enhance_frame(frame)
        rgb = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = self.detector.detect(mp_image)
        
        # پاک کردن لیست‌های موقت
        self.hands_detected = []
        self.all_landmarks = []
        self.all_bounding_boxes = []
        self.all_fingers_status = []
        self.hand_types = []
        self.hand_is_live = []
        
        h, w, _ = frame.shape
        
        # ====== تشخیص دست‌ها ======
        detected_hands = {'Right': False, 'Left': False}
        
        if detection_result.hand_landmarks:
            for i, hand_landmarks in enumerate(detection_result.hand_landmarks):
                # تشخیص نوع دست
                if detection_result.handedness and i < len(detection_result.handedness):
                    hand_type = detection_result.handedness[i][0].category_name
                else:
                    hand_type = 'Unknown'
                
                # محاسبه کادر
                x_coords = [lm.x for lm in hand_landmarks]
                y_coords = [lm.y for lm in hand_landmarks]
                center_x = int(sum(x_coords) / len(x_coords) * w)
                center_y = int(sum(y_coords) / len(y_coords) * h)
                
                x_min = int(min(x_coords) * w) - 30
                x_max = int(max(x_coords) * w) + 30
                y_min = int(min(y_coords) * h) - 30
                y_max = int(max(y_coords) * h) + 30
                
                x_min = max(0, x_min)
                x_max = min(w, x_max)
                y_min = max(0, y_min)
                y_max = min(h, y_max)
                
                # نرم‌سازی موقعیت
                if hand_type in ['Right', 'Left']:
                    smooth_x, smooth_y = self._smooth_position(
                        hand_type.lower(), center_x, center_y
                    )
                    
                    # به‌روزرسانی حافظه
                    self.memory[hand_type.lower()]['position'] = (smooth_x, smooth_y)
                    self.memory[hand_type.lower()]['box'] = ((x_min, y_min), (x_max, y_max))
                    self.memory[hand_type.lower()]['lost_frames'] = 0
                    detected_hands[hand_type] = True
                
                self.hands_detected.append(True)
                self.all_landmarks.append(hand_landmarks)
                self.all_bounding_boxes.append(((x_min, y_min), (x_max, y_max)))
                
                fingers = self._get_fingers_status(hand_landmarks)
                self.all_fingers_status.append(fingers)
                self.hand_types.append(hand_type)
                self.hand_is_live.append(True)
                
                if hand_type in ['Right', 'Left']:
                    self.memory[hand_type.lower()]['fingers'] = list(fingers)
        
        # ====== پر کردن دست‌های از دست رفته با حافظه ======
        for hand_type in ['right', 'left']:
            if not detected_hands[hand_type.capitalize()]:
                self.memory[hand_type]['lost_frames'] += 1
                
                # اگر کمتر از حد مجاز از دست رفته، از حافظه استفاده کن
                if self.memory[hand_type]['lost_frames'] <= self.max_lost_frames:
                    if self.memory[hand_type]['position'] is not None:
                        # اضافه کردن به لیست با داده‌های حافظه
                        self.hands_detected.append(True)
                        self.hand_types.append(hand_type.capitalize())
                        
                        # استفاده از کادر حافظه
                        if self.memory[hand_type]['box']:
                            self.all_bounding_boxes.append(self.memory[hand_type]['box'])
                        else:
                            # کادر پیش‌فرض
                            self.all_bounding_boxes.append(((0, 0), (100, 100)))
                        
                        # استفاده از وضعیت انگشتان حافظه
                        if self.memory[hand_type]['fingers']:
                            self.all_fingers_status.append(self.memory[hand_type]['fingers'])
                        else:
                            self.all_fingers_status.append([True, True, False, False, False])
                        
                        # لندمارک‌های تقریبی (برای نمایش)
                        self.all_landmarks.append(None)
                        self.hand_is_live.append(False)
        
        return len(self.hands_detected)
    
    def _get_fingers_status(self, landmarks):
        """تشخیص وضعیت انگشتان با آستانه‌های نرم‌تر"""
        fingers = []
        
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        fingers.append(thumb_tip.x < thumb_ip.x + 0.02)
        
        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]
        
        for tip_id, pip_id in zip(tip_ids, pip_ids):
            is_up = landmarks[tip_id].y < landmarks[pip_id].y - 0.01
            fingers.append(is_up)
        
        return fingers
    
    def _finger_extended(self, landmarks, tip_id, pip_id, margin=0.01):
        return landmarks[tip_id].y < landmarks[pip_id].y - margin
    
    def get_click_fingers_status(self, index=0):
        """وضعیت انگشتان با حساسیت بهتر برای کلیک"""
        landmarks = self.get_landmarks(index)
        if not landmarks:
            cached = self.get_fingers_status(index)
            return cached if cached else [True, True, True, True, True]
        
        return [
            True,
            self._finger_extended(landmarks, 8, 6, margin=0.010),
            self._finger_extended(landmarks, 12, 10, margin=0.014),
            self._finger_extended(landmarks, 16, 14, margin=0.008),
            self._finger_extended(landmarks, 20, 18, margin=0.008),
        ]
    
    def get_hand_count(self):
        return len(self.hands_detected)
    
    def get_landmarks(self, index=0):
        if index < len(self.all_landmarks):
            return self.all_landmarks[index]
        return None
    
    def get_bounding_box(self, index=0):
        if index < len(self.all_bounding_boxes):
            return self.all_bounding_boxes[index]
        return None
    
    def get_fingers_status(self, index=0):
        if index < len(self.all_fingers_status):
            return self.all_fingers_status[index]
        return None
    
    def get_hand_type(self, index=0):
        if index < len(self.hand_types):
            return self.hand_types[index]
        return 'Unknown'
    
    def is_hand_live(self, index=0):
        if index < len(self.hand_is_live):
            return self.hand_is_live[index]
        return False
    
    def get_index_tip(self, frame_shape, index=0, live_only=False):
        if live_only and not self.is_hand_live(index):
            return None
        
        landmarks = self.get_landmarks(index)
        if landmarks:
            h, w, _ = frame_shape
            lm = landmarks[8]
            return (int(lm.x * w), int(lm.y * h))
        
        if live_only:
            return None
        
        hand_type = self.get_hand_type(index).lower()
        if hand_type in self.memory and self.memory[hand_type]['position']:
            pos = self.memory[hand_type]['position']
            return (int(pos[0]), int(pos[1]))
        
        return None
    
    def draw_landmarks(self, frame, color=(0, 255, 255), index=0):
        landmarks = self.get_landmarks(index)
        if not landmarks:
            # اگر لندمارک نداشت، یک نقطه ساده بکش
            hand_type = self.get_hand_type(index).lower()
            if hand_type in self.memory and self.memory[hand_type]['position']:
                pos = self.memory[hand_type]['position']
                cv2.circle(frame, (int(pos[0]), int(pos[1])), 10, color, -1)
            return frame
        
        h, w, _ = frame.shape
        
        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 5, color, -1)
            cv2.circle(frame, (cx, cy), 5, (255, 255, 255), 1)
        
        connections = [
            (0,1), (1,2), (2,3), (3,4),
            (0,5), (5,6), (6,7), (7,8),
            (0,9), (9,10), (10,11), (11,12),
            (0,13), (13,14), (14,15), (15,16),
            (0,17), (17,18), (18,19), (19,20),
            (5,9), (9,13), (13,17)
        ]
        for i, j in connections:
            x1, y1 = int(landmarks[i].x * w), int(landmarks[i].y * h)
            x2, y2 = int(landmarks[j].x * w), int(landmarks[j].y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        return frame
    
    def release(self):
        log_message("HandTracker released")