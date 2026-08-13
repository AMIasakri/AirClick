"""
AirClick - Hand Mouse Control با دو دست
دست راست = حرکت موس (کادر سبز) | دست چپ = کلیک چپ (کادر نارنجی)
"""

import cv2
import sys
import os
import time
import tkinter as tk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import CAMERA_SETTINGS, DISPLAY_SETTINGS, COLORS
from core.hand_tracker import HandTracker
from core.gesture_recognizer import GestureRecognizer
from core.mouse_controller import MouseController
from utils.helpers import log_message, get_fps


class HelpWindow:
    @staticmethod
    def show():
        root = tk.Tk()
        root.title("🎯 AirClick - Help Guide")
        root.geometry("450x450")
        root.resizable(False, False)
        root.configure(bg='#0f0f23')
        root.attributes('-topmost', True)
        
        header = tk.Frame(root, bg='#0f0f23')
        header.pack(fill='x', pady=15)
        
        tk.Label(header, text="🎯 AIRCLICK", 
                font=("Arial", 18, "bold"), fg="#e94560", bg='#0f0f23').pack()
        tk.Label(header, text="Two-Hand Mouse Control", 
                font=("Arial", 10), fg="#aaaaaa", bg='#0f0f23').pack()
        
        sep = tk.Frame(root, height=2, bg='#e94560')
        sep.pack(fill='x', padx=30, pady=10)
        
        gestures_frame = tk.Frame(root, bg='#0f0f23')
        gestures_frame.pack(pady=10)
        
        # دست راست (سبز)
        tk.Label(gestures_frame, text="🟢 RIGHT HAND - MOUSE MOVE", 
                font=("Arial", 11, "bold"), fg="#51cf66", bg='#0f0f23').pack(pady=5)
        
        right_gestures = [
            ("☝️ INDEX UP", "→  MOVE MOUSE", "#51cf66"),
            ("🖐️ ALL OPEN", "→  READY", "#4fc3f7"),
        ]
        
        for gesture, action, color in right_gestures:
            row = tk.Frame(gestures_frame, bg='#1a1a3e')
            row.pack(pady=3, padx=20, fill='x')
            tk.Label(row, text=gesture, font=("Arial", 10), 
                    fg="#ffffff", bg='#1a1a3e', width=15, anchor='w').pack(side='left')
            tk.Label(row, text=action, font=("Arial", 9), 
                    fg=color, bg='#1a1a3e').pack(side='right')
        
        sep2 = tk.Frame(gestures_frame, height=1, bg='#333366')
        sep2.pack(fill='x', padx=30, pady=10)
        
        # دست چپ (نارنجی)
        tk.Label(gestures_frame, text="🟠 LEFT HAND - CLICK", 
                font=("Arial", 11, "bold"), fg="#ff922b", bg='#0f0f23').pack(pady=5)
        
        left_gestures = [
            ("👇 CLOSE INDEX", "→  PRESS (Down)", "#ff6b6b"),
            ("☝️ OPEN INDEX", "→  RELEASE (Up)", "#51cf66"),
        ]
        
        for gesture, action, color in left_gestures:
            row = tk.Frame(gestures_frame, bg='#1a1a3e')
            row.pack(pady=3, padx=20, fill='x')
            tk.Label(row, text=gesture, font=("Arial", 10), 
                    fg="#ffffff", bg='#1a1a3e', width=15, anchor='w').pack(side='left')
            tk.Label(row, text=action, font=("Arial", 9), 
                    fg=color, bg='#1a1a3e').pack(side='right')
        
        sep3 = tk.Frame(root, height=1, bg='#333366')
        sep3.pack(fill='x', padx=30, pady=10)
        
        tips = [
            "🟢 Right hand = Move cursor",
            "🟠 Left hand = Click (Close/Open index)",
            "🔒 Mouse locks when hands leave",
            "⌨️ Press 'q' to exit"
        ]
        
        tips_frame = tk.Frame(root, bg='#0f0f23')
        tips_frame.pack(pady=5)
        
        for tip in tips:
            tk.Label(tips_frame, text=tip, font=("Arial", 9), 
                    fg="#8888aa", bg='#0f0f23').pack(pady=2)
        
        btn_frame = tk.Frame(root, bg='#0f0f23')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="✕ CLOSE", command=root.destroy,
                 font=("Arial", 10, "bold"), bg="#e94560", 
                 fg="white", padx=30, pady=8, relief='flat',
                 activebackground="#c73652", activeforeground="white",
                 cursor="hand2").pack()
        
        root.mainloop()


