# AirClick Pro

**Two-hand, webcam-based mouse control for Windows.** AirClick tracks hand
landmarks locally and maps configurable hand gestures to real mouse movement,
clicking, dragging, and scrolling.

**کنترل موس با وب‌کم و دو دست در Windows.** AirClick نقاط دست را به‌صورت محلی
ردیابی می‌کند و حرکت موس، کلیک، کشیدن و اسکرول را به ژست‌های دست پیوند می‌دهد.

> [English](#english) · [فارسی](#فارسی) · [Changelog](CHANGELOG.md) ·
> [Third-party notices](THIRD_PARTY_NOTICES.md) · [License](LICENSE)

> **Release status / وضعیت انتشار:** The application code is MIT-licensed, but
> the redistribution terms for the bundled Hand Landmarker model have not yet
> been authoritatively confirmed. See [Licensing](#licensing-and-model-rights)
> before redistributing a build that contains the model.
>
> کد خود برنامه تحت MIT است، اما مجوز توزیع مدل Hand Landmarker همراه برنامه
> هنوز به‌طور رسمی تأیید نشده است. پیش از بازتوزیع نسخه‌ی دارای مدل، بخش
> [مجوزها](#مجوزها-و-حقوق-مدل) را ببینید.

---

## English

### Overview

AirClick is a Windows accessibility/input-control application that turns a
webcam into a hands-free mouse interface. One hand controls pointer movement
and dragging; the other performs clicking and scrolling. Hand tracking runs
with MediaPipe, and mouse input is sent through PyAutoGUI.

AirClick analyzes the live camera image locally. Camera frames, landmarks, and
gestures are not sent to AirClick servers.

### What makes AirClick distinctive

| Feature | Details |
| --- | --- |
| Two-hand control | Assigns separate pointer and click roles using hand position and role memory |
| Hand landmark tracking | Uses MediaPipe Hand Landmarker for on-device hand tracking |
| Real mouse input | Relative pointer movement, drag, left/right/middle click, double-click, and scroll |
| Gesture stabilization | Requires a gesture to persist across consecutive frames before activating a click |
| Safety pause | `p` pauses/resumes mouse control; `q` or `Esc` exits |
| Visual feedback | Webcam preview, hand boxes, gesture state, control mode, and FPS |
| Performance diagnostics | `d` displays rolling two-second averages for camera, model, app logic, and overlay |
| Offline after installation | The model is bundled in Setup; the installed app does not need internet to load it |
| Consent-based logs | Optional first-run consent, with a 512 KiB size limit |
| Windows installer | Setup with Start Menu and desktop shortcuts, destination selection, and an uninstaller |

These describe the current implementation; they are not claims of guaranteed
recognition accuracy or frame rate. FPS depends on the camera, lighting, hand
distance, and available processing power.

### Gesture map

> AirClick sends real mouse input. Try gestures in a non-sensitive environment
> first. Press `p` to pause mouse control immediately if needed.

| Hand | Gesture | Action |
| --- | --- | --- |
| Pointer hand | Index finger extended by itself | Move the pointer |
| Pointer hand | Index and middle fingers extended | Start/continue dragging |
| Click hand | Index folded, middle extended | Left click |
| Click hand | Index extended, middle folded | Right click |
| Click hand | Fist | Middle click |
| Click hand | Index and middle folded | Double-click |
| Click hand | Ring finger folded while the other main fingers are extended | Scroll |

Keep hands inside the camera view and use adequate lighting. Mouse input is
blocked when the hands are too close together to avoid confusing their roles.

### Keyboard shortcuts

| Key | Action |
| --- | --- |
| `p` | Pause/resume mouse control without closing the app |
| `h` | Open the gesture help window |
| `d` | Show/hide the debug panel |
| `q` or `Esc` | Exit |

When enabled, the debug panel shows rolling two-second averages:

| Metric | Meaning |
| --- | --- |
| `Camera avg` | Time spent reading a webcam frame |
| `Model avg` | Hand-model inference time |
| `App avg` | Application logic and mouse-control time |
| `Overlay avg` | Visual overlay rendering time |

The FPS display reports recent processing throughput. It is not artificially
clamped to a minimum and will vary with the device and runtime conditions.

### Requirements and supported systems

| Item | Requirement |
| --- | --- |
| Official operating system | Windows 11 x64 |
| Best-effort compatibility | Windows 10 22H2 x64; not guaranteed. Standard Windows 10 support ended on October 14, 2025. |
| Camera | Working webcam and Windows Camera permission |
| Recommended resolution | 640×480 or higher; the app currently opens camera index `0` |
| Hands | Up to two hands per frame |
| Internet for Setup build | Not required for normal use or model loading |
| Python for Setup build | Not required |
| Installation permission | Setup may request Administrator approval for a system installation; run the app as a regular user |

Windows 11 is the officially supported OS. Windows 10 is best-effort only and
has reached end of support; see Microsoft's
[Windows 10 lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/windows-10-home-and-pro).

### Download and install

1. Open the [GitHub Releases page](https://github.com/AMIasakri/AirClick/releases).
2. Download and run `AirClick-Setup-<version>.exe` from the desired release.
3. Approve the Windows installation prompt if requested.
4. Choose a destination on the **Select Destination Location** page. On
   reinstall, the previous install path is suggested by default.
5. Launch AirClick from the Start Menu or desktop shortcut. Administrator
   privileges are not required for normal use.

Verify the downloaded file's SHA-256 against the value published with that
same release. The repository's `SHA256SUMS.txt` records the checksum for the
currently prepared Setup; each release should publish the checksum matching
its own installer.

### Run from source

Running from source requires Python and an internet connection for the initial
model download if `hand_landmarker.task` is missing. From Windows PowerShell in
the repository root:

```powershell
python -m venv .venv
$env:PYTHONPATH = ''
$env:PIP_CONFIG_FILE = 'NUL'
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
& .\.venv\Scripts\python.exe .\main.py
```

If `hand_landmarker.task` is absent from the project root, the source version
downloads it from the official model URL hosted on Google Cloud. Only download
models from sources you trust, and review [model rights](#licensing-and-model-rights)
before redistributing one.

### Privacy and data handling

| Topic | Behavior |
| --- | --- |
| Image processing | Local to the device |
| Camera frames sent to AirClick | None |
| Webcam images written to disk | None |
| Model in Setup | Bundled with the application |
| Model in source runs | Downloaded from the official MediaPipe source if missing |
| Logging | Optional; first-run consent prompt |
| Log contents | Status and error messages; no camera images |
| Log size | Limited to 512 KiB |
| Installed-app log path | `logs` directory beside the executable |
| Consent preference | `%LOCALAPPDATA%\AirClick\preferences.json` |
| Data removal | The uninstaller removes application logs and the saved consent preference |

Enable Camera access for desktop apps in Windows. Logging is optional, and
the saved choice is respected on subsequent launches.

### Troubleshooting

| Problem | Suggested action |
| --- | --- |
| Camera not found or already in use | Close Camera, Teams, Zoom, and browser apps; check Windows Camera permissions and test the webcam with Windows Camera. AirClick currently uses camera index `0`. |
| Model or tracking engine fails to start | Uninstall and reinstall the Setup to restore installed files. For source runs, check internet access and `hand_landmarker.task`. |
| Log-consent prompt does not reappear | The previous choice is stored in `%LOCALAPPDATA%\AirClick\preferences.json`. Uninstalling removes the saved choice. |
| Uninstall error | Do not manually delete the install directory. Use Start → AirClick → Uninstall or Settings → Apps → Installed apps. |
| Low or variable FPS | Press `d` and inspect camera, model, app-logic, and overlay averages. Lighting, camera resolution, and device performance affect throughput. |
| Need support | Include the full error, Windows version, and—if you opted into logging—`logs\airclick.log`. |

### Project layout

```text
AirClick/
├── config/
│   ├── settings.py             # Camera, hand, mouse, and display settings
│   └── version.py              # Application version
├── core/
│   ├── hand_tracker.py         # Model and hand tracking
│   ├── gesture_recognizer.py   # Gesture recognition and stabilization
│   └── mouse_controller.py    # Real mouse input
├── ui/
│   └── overlay.py              # Camera preview and HUD
├── utils/
│   └── helpers.py              # Logging, FPS, and shared helpers
├── packaging/
│   ├── AirClick.iss            # Inno Setup configuration
│   ├── AirClick.spec           # PyInstaller configuration
│   └── build_installer.ps1     # Windows release build
├── tests/                      # Unit and release-layout tests
├── hand_landmarker.task        # MediaPipe model
├── main.py                     # Application entry point
└── requirements*.txt           # Dependencies and pinned versions
```

### Tests

Run the unit and release-layout tests with Python:

```powershell
python .\tests\test_gestures.py
python .\tests\test_hand_tracker.py
python .\tests\test_mouse_controller.py
python .\tests\test_settings.py
python .\tests\test_helpers.py
python .\tests\test_overlay.py
python .\tests\test_release_layout.py
```

The setup smoke test also checks a real camera and model. Ensure camera access
is available before running it:

```powershell
python .\test_setup.py
```

### Build the Windows release

The pinned Windows x64 release build uses Python `3.14.7` and Inno Setup. From
PowerShell at the repository root:

```powershell
python -m venv .release-venv
$env:PYTHONPATH = ''
$env:PIP_CONFIG_FILE = 'NUL'
& .\.release-venv\Scripts\python.exe -m pip --isolated install -r .\requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
.\packaging\build_installer.ps1
```

Build outputs:

| File | Purpose |
| --- | --- |
| `dist\AirClick.exe` | Standalone executable built with PyInstaller |
| `dist\installer\AirClick-Setup-<version>.exe` | Inno Setup installer |

To build only the executable and skip the installer:

```powershell
.\packaging\build_installer.ps1 -SkipInstaller
```

The canonical version is defined in `config/version.py`; the app, Inno Setup,
and installer filename use that value. Keep the Git tag and GitHub Release
version aligned with it.

### Install and uninstall

The installer lets users select an installation directory and creates Start
Menu and desktop shortcuts. The shortcuts use the icon bundled with the Setup.

Uninstall AirClick using either route:

| Location | Steps |
| --- | --- |
| Start Menu | AirClick → Uninstall AirClick |
| Windows Settings | Settings → Apps → Installed apps → AirClick → Uninstall |
| Start Menu folder | AirClick → Uninstall AirClick |

Do not delete the install directory before running the uninstaller: the
uninstaller files are stored there. After a complete uninstall, Setup can be
run again to reinstall the application.

### Licensing and model rights

| Component | Status |
| --- | --- |
| AirClick application code | MIT; see [LICENSE](LICENSE) |
| Direct dependencies | Individually licensed; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) |
| Current application icon | Original AirClick artwork |
| `hand_landmarker.task` model | Obtained from the official MediaPipe URL; redistribution terms for this exact binary have not yet been authoritatively confirmed |

The repository's MIT license does not change the terms for models or
third-party libraries. The official Hand Landmarker guide and model card
describe the model but do not explicitly identify the license for this binary.
**Do not assume the model's redistribution rights are confirmed.** Obtain
authoritative clarification covering this exact asset before publishing a
Setup or source package that redistributes it.

- Model URL: [Google Cloud Storage](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task)
- SHA-256 of the model in this repository: `fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1`
- Model documentation: [MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
- Third-party notices: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

A MediaPipe maintainer answered that a specific **Pose Landmarker** task bundle
is Apache 2.0 in
[google-ai-edge/mediapipe#6306](https://github.com/google-ai-edge/mediapipe/issues/6306).
That answer concerns a different model and does not establish the license of
this project's Hand Landmarker asset.

### Contact and support

- Repository: [AMIasakri/AirClick](https://github.com/AMIasakri/AirClick)
- Support and bug reports: [amir.as.7257@gmail.com](mailto:amir.as.7257@gmail.com)
- Changes by version: [CHANGELOG.md](CHANGELOG.md)
- Release readiness: [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)

---

## فارسی

### معرفی

AirClick یک برنامه‌ی دسترس‌پذیری/کنترل ورودی برای Windows است که وب‌کم را به
وسیله‌ی کنترل موس تبدیل می‌کند. یک دست برای حرکت و Drag و دست دیگر برای کلیک و
اسکرول استفاده می‌شود. تشخیص دست با MediaPipe و ارسال ورودی واقعی موس با
PyAutoGUI انجام می‌شود.

AirClick به‌جای شبیه‌سازی صفحه‌لمسی یا کنترل از راه دور، حرکت‌های دست را در
تصویر زنده تحلیل می‌کند؛ مختصات، ژست و فریم‌های وب‌کم برای پردازش به سرور
AirClick فرستاده نمی‌شوند.

### ویژگی‌های شاخص

| ویژگی | توضیح |
| --- | --- |
| کنترل دو‌دستی | تفکیک نقش «دست موس» و «دست کلیک» بر اساس موقعیت دست‌ها و حافظه‌ی نقش‌ها |
| ردیابی نقاط دست | استفاده از Hand Landmarker برای تشخیص لندمارک‌های دست روی دستگاه |
| کنترل موس واقعی | حرکت نسبی موس، Drag، کلیک چپ/راست/وسط، دابل‌کلیک و اسکرول |
| پایدارسازی ژست | ژست باید در چند فریم متوالی پایدار بماند تا عمل کلیک فعال شود |
| توقف امن | کلید `p` کنترل موس را موقتاً متوقف/ازسرگیری می‌کند؛ `q` یا `Esc` برنامه را می‌بندد |
| بازخورد دیداری | پیش‌نمایش وب‌کم، کادر دست‌ها، وضعیت ژست، حالت کنترل و FPS |
| دیباگ عملکرد | کلید `d` میانگین لغزان دوثانیه‌ای زمان دوربین، مدل، منطق برنامه و رندر را نشان می‌دهد |
| کارکرد آفلاین پس از نصب | مدل در Setup قرار دارد؛ اجرای نسخه‌ی نصب‌شده برای دریافت مدل به اینترنت نیاز ندارد |
| لاگ با رضایت کاربر | ذخیره‌ی لاگ اختیاری است، با پرسش بار اول و سقف ۵۱۲ کیلوبایت |
| نصب‌کننده‌ی Windows | Setup با میان‌بر دسکتاپ و Start Menu، انتخاب مسیر نصب و Uninstaller |

این موارد توصیف قابلیت‌های فعلی‌اند، نه ادعای دقت تشخیص یا سرعت تضمین‌شده.
FPS به دوربین، نور، فاصله‌ی دست و توان پردازشی دستگاه بستگی دارد.

### نگاشت ژست‌ها

> AirClick کلیک‌ها و حرکت‌های واقعی موس را ارسال می‌کند. ابتدا ژست‌ها را در
> محیطی غیرحساس امتحان کنید. در صورت نیاز فوراً `p` را برای توقف کنترل موس بزنید.

| دست | ژست | عمل |
| --- | --- | --- |
| دست موس | فقط انگشت اشاره باز | حرکت موس |
| دست موس | اشاره و انگشت وسط باز | شروع/ادامه‌ی Drag |
| دست کلیک | انگشت اشاره خم، انگشت وسط باز | کلیک چپ |
| دست کلیک | اشاره باز، انگشت وسط خم | کلیک راست |
| دست کلیک | مشت | کلیک وسط |
| دست کلیک | اشاره و انگشت وسط خم | دابل‌کلیک |
| دست کلیک | انگشت حلقه خم و سایر انگشتان اصلی باز | اسکرول |

برای اجرای عمل، دست‌ها را در محدوده‌ی تصویر نگه دارید و نور کافی فراهم کنید.
اگر دست‌ها بیش از حد به هم نزدیک شوند، ورودی مسدود می‌شود تا نقش‌ها با هم
اشتباه نشوند.

### کلیدهای میان‌بر

| کلید | کار |
| --- | --- |
| `p` | توقف/ادامه‌ی کنترل موس، بدون بستن برنامه |
| `h` | نمایش راهنمای ژست‌ها |
| `d` | نمایش/پنهان‌کردن پنل دیباگ |
| `q` یا `Esc` | خروج از برنامه |

پنل دیباگ، در صورت روشن‌بودن، این میانگین‌های دوثانیه‌ای را نشان می‌دهد:

| مقدار | معنی |
| --- | --- |
| `Camera avg` | زمان خواندن فریم از وب‌کم |
| `Model avg` | زمان اجرای مدل تشخیص دست |
| `App avg` | زمان منطق برنامه و کنترل موس |
| `Overlay avg` | زمان رسم لایه‌ی دیداری |

عدد FPS نرخ اخیر پردازش فریم‌ها را نشان می‌دهد؛ مقدار آن به‌صورت مصنوعی روی
حداقل ثابتی قفل نمی‌شود و با سخت‌افزار و شرایط اجرا تغییر می‌کند.

### پیش‌نیازها و سیستم‌عامل

| مورد | نیاز |
| --- | --- |
| سیستم‌عامل رسمی | Windows 11 نسخه‌ی ۶۴ بیتی (x64) |
| پشتیبانی best-effort | Windows 10 نسخه‌ی 22H2 x64؛ بدون تضمین. پشتیبانی عادی Windows 10 در ۱۴ اکتبر ۲۰۲۵ پایان یافته است. |
| دوربین | وب‌کم فعال و مجوز دسترسی Camera در Windows |
| رزولوشن پیشنهادی | حداقل 640×480؛ برنامه در حال حاضر دوربین شماره‌ی `0` را باز می‌کند |
| دست‌ها | حداکثر دو دست در هر فریم |
| اینترنت در نسخه‌ی Setup | برای استفاده‌ی عادی یا دریافت مدل لازم نیست |
| Python برای نسخه‌ی Setup | لازم نیست |
| مجوز نصب | برای نصب در مسیر سیستمی، Setup ممکن است تأیید Administrator بخواهد؛ برنامه را روزمره با حساب عادی اجرا کنید |

> پشتیبانی رسمی Windows 11 است. Windows 10 صرفاً به‌صورت best-effort ذکر شده و
> پشتیبانی آن از سوی Microsoft پایان یافته است؛ [چرخه‌ی عمر Windows 10 در
> Microsoft](https://learn.microsoft.com/en-us/lifecycle/products/windows-10-home-and-pro).

### دانلود و نصب

1. به صفحه‌ی [GitHub Releases](https://github.com/AMIasakri/AirClick/releases) بروید.
2. فایل `AirClick-Setup-<version>.exe` را از Release انتخاب و اجرا کنید.
3. در صورت نیاز، درخواست مجوز نصب Windows را تأیید کنید.
4. در صفحه‌ی **Select Destination Location** مسیر نصب را انتخاب کنید؛ هنگام
   نصب مجدد مسیر نصب قبلی به‌عنوان پیش‌فرض پیشنهاد می‌شود.
5. AirClick را از میان‌بر Start یا دسکتاپ اجرا کنید. برای استفاده‌ی روزانه
   نیازی به اجرای Administrator نیست.

برای بررسی صحت فایل دانلودی، SHA-256 را با مقدار منتشرشده در همان GitHub Release
مقایسه کنید. مخزن فایل `SHA256SUMS.txt` را برای Setup فعلی نگه می‌دارد؛ هر انتشار
باید checksum مربوط به همان فایل Setup را همراه خود منتشر کند.

### اجرای نسخه‌ی سورس

برای اجرای سورس به Python و اینترنت در اولین دریافت مدل نیاز است. از Windows
PowerShell در ریشه‌ی پروژه:

```powershell
python -m venv .venv
$env:PYTHONPATH = ''
$env:PIP_CONFIG_FILE = 'NUL'
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
& .\.venv\Scripts\python.exe .\main.py
```

اگر فایل `hand_landmarker.task` در ریشه‌ی پروژه موجود نباشد، نسخه‌ی سورس آن را
از URL رسمی مدل در Google Cloud دریافت می‌کند. دریافت مدل را فقط از منبع مورد
اعتماد انجام دهید و بخش [حقوق مدل](#مجوزها-و-حقوق-مدل) را پیش از بازتوزیع
بررسی کنید.

### حریم خصوصی و داده‌ها

| موضوع | رفتار |
| --- | --- |
| پردازش تصویر | روی همان دستگاه و به‌صورت محلی |
| ارسال فریم/تصویر به AirClick | انجام نمی‌شود |
| ذخیره‌ی تصویر وب‌کم | انجام نمی‌شود |
| مدل در نسخه‌ی Setup | همراه برنامه نصب می‌شود |
| مدل در اجرای سورس | اگر غایب باشد، از منبع رسمی MediaPipe دانلود می‌شود |
| ثبت لاگ | اختیاری؛ در اولین اجرا با پرسش رضایت |
| محتوای لاگ | پیام‌های وضعیت و خطا؛ تصویر دوربین در لاگ ذخیره نمی‌شود |
| اندازه‌ی لاگ | حداکثر ۵۱۲ کیلوبایت |
| محل لاگ نصب‌شده | پوشه‌ی `logs` کنار فایل اجرایی |
| محل تنظیم رضایت | `%LOCALAPPDATA%\AirClick\preferences.json` |
| حذف داده‌های AirClick | Uninstaller لاگ برنامه و فایل رضایت را پاک می‌کند |

برای استفاده باید مجوز Camera را برای برنامه‌های دسکتاپ در Windows فعال کنید.
انتخاب ذخیره‌ی لاگ اختیاری است و انتخاب کاربر در اجرای بعدی رعایت می‌شود.

### عیب‌یابی

| مشکل | راهکار |
| --- | --- |
| دوربین پیدا نمی‌شود یا در حال استفاده است | Camera، Teams، Zoom و برنامه‌های مرورگر را ببندید؛ مجوز Camera ویندوز و وب‌کم را در Windows Camera بررسی کنید. برنامه فعلاً دوربین شماره‌ی `0` را استفاده می‌کند. |
| موتور تشخیص یا مدل راه‌اندازی نمی‌شود | نسخه‌ی Setup را حذف و دوباره نصب کنید تا فایل‌های نصب ترمیم شوند. در اجرای سورس، اتصال اینترنت و وجود `hand_landmarker.task` را بررسی کنید. |
| درخواست ذخیره‌ی لاگ دوباره ظاهر نمی‌شود | تصمیم قبلی در `%LOCALAPPDATA%\AirClick\preferences.json` ذخیره می‌شود. Uninstall تنظیم رضایت را پاک می‌کند. |
| Uninstall خطا می‌دهد | پوشه‌ی نصب را دستی پاک نکنید. از Start → AirClick → Uninstall یا Settings → Apps → Installed apps استفاده کنید. |
| FPS یا پاسخ‌گویی پایین است | با `d` زمان‌های میانگین دوربین، مدل، منطق برنامه و رندر را ببینید. نور، وضوح دوربین و توان دستگاه روی سرعت اثر دارند. |
| نیاز به پشتیبانی دارید | متن کامل خطا، نسخه‌ی Windows و در صورت رضایت، فایل `logs\airclick.log` را همراه گزارش ارسال کنید. |

### ساختار پروژه

```text
AirClick/
├── config/
│   ├── settings.py             # تنظیمات دوربین، دست، موس و نمایش
│   └── version.py              # شماره نسخه‌ی برنامه
├── core/
│   ├── hand_tracker.py         # مدل و ردیابی دست‌ها
│   ├── gesture_recognizer.py   # تشخیص و پایدارسازی ژست‌ها
│   └── mouse_controller.py    # ورودی‌های واقعی موس
├── ui/
│   └── overlay.py              # پیش‌نمایش و HUD
├── utils/
│   └── helpers.py              # لاگ، FPS و ابزارهای مشترک
├── packaging/
│   ├── AirClick.iss            # تنظیمات Inno Setup
│   ├── AirClick.spec           # تنظیمات PyInstaller
│   └── build_installer.ps1     # Build نسخه‌ی Windows
├── tests/                      # تست‌های واحد و چیدمان انتشار
├── hand_landmarker.task        # مدل MediaPipe
├── main.py                     # نقطه‌ی ورود برنامه
└── requirements*.txt           # وابستگی‌ها و نسخه‌های قفل‌شده
```

### تست‌ها

تست‌های واحد را در PowerShell و با Python نصب‌شده اجرا کنید:

```powershell
python .\tests\test_gestures.py
python .\tests\test_hand_tracker.py
python .\tests\test_mouse_controller.py
python .\tests\test_settings.py
python .\tests\test_helpers.py
python .\tests\test_overlay.py
python .\tests\test_release_layout.py
```

تست راه‌اندازی زیر دوربین و مدل واقعی را نیز بررسی می‌کند؛ قبل از اجرا مطمئن
شوید دسترسی دوربین آزاد است:

```powershell
python .\test_setup.py
```

### ساخت نسخه‌ی Windows

Build قفل‌شده برای Windows x64 با Python `3.14.7` و Inno Setup ساخته می‌شود.
از PowerShell در ریشه‌ی مخزن:

```powershell
python -m venv .release-venv
$env:PYTHONPATH = ''
$env:PIP_CONFIG_FILE = 'NUL'
& .\.release-venv\Scripts\python.exe -m pip --isolated install -r .\requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
.\packaging\build_installer.ps1
```

خروجی‌ها:

| فایل | کاربرد |
| --- | --- |
| `dist\AirClick.exe` | برنامه‌ی اجرایی مستقل ساخته‌شده با PyInstaller |
| `dist\installer\AirClick-Setup-<version>.exe` | نصب‌کننده‌ی Inno Setup |

برای ساخت فقط EXE و صرف‌نظر از نصب‌کننده:

```powershell
.\packaging\build_installer.ps1 -SkipInstaller
```

شماره‌ی نسخه فقط در `config/version.py` تعریف می‌شود؛ برنامه، Inno Setup و نام
فایل نصب از همان نسخه استفاده می‌کنند. برای انتشار، Tag و نام GitHub Release
باید با همان نسخه هماهنگ شوند.

### نصب و حذف

Setup امکان انتخاب مسیر نصب را دارد و میان‌برهای AirClick را در Start Menu و
دسکتاپ می‌سازد. آیکن میان‌بر از فایل آیکن داخل Setup گرفته می‌شود.

برای حذف، یکی از این مسیرها را استفاده کنید:

| مسیر | روش |
| --- | --- |
| Start Menu | AirClick → Uninstall AirClick |
| تنظیمات Windows | Settings → Apps → Installed apps → AirClick → Uninstall |
| پوشه‌ی منوی Start | AirClick → Uninstall AirClick |

پوشه‌ی نصب را پیش از Uninstall دستی حذف نکنید؛ فایل‌های Uninstaller داخل همان
مسیر قرار دارند. پس از حذف کامل، نصب دوباره با Setup امکان‌پذیر است.

### مجوزها و حقوق مدل

| جزء | وضعیت |
| --- | --- |
| کد AirClick | MIT؛ متن کامل در [LICENSE](LICENSE) |
| وابستگی‌های مستقیم | هرکدام تحت مجوز مستقل؛ فهرست و پیوندها در [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) |
| آیکن فعلی | artwork اختصاصی AirClick |
| مدل `hand_landmarker.task` | از نشانی رسمی MediaPipe دریافت شده؛ مجوز بازتوزیع همین فایل باینری هنوز به‌طور رسمی تأیید نشده است |

مجوز MIT مخزن به‌تنهایی مجوز مدل یا کتابخانه‌های شخص ثالث را تغییر نمی‌دهد.
راهنمای رسمی Hand Landmarker و Model Card، خود مدل را توصیف می‌کنند اما مجوز
صریح این فایل مدل را مشخص نمی‌کنند. بنابراین **مجوز مدل را تأییدشده فرض نکنید**
و برای انتشار عمومی Setup/بسته‌ای که مدل را دربر دارد، ابتدا پاسخ رسمی درباره‌ی
مجوز همین asset را دریافت کنید.

- URL مدل: [Google Cloud Storage](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task)
- SHA-256 مدل داخل مخزن: `fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1`
- اسناد مدل: [MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
- اعلان‌های شخص ثالث: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

یک پاسخ نگه‌دارنده‌ی MediaPipe درباره‌ی مجوز یک مدل **Pose Landmarker** مشخص در
[google-ai-edge/mediapipe#6306](https://github.com/google-ai-edge/mediapipe/issues/6306)
وجود دارد؛ آن پاسخ درباره‌ی مدل متفاوتی است و مجوز مدل Hand Landmarker این
پروژه را اثبات نمی‌کند.

### ارتباط و گزارش مشکل

- مخزن: [AMIasakri/AirClick](https://github.com/AMIasakri/AirClick)
- پشتیبانی و گزارش باگ: [amir.as.7257@gmail.com](mailto:amir.as.7257@gmail.com)
- تغییرات نسخه‌ها: [CHANGELOG.md](CHANGELOG.md)
- چک‌لیست آمادگی انتشار: [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)
