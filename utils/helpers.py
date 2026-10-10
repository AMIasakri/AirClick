"""
توابع کمکی عمومی برای پروژه AirClick
"""

import math
import sys
import cv2
import os
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from collections import deque
import traceback
import time

MAX_LOG_BYTES = 512 * 1024
INSTALL_REGISTRY_KEY = r"Software\AirClick"
_logging_enabled = False
_log_path = None


def _ensure_utf8_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


_ensure_utf8_stdout()


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
    line = f"[{timestamp}] [{level}] {message}"
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", errors="replace").decode("ascii"))
    if not _logging_enabled or not _log_path:
        return

    try:
        os.makedirs(os.path.dirname(_log_path), exist_ok=True)
        new_line = line + "\n"
        if os.path.exists(_log_path) and os.path.getsize(_log_path) + len(new_line.encode("utf-8")) > MAX_LOG_BYTES:
            with open(_log_path, "rb") as log_file:
                recent = log_file.read(MAX_LOG_BYTES // 2)
            with open(_log_path, "wb") as log_file:
                log_file.write(recent)
                log_file.write(b"\n--- log truncated; keeping recent entries ---\n")
        with open(_log_path, "a", encoding="utf-8") as log_file:
            log_file.write(new_line)
    except OSError:
        print(f"[WARNING] Could not write log file: {_log_path}")


def log_exception(context, error):
    """Record a concise error and its traceback for support diagnostics."""
    log_message(f"{context}: {error}", "ERROR")
    traceback_text = traceback.format_exc()
    if traceback_text and traceback_text.strip() != "NoneType: None":
        for line in traceback_text.rstrip().splitlines():
            log_message(line, "ERROR")


def show_error(title, message):
    root = tk.Tk()
    root.withdraw()
    try:
        messagebox.showerror(title, message, parent=root)
    finally:
        root.destroy()


def configure_logging():
    """Ask once whether the user wants bounded logs beside the installed app."""
    global _logging_enabled, _log_path
    settings_root = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "AirClick",
    )
    preference_path = os.path.join(settings_root, "preferences.json")
    consent = None

    try:
        os.makedirs(settings_root, exist_ok=True)
        if os.path.exists(preference_path):
            with open(preference_path, encoding="utf-8") as preference_file:
                preference = json.load(preference_file)
            consent = preference.get("save_logs")
    except (OSError, ValueError):
        consent = None

    if consent is None:
        root = None
        try:
            root = tk.Tk()
            root.withdraw()
            consent = messagebox.askyesno(
                "AirClick",
                "آیا می‌خواهید گزارش خطاها و عملکرد برنامه در فایل لاگ ذخیره شود؟\n"
                "حجم لاگ حداکثر ۵۱۲ کیلوبایت است و کنار برنامه ذخیره می‌شود.",
                parent=root,
            )
        except Exception:
            consent = False
        finally:
            if root is not None:
                try:
                    root.destroy()
                except Exception:
                    pass

        try:
            with open(preference_path, "w", encoding="utf-8") as preference_file:
                json.dump({"save_logs": consent}, preference_file)
        except OSError:
            pass

    if consent:
        if getattr(sys, "_MEIPASS", None):
            install_root = os.path.dirname(sys.executable)
        else:
            install_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _log_path = os.path.join(install_root, "logs", "airclick.log")
        _logging_enabled = True


def require_installed_build():
    """Prevent a packaged executable from running without the Inno Setup marker."""
    if not getattr(sys, "_MEIPASS", None):
        return

    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            INSTALL_REGISTRY_KEY,
            0,
            winreg.KEY_READ,
        ) as key:
            installed, _ = winreg.QueryValueEx(key, "Installed")
    except (FileNotFoundError, OSError):
        installed = None

    if installed != "1":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "AirClick",
            "این نسخه باید ابتدا با Setup نصب شود.",
            parent=root,
        )
        root.destroy()
        raise SystemExit(1)


class RollingFpsCounter:
    def __init__(self, window_seconds=2.0):
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.window_seconds = window_seconds
        self._frame_times = deque()

    def tick(self, now=None):
        now = time.monotonic() if now is None else now
        if self._frame_times and now <= self._frame_times[-1]:
            raise ValueError("frame timestamps must increase")

        self._frame_times.append(now)
        cutoff = now - self.window_seconds
        while self._frame_times[0] < cutoff:
            self._frame_times.popleft()

        if len(self._frame_times) < 2:
            return 0.0
        elapsed = self._frame_times[-1] - self._frame_times[0]
        return (len(self._frame_times) - 1) / elapsed


class RollingPerformanceMonitor:
    def __init__(self, window_seconds=2.0):
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.window_seconds = window_seconds
        self._samples = deque()

    def update(self, metrics, now=None):
        now = time.monotonic() if now is None else now
        if self._samples and now <= self._samples[-1][0]:
            raise ValueError("sample timestamps must increase")

        self._samples.append((now, dict(metrics)))
        cutoff = now - self.window_seconds
        while self._samples[0][0] < cutoff:
            self._samples.popleft()

        sample_count = len(self._samples)
        keys = self._samples[-1][1]
        return {
            key: sum(sample[1][key] for sample in self._samples) / sample_count
            for key in keys
        }