class AirClick:
    def __init__(self):
        log_message("=" * 50)
        log_message("🚀 AirClick Pro Starting...")
        log_message("=" * 50)
        
        self.hand_tracker = HandTracker()
        self.gesture_recognizer = GestureRecognizer()
        self.mouse_controller = MouseController()
        
        self.frame_width = 640
        self.frame_height = 480
        self.flip_frame = True
        self.show_fps = True
        self.show_landmarks = True
        
        self.running = False
        self.frame_count = 0
        self.start_time = time.time()
        
        # وضعیت دست‌ها
        self.left_hand_index = -1
        self.right_hand_index = -1
        self.current_gesture_right = "WAITING"
        self.current_gesture_left = "WAITING"
        
        # وضعیت کلیک
        self.index_was_down = False
        self.last_click_time = 0
        self.click_cooldown = 0.3
        
        self.mouse_locked = False
        self.hand_was_detected = False
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            log_message("❌ Camera not found!")
            sys.exit(1)
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        
        log_message(f"📹 Camera opened: {self.frame_width}x{self.frame_height}")
        log_message("=" * 50)
        self.print_help()
        log_message("=" * 50)
    
    def print_help(self):
        print("\n" + "=" * 50)
        print("  🎯 AIRCLICK - TWO HAND CONTROL")
        print("=" * 50)
        print("  🟢  RIGHT HAND (GREEN):")
        print("     ☝️  INDEX UP  →  MOVE MOUSE")
        print("     🖐️  ALL OPEN  →  READY")
        print("  🟠  LEFT HAND (ORANGE):")
        print("     👇  CLOSE INDEX  →  CLICK (Press)")
        print("     ☝️  OPEN INDEX   →  RELEASE (Up)")
        print("-" * 50)
        print("  💡 Right hand = Move, Left hand = Click")
        print("  ⌨️  'q' = Exit    'h' = Help")
        print("=" * 50 + "\n")
    
    def run(self):
        self.running = True
        
        cv2.namedWindow("AirClick", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("AirClick", 660, 520)
        cv2.setWindowProperty("AirClick", cv2.WND_PROP_TOPMOST, 1)
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            processed_frame = self.process_frame(frame)
            
            # نوار پایین
            cv2.rectangle(processed_frame, (0, self.frame_height - 35), 
                         (self.frame_width, self.frame_height), (20, 20, 30), -1)
            
            # اطلاعات دست‌ها
            right_status = f"🟢 R:{self.current_gesture_right}"
            left_status = f"🟠 L:{self.current_gesture_left}"
            
            cv2.putText(processed_frame, right_status, (15, self.frame_height - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(processed_frame, left_status, (230, self.frame_height - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
            
            # وضعیت کلیک
            click_status = "🔴 CLICK" if self.mouse_controller.is_pressed else "🟢 READY"
            click_color = (0, 0, 255) if self.mouse_controller.is_pressed else (0, 255, 0)
            cv2.putText(processed_frame, click_status, 
                       (self.frame_width - 180, self.frame_height - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, click_color, 1)
            
            if self.show_fps:
                fps = get_fps(self.start_time, self.frame_count)
                cv2.putText(processed_frame, f"⚡ {fps:.0f}", 
                           (self.frame_width - 55, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            cv2.putText(processed_frame, "q:Exit  h:Help", 
                       (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            cv2.imshow("AirClick", processed_frame)
            self.frame_count += 1
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                self.running = False
                break
            elif key == ord('h'):
                import threading
                threading.Thread(target=HelpWindow.show, daemon=True).start()
        
        self.cleanup()
    
    def process_frame(self, frame):
        hand_count = self.hand_tracker.process_frame(frame)
        
        # پیدا کردن دست چپ و راست
        self.left_hand_index = -1
        self.right_hand_index = -1
        
        for i in range(hand_count):
            hand_type = self.hand_tracker.get_hand_type(i)
            if hand_type == 'Left':
                self.left_hand_index = i
            elif hand_type == 'Right':
                self.right_hand_index = i
        
        # ====== پردازش دست راست (حرکت موس) - کادر سبز ======
        if self.right_hand_index != -1:
            self.hand_was_detected = True
            if self.mouse_locked:
                self.mouse_locked = False
                log_message("🔓 Mouse unlocked")
            
            fingers_right = self.hand_tracker.get_fingers_status(self.right_hand_index)
            gesture_right = self.gesture_recognizer.recognize(fingers_right)
            self.current_gesture_right = gesture_right
            
            # حرکت موس: فقط انگشت اشاره بالا، بقیه پایین
            index_up = fingers_right[1]
            other_fingers = fingers_right[2:]
            is_moving = index_up and not any(other_fingers)
            
            if is_moving:
                h, w, _ = frame.shape
                tip_x, tip_y = self.hand_tracker.get_index_tip((h, w, 3), self.right_hand_index)
                self.mouse_controller.move(tip_x, tip_y, self.frame_width, self.frame_height)
            
            # کادر سبز برای دست راست
            if self.hand_tracker.get_bounding_box(self.right_hand_index):
                (x1, y1), (x2, y2) = self.hand_tracker.get_bounding_box(self.right_hand_index)
                color = (0, 255, 0)  # سبز
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, "RIGHT", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                # نقاط دست راست
                if self.show_landmarks:
                    self.hand_tracker.draw_landmarks(frame, (0, 255, 255), self.right_hand_index)
        
        # ====== پردازش دست چپ (کلیک) - کادر نارنجی ======
        if self.left_hand_index != -1:
            self.hand_was_detected = True
            if self.mouse_locked:
                self.mouse_locked = False
                log_message("🔓 Mouse unlocked")
            
            fingers_left = self.hand_tracker.get_fingers_status(self.left_hand_index)
            gesture_left = self.gesture_recognizer.recognize(fingers_left)
            self.current_gesture_left = gesture_left
            
            # تشخیص کلیک با انگشت اشاره دست چپ
            index_up_left = fingers_left[1]
            current_time = time.time()
            
            if not index_up_left and not self.index_was_down:
                if current_time - self.last_click_time > self.click_cooldown:
                    self.index_was_down = True
                    self.mouse_controller.click_down()
                    self.last_click_time = current_time
                    log_message("🟠 Left Click PRESS")
            
            elif index_up_left and self.index_was_down:
                self.index_was_down = False
                self.mouse_controller.click_up()
                log_message("🟠 Left Click RELEASE")
            
            # کادر نارنجی برای دست چپ
            if self.hand_tracker.get_bounding_box(self.left_hand_index):
                (x1, y1), (x2, y2) = self.hand_tracker.get_bounding_box(self.left_hand_index)
                color = (0, 165, 255)  # نارنجی
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, "LEFT", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                # ایموجی کلیک روی کادر چپ
                emoji = "👇" if self.mouse_controller.is_pressed else "☝️"
                cv2.putText(frame, emoji, (x1 + 5, y1 + 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                
                # نقاط دست چپ
                if self.show_landmarks:
                    self.hand_tracker.draw_landmarks(frame, (0, 165, 255), self.left_hand_index)
        
        # ====== لاک موس ======
        if self.left_hand_index == -1 and self.right_hand_index == -1:
            if self.hand_was_detected and not self.mouse_locked:
                self.mouse_locked = True
                log_message("🔒 Mouse locked")
                if self.mouse_controller.is_pressed:
                    self.mouse_controller.click_up()
                    self.index_was_down = False
            
            cv2.putText(frame, "⏳ NO HAND", 
                       (self.frame_width//2 - 60, self.frame_height//2 + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 200), 2)
            
            self.current_gesture_right = "WAITING"
            self.current_gesture_left = "WAITING"
            self.mouse_controller.reset()
        
        return frame
    
    def cleanup(self):
        log_message("🧹 Cleaning up...")
        try:
            self.hand_tracker.release()
            self.cap.release()
            cv2.destroyAllWindows()
        except:
            pass
        log_message("✅ AirClick stopped!")
        log_message("=" * 50)


if __name__ == "__main__":
    try:
        app = AirClick()
        app.run()
    except KeyboardInterrupt:
        log_message("⚠️ Interrupted")
    except Exception as e:
        log_message(f"❌ Error: {e}")
    finally:
        cv2.destroyAllWindows()