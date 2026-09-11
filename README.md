# AirClick Pro

کنترل حرفه‌ای موس با دو دست — وب‌کم + MediaPipe + PyAutoGUI

## اجرا

```bash
pip install -r requirements.txt
python main.py
```

> در اولین اجرا، مدل MediaPipe (`hand_landmarker.task`) به‌صورت خودکار دانلود می‌شود.

## تست

```bash
python test_setup.py
python tests/test_gestures.py
python tests/test_hand_tracker.py
python tests/test_mouse_controller.py
python tests/test_settings.py
```

`test_setup.py` تنظیمات، وابستگی‌ها، دوربین و مدل MediaPipe را بررسی می‌کند.

## ژست‌ها

| دست | ژست | عمل |
|-----|-----|-----|
| موس | ☝️ فقط اشاره | حرکت موس |
| موس | ✌️ اشاره+وسط | Drag |
| کلیک | 👇 اشاره پایین | کلیک چپ |
| کلیک | 🖕 وسط پایین | کلیک راست |
| کلیک | ✊ مشت | کلیک وسط |
| کلیک | ✌️↓ اشاره+وسط پایین | دابل کلیک |
| کلیک | 💍 حلقه پایین | اسکرول |

## کلیدها

- `q` — خروج
- `h` — راهنما
- `d` — دیباگ

## تنظیم حساسیت

مقادیر قابل تنظیم در `config/settings.py` قرار دارند:

- `MOUSE_SETTINGS.movement_speed` — سرعت حرکت موس
- `MOUSE_SETTINGS.smoothing_factor` — نرمی حرکت، بین `0` و `1`
- `MOUSE_SETTINGS.dead_zone` — مقدار حرکت نادیده‌گرفته‌شده برای کاهش لرزش
- `MOUSE_SETTINGS.gesture_stability_frames` — تعداد فریم لازم برای تأیید ژست
- `HAND_SETTINGS.role_stability_frames` — تعداد فریم لازم برای تغییر نقش دست
- `HAND_SETTINGS.min_hand_separation` — حداقل فاصله دو دست

مقادیر نامعتبر هنگام شروع برنامه با خطای واضح رد می‌شوند.

## ساختار

```
AirClick/
├── main.py                 # حلقه اصلی
├── config/settings.py      # تنظیمات
├── core/
│   ├── hand_tracker.py     # تشخیص دست
│   ├── gesture_recognizer.py
│   └── mouse_controller.py
├── ui/overlay.py           # UI حرفه‌ای
└── utils/
```
