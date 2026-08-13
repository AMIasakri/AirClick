"""
ماژول تشخیص دست با MediaPipe 1.0.0 - پشتیبانی از چند دست
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MEDIAPIPE_SETTINGS
from utils.helpers import log_message


class HandTracker:
    """کلاس تشخیص دست با پشتیبانی از چند دست"""
    
    def __init__(self):
        log_message("در حال راه‌اندازی HandTracker...")
        
        self.max_num_hands = MEDIAPIPE_SETTINGS['max_num_hands']
        
        model_path = 'hand_landmarker.task'
        if not os.path.exists(model_path):
            log_message("⚠️ مدل پیدا نشد! در حال دانلود...")
            self._download_model()
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.max_num_hands,
            min_hand_detection_confidence=MEDIAPIPE_SETTINGS['min_detection_confidence'],
            min_hand_presence_confidence=MEDIAPIPE_SETTINGS['min_tracking_confidence'],
            min_tracking_confidence=MEDIAPIPE_SETTINGS['min_tracking_confidence']
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # لیست برای ذخیره چند دست
        self.hands_detected = []
        self.all_landmarks = []
        self.all_bounding_boxes = []
        self.all_fingers_status = []
        self.hand_types = []  # 'Left' یا 'Right'
        
        log_message("✅ HandTracker راه‌اندازی شد")
    
    def _download_model(self):
        import urllib.request
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        log_message(f"📥 در حال دانلود مدل...")
        urllib.request.urlretrieve(url, 'hand_landmarker.task')
        log_message("✅ مدل دانلود شد!")
    
    def process_frame(self, frame):
        """
        پردازش فریم و تشخیص همه دست‌ها
        Returns: تعداد دست‌های تشخیص داده شده
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = self.detector.detect(mp_image)
        
        # پاک کردن لیست‌ها
        self.hands_detected = []
        self.all_landmarks = []
        self.all_bounding_boxes = []
        self.all_fingers_status = []
        self.hand_types = []
        
        if detection_result.hand_landmarks:
            h, w, _ = frame.shape
            
            # تشخیص نوع دست (چپ/راست) از hand_landmarks
            for i, hand_landmarks in enumerate(detection_result.hand_landmarks):
                self.hands_detected.append(True)
                self.all_landmarks.append(hand_landmarks)
                
                # تشخیص چپ یا راست بودن دست
                if detection_result.handedness and i < len(detection_result.handedness):
                    hand_type = detection_result.handedness[i][0].category_name
                    self.hand_types.append(hand_type)  # 'Left' یا 'Right'
                else:
                    self.hand_types.append('Unknown')
                
                # محاسبه کادر
                x_coords = [lm.x for lm in hand_landmarks]
                y_coords = [lm.y for lm in hand_landmarks]
                x_min = int(min(x_coords) * w) - 20
                x_max = int(max(x_coords) * w) + 20
                y_min = int(min(y_coords) * h) - 20
                y_max = int(max(y_coords) * h) + 20
                
                x_min = max(0, x_min)
                x_max = min(w, x_max)
                y_min = max(0, y_min)
                y_max = min(h, y_max)
                
                self.all_bounding_boxes.append(((x_min, y_min), (x_max, y_max)))
                
                # وضعیت انگشتان
                fingers = self._get_fingers_status(hand_landmarks)
                self.all_fingers_status.append(fingers)
        
        return len(self.hands_detected)
    
    def _get_fingers_status(self, landmarks):
        """تشخیص وضعیت انگشتان برای یک دست"""
        fingers = []
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        fingers.append(thumb_tip.x < thumb_ip.x)
        
        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]
        
        for tip_id, pip_id in zip(tip_ids, pip_ids):
            fingers.append(landmarks[tip_id].y < landmarks[pip_id].y)
        
        return fingers
    
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
    
    def get_index_tip(self, frame_shape, index=0):
        landmarks = self.get_landmarks(index)
        if not landmarks:
            return (0, 0)
        h, w, _ = frame_shape
        lm = landmarks[8]
        return (int(lm.x * w), int(lm.y * h))
    
    def draw_landmarks(self, frame, color=(0, 255, 255), index=0):
        landmarks = self.get_landmarks(index)
        if not landmarks:
            return frame
        
        h, w, _ = frame.shape
        
        # رسم نقاط
        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 4, color, -1)
            cv2.circle(frame, (cx, cy), 4, (255, 255, 255), 1)
        
        # رسم اتصالات
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