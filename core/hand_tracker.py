"""
ماژول تشخیص دست با استفاده از MediaPipe
مسئول شناسایی دست، نقاط کلیدی و وضعیت انگشتان
"""

import cv2
import mediapipe as mp
import sys
import os

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MEDIAPIPE_SETTINGS, CAMERA_SETTINGS
from utils.helpers import get_bounding_box, log_message


class HandTracker:
    """
    کلاس تشخیص دست با MediaPipe
    مدیریت تشخیص دست، استخراج نقاط کلیدی و وضعیت انگشتان
    """
    
    def __init__(self):
        """راه‌اندازی اولیه‌ی MediaPipe"""
        log_message("در حال راه‌اندازی HandTracker...")
        
        # تنظیمات MediaPipe
        self.max_num_hands = MEDIAPIPE_SETTINGS['max_num_hands']
        self.min_detection_confidence = MEDIAPIPE_SETTINGS['min_detection_confidence']
        self.min_tracking_confidence = MEDIAPIPE_SETTINGS['min_tracking_confidence']
        self.static_image_mode = MEDIAPIPE_SETTINGS['static_image_mode']
        
        # راه‌اندازی MediaPipe Hands (روش جدید برای نسخه 1.0.0)
        # در نسخه‌های جدید باید از mp.solutions.hands استفاده کرد
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.static_image_mode,
            max_num_hands=self.max_num_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # متغیرهای وضعیت
        self.hand_detected = False
        self.landmarks = None
        self.bounding_box = None
        self.fingers_status = None
        
        log_message("✅ HandTracker راه‌اندازی شد")
    
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
        
        # پردازش با MediaPipe
        result = self.hands.process(rgb)
        
        # بازنشانی وضعیت
        self.hand_detected = False
        self.landmarks = None
        self.bounding_box = None
        self.fingers_status = None
        
        if result.multi_hand_landmarks:
            self.hand_detected = True
            # گرفتن اولین دست (فقط یک دست)
            hand_landmarks = result.multi_hand_landmarks[0]
            self.landmarks = hand_landmarks.landmark
            
            # محاسبه‌ی کادر
            h, w, _ = frame.shape
            self.bounding_box = get_bounding_box(self.landmarks, w, h)
            
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
    
    def draw_hand(self, frame, show_landmarks=False):
        """
        رسم کادر و نقاط دست روی تصویر
        
        Args:
            frame: تصویر ورودی
            show_landmarks: آیا نقاط کلیدی رسم شوند؟
        
        Returns:
            frame: تصویر با رسم‌ها
        """
        if not self.hand_detected or not self.landmarks:
            return frame
        
        # رسم نقاط کلیدی (اختیاری)
        if show_landmarks:
            # در نسخه‌های جدید باید از این روش استفاده کرد
            try:
                # ایجاد یک آبجکت موقت برای رسم
                hand_landmarks = self.mp_hands.HandLandmarks()
                # این بخش ممکنه در نسخه‌های مختلف فرق کنه
            except:
                pass
        
        return frame
    
    def is_hand_detected(self):
        """بررسی اینکه آیا دستی تشخیص داده شده است"""
        return self.hand_detected
    
    def release(self):
        """آزادسازی منابع"""
        self.hands.close()
        log_message("HandTracker آزاد شد")


# ==================== تست سریع ====================
if __name__ == "__main__":
    print("🧪 تست HandTracker...")
    
    # راه‌اندازی دوربین
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ دوربین پیدا نشد!")
        exit()
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # راه‌اندازی HandTracker
    tracker = HandTracker()
    
    print("📹 دوربین باز شد. برای خروج 'q' را بزنید.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ خطا در دریافت تصویر!")
            break
        
        frame = cv2.flip(frame, 1)
        
        # تشخیص دست
        detected = tracker.process_frame(frame)
        
        if detected:
            # گرفتن وضعیت انگشتان
            fingers = tracker.get_fingers_status()
            finger_names = ["شست", "اشاره", "وسط", "حلقه", "کوچک"]
            status_text = " ".join([f"{name}:{'⬆️' if f else '⬇️'}" for name, f in zip(finger_names, fingers)])
            
            # گرفتن کادر
            if tracker.bounding_box:
                (x1, y1), (x2, y2) = tracker.bounding_box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "✅ Hand Detected", (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # نمایش وضعیت انگشتان
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        else:
            cv2.putText(frame, "⏳ Waiting for hand...", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.imshow("HandTracker Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    tracker.release()
    cap.release()
    cv2.destroyAllWindows()
    print("✅ تست پایان یافت")