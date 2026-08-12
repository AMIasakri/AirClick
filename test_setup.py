"""
تست اولیه‌ی پروژه AirClick
بررسی نصب کتابخونه‌ها و تنظیمات اولیه
"""

import sys
import cv2
import mediapipe as mp
import pyautogui

print("=" * 50)
print("🧪 تست اولیه‌ی AirClick")
print("=" * 50)

# 1. تست Python
print(f"\n✅ Python version: {sys.version}")

# 2. تست OpenCV
try:
    print(f"✅ OpenCV version: {cv2.__version__}")
except:
    print("❌ OpenCV نصب نیست!")
    sys.exit(1)

# 3. تست MediaPipe
try:
    print(f"✅ MediaPipe version: {mp.__version__}")
except:
    print("❌ MediaPipe نصب نیست!")
    sys.exit(1)

# 4. تست PyAutoGUI
try:
    screen_width, screen_height = pyautogui.size()
    print(f"✅ PyAutoGUI نصب است! صفحه‌نمایش: {screen_width}x{screen_height}")
except:
    print("❌ PyAutoGUI نصب نیست!")
    sys.exit(1)

# 5. تست دوربین
print("\n📹 در حال تست دوربین...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ دوربین پیدا نشد! لطفاً دوربین را بررسی کنید.")
    sys.exit(1)
else:
    print("✅ دوربین پیدا شد!")
    cap.release()

# 6. تست ساختار پوشه‌ها
import os
folders = ['core', 'utils', 'config', 'logs', 'assets']
print("\n📁 بررسی ساختار پوشه‌ها:")
for folder in folders:
    if os.path.exists(folder):
        print(f"  ✅ {folder}/")
    else:
        print(f"  ❌ {folder}/ وجود ندارد!")

# 7. تست فایل‌های اصلی
files = ['main.py', 'requirements.txt', 'README.md']
print("\n📄 بررسی فایل‌های اصلی:")
for file in files:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} وجود ندارد!")

print("\n" + "=" * 50)
print("✅ همه‌چیز آماده است! می‌توانید پروژه را شروع کنید.")
print("=" * 50)