"""
تست اولیه پروژه AirClick
بررسی نصب کتابخانه‌ها و تنظیمات اولیه
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
import mediapipe as mp
import pyautogui

from config.settings import CAMERA_SETTINGS, validate_settings
from utils.helpers import log_message


def main():
    log_message("=" * 50)
    log_message("AirClick setup test")
    log_message("=" * 50)

    log_message(f"Python version: {sys.version}")
    log_message(f"OpenCV version: {cv2.__version__}")
    log_message(f"MediaPipe version: {mp.__version__}")

    try:
        validate_settings()
    except ValueError as error:
        log_message(f"Invalid settings: {error}", "ERROR")
        sys.exit(1)
    log_message("Settings OK")

    screen_width, screen_height = pyautogui.size()
    log_message(f"PyAutoGUI OK — screen: {screen_width}x{screen_height}")

    log_message("Testing camera...")
    camera_id = CAMERA_SETTINGS['camera_id']
    cap = cv2.VideoCapture(camera_id)
    try:
        if not cap.isOpened():
            log_message(f"Camera {camera_id} not found!", "ERROR")
            sys.exit(1)
        log_message(f"Camera {camera_id} OK")
    finally:
        cap.release()

    folders = ['core', 'utils', 'config', 'ui', 'tests']
    log_message("Checking project structure:")
    missing = [f for f in folders if not os.path.exists(f)]
    for folder in folders:
        status = "OK" if folder not in missing else "MISSING"
        log_message(f"  {folder}/ — {status}")

    files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'hand_landmarker.task',
    ]
    log_message("Checking main files:")
    for file in files:
        status = "OK" if os.path.exists(file) else "MISSING"
        log_message(f"  {file} — {status}")

    missing_files = [file for file in files if not os.path.exists(file)]
    if missing or missing_files:
        log_message("Project structure is incomplete.", "ERROR")
        sys.exit(1)

    log_message("=" * 50)
    log_message("Setup test passed. Run: python main.py")
    log_message("=" * 50)


if __name__ == "__main__":
    main()
