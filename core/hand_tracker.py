"""
ماژول تشخیص دست با استفاده از MediaPipe 1.0.0 (روش tasks)
مسئول شناسایی دست، نقاط کلیدی و وضعیت انگشتان
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import sys
import os

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MEDIAPIPE_SETTINGS
from utils.helpers import log_message


class HandTracker:
    """
    کلاس تشخیص دست با MediaPipe 1.0.0
    مدیریت تشخیص دست، استخراج نقاط کلیدی و وضعیت انگشتان
    """
    
    def __init__(self):
        """راه‌اندازی اولیه‌ی MediaPipe"""
        log_message("در حال راه‌اندازی HandTracker...")
        
        # تنظیمات MediaPipe
        self.max_num_hands = MEDIAPIPE_SETTINGS['max_num_hands']
        
        # بررسی وجود فایل مدل
        model_path = 'hand_landmarker.task'
        if not os.path.exists(model_path):
            log_message("⚠️ فایل مدل پیدا نشد! در حال دانلود...")
            self._download_model()
        
        # راه‌اندازی با روش tasks
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.max_num_hands,
            min_hand_detection_confidence=MEDIAPIPE_SETTINGS['min_detection_confidence'],
            min_hand_presence_confidence=MEDIAPIPE_SETTINGS['min_tracking_confidence'],
            min_tracking_confidence=MEDIAPIPE_SETTINGS['min_tracking_confidence']
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # متغیرهای وضعیت
        self.hand_detected = False
        self.landmarks = None
        self.bounding_box = None
        self.fingers_status = None
        
        log_message("✅ HandTracker راه‌اندازی شد")
    
    def _download_model(self):
        """دانلود فایل مدل"""
        import urllib.request
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        log_message(f"📥 در حال دانلود مدل از {url}...")
        urllib.request.urlretrieve(url, 'hand_landmarker.task')
        log_message("✅ مدل دانلود شد!")
    
    def process_frame(self, frame):
        """
        پردازش یک فریم و تشخیص دست
        
        Args:
            frame: تصویر ورودی (BGR)
        
        Returns:
            bool: آیا دستی تشخیص داده شد؟
        """
        # تبدیل BGR به RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # تبدیل به Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        # تشخیص دست
        detection_result = self.detector.detect(mp_image)
        
        # بازنشانی وضعیت
        self.hand_detected = False
        self.landmarks = None
        self.bounding_box = None
        self.fingers_status = None
        
        if detection_result.hand_landmarks:
            self.hand_detected = True
            # گرفتن اولین دست (فقط یک دست)
            hand_landmarks = detection_result.hand_landmarks[0]
            self.landmarks = hand_landmarks
            
            # محاسبه‌ی کادر
            h, w, _ = frame.shape
            x_coords = [lm.x for lm in hand_landmarks]
            y_coords = [lm.y for lm in hand_landmarks]
            x_min = int(min(x_coords) * w) - 20
            x_max = int(max(x_coords) * w) + 20
            y_min = int(min(y_coords) * h) - 20
            y_max = int(max(y_coords) * h) + 20
            
            # محدود کردن به ابعاد تصویر
            x_min = max(0, x_min)
            x_max = min(w, x_max)
            y_min = max(0, y_min)
            y_max = min(h, y_max)
            
            self.bounding_box = ((x_min, y_min), (x_max, y_max))
            
            # استخراج وضعیت انگشتان
            self.fingers_status = self.get_fingers_status()
            
            return True
        
        return False
    
    def get_fingers_status(self):
        """
        تشخیص وضعیت ۵ انگشت
        True = بالا، False = پایین
        
        Returns:
            list: [شست, اشاره, وسط, حلقه, کوچک]
        """
        if not self.landmarks:
            return [False, False, False, False, False]
        
        fingers = []
        
        # شست: مقایسه‌ی افقی (برای دست راست)
        # نوک شست (نقطه 4) و مفصل (نقطه 3)
        thumb_tip = self.landmarks[4]
        thumb_ip = self.landmarks[3]
        fingers.append(thumb_tip.x < thumb_ip.x)  # برای دست راست
        
        # ۴ انگشت دیگر: مقایسه‌ی عمودی
        # نوک انگشت باید بالاتر از مفصل وسط باشد
        tip_ids = [8, 12, 16, 20]    # نوک انگشتان
        pip_ids = [6, 10, 14, 18]    # مفاصل وسط
        
        for tip_id, pip_id in zip(tip_ids, pip_ids):
            fingers.append(self.landmarks[tip_id].y < self.landmarks[pip_id].y)
        
        return fingers
    
    def get_landmark_coords(self, landmark_id, frame_shape):
        """
        دریافت مختصات یک نقطه‌ی کلیدی
        
        Args:
            landmark_id: شناسه‌ی نقطه (0 تا 20)
            frame_shape: tuple (height, width, channels)
        
        Returns:
            tuple: (x, y) مختصات در تصویر
        """
        if not self.landmarks:
            return (0, 0)
        
        h, w, _ = frame_shape
        lm = self.landmarks[landmark_id]
        return (int(lm.x * w), int(lm.y * h))
    
    def get_index_tip(self, frame_shape):
        """
        دریافت مختصات نوک انگشت اشاره
        
        Args:
            frame_shape: tuple (height, width, channels)
        
        Returns:
            tuple: (x, y) مختصات
        """
        return self.get_landmark_coords(8, frame_shape)  # نقطه 8 = نوک اشاره
    
    def get_hand_center(self, frame_shape):
        """
        دریافت مرکز کادر دست
        
        Args:
            frame_shape: tuple (height, width, channels)
        
        Returns:
            tuple: (x, y) مرکز
        """
        if not self.bounding_box:
            return (0, 0)
        
        (x1, y1), (x2, y2) = self.bounding_box
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    def is_hand_detected(self):
        """بررسی اینکه آیا دستی تشخیص داده شده است"""
        return self.hand_detected
    
    def draw_landmarks(self, frame, color=(0, 255, 255)):
        """
        رسم نقاط و اتصالات دست روی تصویر
        
        Args:
            frame: تصویر
            color: رنگ نقاط (BGR)
        """
        if not self.landmarks:
            return frame
        
        h, w, _ = frame.shape
        
        # رسم نقاط
        for lm in self.landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 3, color, -1)
        
        # رسم اتصالات
        connections = [
            (0,1), (1,2), (2,3), (3,4),  # شست
            (0,5), (5,6), (6,7), (7,8),  # اشاره
            (0,9), (9,10), (10,11), (11,12),  # وسط
            (0,13), (13,14), (14,15), (15,16),  # حلقه
            (0,17), (17,18), (18,19), (19,20),  # کوچک
            (5,9), (9,13), (13,17)  # اتصالات بین انگشتان
        ]
        for i, j in connections:
            x1, y1 = int(self.landmarks[i].x * w), int(self.landmarks[i].y * h)
            x2, y2 = int(self.landmarks[j].x * w), int(self.landmarks[j].y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        return frame
    
    def release(self):
        """آزادسازی منابع"""
        log_message("HandTracker released")


# ==================== تست سریع ====================
if __name__ == "__main__":
    print("🧪 HandTracker Test...")
    
    # راه‌اندازی دوربین
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera not found!")
        exit()
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # راه‌اندازی HandTracker
    tracker = HandTracker()
    
    print("📹 Camera opened. Press 'q' to exit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error reading frame!")
            break
        
        frame = cv2.flip(frame, 1)
        
        # تشخیص دست
        detected = tracker.process_frame(frame)
        
        if detected:
            # گرفتن وضعیت انگشتان
            fingers = tracker.get_fingers_status()
            finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
            status_text = " ".join([f"{name}:{'UP' if f else 'DOWN'}" for name, f in zip(finger_names, fingers)])
            
            # گرفتن کادر
            if tracker.bounding_box:
                (x1, y1), (x2, y2) = tracker.bounding_box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "HAND DETECTED", (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # رسم نقاط و اتصالات
            tracker.draw_landmarks(frame)
            
            # نمایش وضعیت انگشتان
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        else:
            cv2.putText(frame, "WAITING FOR HAND...", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.imshow("HandTracker Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    tracker.release()
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Test finished")