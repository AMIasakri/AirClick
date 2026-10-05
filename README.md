# AirClick Pro

کنترل حرفه‌ای موس با دو دست — وب‌کم + MediaPipe + PyAutoGUI

## اجرا

```bash
pip install -r requirements.txt
python main.py
```

> در اولین اجرا، مدل MediaPipe (`hand_landmarker.task`) به‌صورت خودکار دانلود می‌شود.

برای ساخت قابل‌تکرار روی Windows x64، از Python 3.14.7 و فایل نسخه‌های قفل‌شده
استفاده کنید:

```powershell
python -m pip install -r requirements-lock.txt
```

## حریم خصوصی و امنیت

- AirClick برای تشخیص دست از دوربین دستگاه استفاده می‌کند.
- پردازش تصویر به‌صورت محلی روی همان دستگاه انجام می‌شود.
- تصویر دوربین، فریم‌ها و اطلاعات دست به سرور AirClick ارسال نمی‌شوند.
- تصویر دوربین در فایل ذخیره نمی‌شود.
- مدل `hand_landmarker.task` در نسخه‌ی Setup همراه برنامه ارائه می‌شود. در اجرای
  نسخه‌ی سورس، اگر مدل در ریشه‌ی پروژه موجود نباشد، برنامه آن را از منبع رسمی
  MediaPipe دانلود می‌کند.
- ذخیره‌ی لاگ اختیاری است و برنامه در اولین اجرا برای فعال‌کردن آن اجازه می‌گیرد.
  لاگ شامل تصویر دوربین نیست و اندازه‌ی آن به حداکثر ۵۱۲ کیلوبایت محدود می‌شود.
- در صورت فعال‌کردن لاگ، فایل آن در پوشه‌ی `logs` کنار برنامه‌ی نصب‌شده ذخیره
  می‌شود. تنظیم رضایت در `%LOCALAPPDATA%\AirClick\preferences.json` نگهداری
  می‌شود.
- برای استفاده از برنامه باید اجازه‌ی دسترسی به دوربین را در Windows فعال کنید.

برای گزارش باگ یا پرسش درباره‌ی حریم خصوصی:

- GitHub: https://github.com/AMIasakri/AirClick
- Email: amir.as.7257@gmail.com

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
Setup برای این پوشه مجوز نوشتن کاربر فعلی را تنظیم می‌کند تا اجرای عادی
برنامه به دسترسی Administrator نیاز نداشته باشد.
هنگام حذف برنامه، پوشه لاگ و انتخاب رضایت ذخیره‌شده نیز حذف می‌شوند؛ بنابراین
نصب بعدی مانند نصب تازه شروع می‌شود.

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
- `p` — توقف/ادامه کنترل موس (Pause)

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

1. Python `3.14.7` نسخه‌ی 64 بیتی و [Inno Setup](https://jrsoftware.org/isinfo.php) را نصب کن.
2. PowerShell را در ریشه‌ی پروژه باز کن و محیط Build مستقل را بساز:

```powershell
python --version
python -m venv .release-venv
$env:PYTHONPATH = ''
$env:PIP_CONFIG_FILE = 'NUL'
& .\.release-venv\Scripts\python.exe -m pip --isolated install -r .\requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
.\packaging\build_installer.ps1
```

اسکریپت Build فقط از `.release-venv` استفاده می‌کند و نسخه‌ی Python را بررسی
می‌کند. برای ساخت فقط نسخه‌ی اجرایی بدون نصب‌کننده، دستور آخر را این‌طور اجرا کن:

```powershell
.\packaging\build_installer.ps1 -SkipInstaller
```

فایل نصب در `dist/installer/AirClick-Setup-1.0.0.exe` ساخته می‌شود.

## حذف برنامه در Windows

پس از نصب، AirClick را از یکی از این مسیرها حذف کن:

- منوی Start: پوشه‌ی **AirClick** → **Uninstall AirClick**
- **Settings → Apps → Installed apps** → **AirClick** → **Uninstall**

پوشه‌ی نصب را پیش از اجرای Uninstaller دستی حذف نکن؛ فایل‌های Uninstaller و
اطلاعات حذف داخل همان پوشه قرار دارند.
