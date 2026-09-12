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

لاگ برنامه در `%LOCALAPPDATA%\AirClick\logs\airclick.log` ذخیره می‌شود و
برای جلوگیری از مصرف فضای دیسک، اندازه آن به‌صورت خودکار محدود می‌ماند.
در اولین اجرا برای ذخیره سابقه از کاربر اجازه گرفته می‌شود؛ با انتخاب «خیر»
هیچ فایل لاگی ساخته نمی‌شود. در نسخه نصب‌شده، در صورت موافقت، لاگ کنار فایل
اجرایی برنامه و در پوشه `logs` ذخیره می‌شود.

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

## ساخت Setup ویندوز

برای ساخت فایل اجرایی مستقل و نصب‌کننده شبیه برنامه‌های ویندوز:

1. [PyInstaller](https://pyinstaller.org/) و [Inno Setup](https://jrsoftware.org/isinfo.php) را نصب کن.
2. PowerShell را در ریشه پروژه باز کن.
3. این دستور را اجرا کن:

```powershell
python -m pip install pyinstaller
.\packaging\build_installer.ps1
```

فایل نصب در `dist/installer/AirClick-Setup-1.0.0.exe` ساخته می‌شود.
برای ساخت فقط نسخه اجرایی بدون نصب‌کننده، از `-SkipInstaller` استفاده کن.
