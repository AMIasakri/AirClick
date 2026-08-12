"""
تست MediaPipe با روش tasks
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

print("✅ MediaPipe version:", mp.__version__)
print("✅ Available modules:", dir(mp))

# ==================== تست تشخیص دست با روش جدید ====================
print("\n🧪 تست تشخیص دست با روش tasks...")

# راه‌اندازی دوربین
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ دوربین پیدا نشد!")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# تنظیمات تشخیص دست
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options,
                                       num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

print("📹 دوربین باز شد. برای خروج 'q' را بزنید.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # تبدیل به Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    
    # تشخیص دست
    detection_result = detector.detect(mp_image)
    
    if detection_result.hand_landmarks:
        hand_landmarks = detection_result.hand_landmarks[0]
        
        # پیدا کردن کادر
        h, w, _ = frame.shape
        x_coords = [lm.x for lm in hand_landmarks]
        y_coords = [lm.y for lm in hand_landmarks]
        x_min = int(min(x_coords) * w) - 20
        x_max = int(max(x_coords) * w) + 20
        y_min = int(min(y_coords) * h) - 20
        y_max = int(max(y_coords) * h) + 20
        
        # کشیدن کادر سبز
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(frame, "✅ Hand Detected", (x_min, y_min - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # کشیدن نقاط
        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)
    
    cv2.imshow("MediaPipe Test - Tasks Method", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("✅ تست پایان یافت")
