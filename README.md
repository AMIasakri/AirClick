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
```

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
