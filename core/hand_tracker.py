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

from config.settings import MEDIAPIPE_SETTINGS, HAND_SETTINGS
from utils.helpers import log_message
import math


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
        
        self.max_lost_frames = 3

        self.mouse_hand_index = -1
        self.click_hand_index = -1
        self.hand_separation = None
        self.hands_too_close = False

        self.role_memory = {
            'mouse': {'center': None, 'lost': 0},
            'click': {'center': None, 'lost': 0},
        }
        
        log_message("HandTracker ready")
    
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

        self._assign_hand_roles(w, h)
        return len(self.hands_detected)

    def _hand_center(self, index):
        box = self.all_bounding_boxes[index]
        return (
            (box[0][0] + box[1][0]) // 2,
            (box[0][1] + box[1][1]) // 2,
        )

    def _update_role_memory(self, role, center):
        self.role_memory[role]['center'] = center
        self.role_memory[role]['lost'] = 0

    def _dist(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _resolve_single_hand_role(self, detection, frame_width):
        cx = detection['center_x']
        mouse_mem = self.role_memory['mouse']['center']
        click_mem = self.role_memory['click']['center']

        if mouse_mem and click_mem:
            if self._dist((cx, detection['center_y']), mouse_mem) <= self._dist((cx, detection['center_y']), click_mem):
                return 'mouse'
            return 'click'

        if mouse_mem and self.role_memory['mouse']['lost'] < 15:
            if self._dist((cx, detection['center_y']), mouse_mem) < 120:
                return 'mouse'
        if click_mem and self.role_memory['click']['lost'] < 15:
            if self._dist((cx, detection['center_y']), click_mem) < 120:
                return 'click'

        # دوربین آینه‌ای: دست راست کاربر سمت چپ تصویر
        return 'mouse' if cx < frame_width * 0.5 else 'click'

    def _match_hands_to_roles(self, d0, d1):
        c0 = (d0['center_x'], d0['center_y'])
        c1 = (d1['center_x'], d1['center_y'])
        mouse_mem = self.role_memory['mouse']['center']
        click_mem = self.role_memory['click']['center']

        if mouse_mem and click_mem:
            assign_a = self._dist(c0, mouse_mem) + self._dist(c1, click_mem)
            assign_b = self._dist(c0, click_mem) + self._dist(c1, mouse_mem)
            if assign_a <= assign_b:
                mouse_idx, click_idx = d0['index'], d1['index']
                mouse_center, click_center = c0, c1
            else:
                mouse_idx, click_idx = d1['index'], d0['index']
                mouse_center, click_center = c1, c0
        else:
            if d0['center_x'] <= d1['center_x']:
                mouse_idx, click_idx = d0['index'], d1['index']
                mouse_center, click_center = c0, c1
            else:
                mouse_idx, click_idx = d1['index'], d0['index']
                mouse_center, click_center = c1, c0

        self._update_role_memory('mouse', mouse_center)
        self._update_role_memory('click', click_center)
        return mouse_idx, click_idx

    def _assign_hand_roles(self, frame_width, frame_height):
        self.mouse_hand_index = -1
        self.click_hand_index = -1
        self.hand_separation = None
        self.hands_too_close = False

        live_indices = [i for i, live in enumerate(self.hand_is_live) if live]
        if not live_indices:
            self.role_memory['mouse']['lost'] += 1
            self.role_memory['click']['lost'] += 1
            return

        detections = []
        for i in live_indices:
            cx, cy = self._hand_center(i)
            detections.append({'index': i, 'center_x': cx, 'center_y': cy})

        if len(detections) == 1:
            d = detections[0]
            role = self._resolve_single_hand_role(d, frame_width)
            if role == 'mouse':
                self.mouse_hand_index = d['index']
                self._update_role_memory('mouse', (d['center_x'], d['center_y']))
                self.role_memory['click']['lost'] += 1
            else:
                self.click_hand_index = d['index']
                self._update_role_memory('click', (d['center_x'], d['center_y']))
                self.role_memory['mouse']['lost'] += 1
            return

        if len(detections) >= 2:
            detections.sort(key=lambda d: d['center_x'])
            d0, d1 = detections[0], detections[-1]
            self.hand_separation = self._dist(
                (d0['center_x'], d0['center_y']),
                (d1['center_x'], d1['center_y']),
            )
            self.hands_too_close = self.hand_separation < HAND_SETTINGS['min_hand_separation']
            self.mouse_hand_index, self.click_hand_index = self._match_hands_to_roles(d0, d1)

    def get_mouse_hand_index(self):
        return self.mouse_hand_index

    def get_click_hand_index(self):
        return self.click_hand_index

    def is_pointer_gesture(self, index, latched=False):
        """ژست اشاره برای حرکت موس — با تحمل خم شدن"""
        if self.is_drag_gesture(index):
            return False

        landmarks = self.get_landmarks(index)
        if not landmarks:
            return False

        middle_up = self._finger_extended(landmarks, 12, 10, margin=0.006)
        ring_up = self._finger_extended(landmarks, 16, 14, margin=0.006)
        pinky_up = self._finger_extended(landmarks, 20, 18, margin=0.006)
        if middle_up or ring_up or pinky_up:
            return False

        tip, pip, mcp = landmarks[8], landmarks[6], landmarks[5]
        bend_limit = HAND_SETTINGS['movement_index_bend']

        if latched and HAND_SETTINGS['movement_latch']:
            return tip.y < mcp.y + bend_limit

        return tip.y < pip.y + 0.006 and tip.y < mcp.y + bend_limit * 0.7

    def is_drag_gesture(self, index):
        """V sign — اشاره و وسط بالا"""
        landmarks = self.get_landmarks(index)
        if not landmarks:
            return False

        index_up = self._finger_extended(landmarks, 8, 6, margin=0.008)
        middle_up = self._finger_extended(landmarks, 12, 10, margin=0.008)
        ring_up = self._finger_extended(landmarks, 16, 14, margin=0.006)
        pinky_up = self._finger_extended(landmarks, 20, 18, margin=0.006)
        return index_up and middle_up and not ring_up and not pinky_up

    def get_hand_center_y(self, index, frame_height):
        box = self.get_bounding_box(index)
        if box:
            return (box[0][1] + box[1][1]) // 2
        landmarks = self.get_landmarks(index)
        if landmarks:
            ys = [lm.y for lm in landmarks]
            return int(sum(ys) / len(ys) * frame_height)
        return None
    
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