<div align="center">

# 🖱️ AirClick Pro

### Control your Windows mouse with your hands — using only a webcam.
### موس ویندوز را فقط با دست‌هایتان و یک وب‌کم کنترل کنید.

![Platform](https://img.shields.io/badge/platform-Windows%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/built%20with-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/tracking-MediaPipe-FF6F00?style=for-the-badge)

**[English](#-english) · [فارسی](#-فارسی)**

<br>

### ⬇️ [Download AirClick Setup 1.0.0 / دانلود نصب‌کننده AirClick نسخه 1.0.0](https://github.com/AMIasakri/AirClick/releases/download/v1.0.0/AirClick-Setup-1.0.0.exe)

<br>

⭐ **If you like AirClick, please give it a star!** ⭐
<br>
⭐ **اگر AirClick را دوست داشتید، لطفاً به آن ستاره بدهید!** ⭐

</div>

---

# 🇬🇧 English

## 📖 About

**AirClick** is a Windows application that turns your webcam into a hands-free mouse. One hand moves the pointer and drags; the other clicks and scrolls. Everything is processed **locally on your computer** — your camera images are never uploaded anywhere.

> 👨‍💻 **This entire project was designed and developed solely by Amir Askari.**

## ✨ What makes AirClick special

| Feature | Details |
| --- | --- |
| 🙌 **Two-hand control** | Separate "pointer hand" and "click hand" roles, assigned by hand position and role memory |
| 🧠 **On-device hand tracking** | Uses the MediaPipe Hand Landmarker — no cloud, no server |
| 🖱️ **Real mouse input** | Pointer movement, drag, left / right / middle click, double-click and scroll (via PyAutoGUI) |
| 🎯 **Gesture stabilization** | A gesture must stay steady for several frames before it counts — fewer accidental clicks |
| ⏸️ **Instant safety pause** | Press `P` to pause or resume control at any moment |
| 👀 **Live visual feedback** | Camera preview, hand boxes, current gesture, control mode and FPS |
| 📊 **Performance diagnostics** | Press `D` for rolling 2-second averages of camera, model, app logic and overlay time |
| 📴 **Works offline** | The model is bundled inside the installer — no internet needed after installing |
| 🔒 **Privacy first** | No camera frames sent or saved; logging is optional and asks for your consent |
| 📦 **Professional installer** | Choose your install folder, Start Menu + desktop shortcuts, and a clean uninstaller |
| 🧪 **Tested** | Unit tests for gestures, tracking, mouse control, settings, helpers and overlay |

## 📥 Download & Install (no coding needed!)

You do **not** need to download the source code, install Python, or know anything about GitHub. Just get the installer:

### Step by step

1. **Download the installer:** 👉 [AirClick-Setup-1.0.0.exe](https://github.com/AMIasakri/AirClick/releases/download/v1.0.0/AirClick-Setup-1.0.0.exe) (or open the [v1.0.0 release page](https://github.com/AMIasakri/AirClick/releases/tag/v1.0.0)).
2. Wait for the download to finish, then **double-click** the downloaded `.exe`.
3. If Windows shows a blue **"Windows protected your PC"** screen, click **More info → Run anyway**. (This appears for most small independent apps that are not commercially code-signed.)
4. Follow the installer: choose a folder (or keep the default) and click **Install**.
5. Open **AirClick** from the **Start Menu** or the **desktop shortcut**. Done! 🎉

> 💡 **Tip:** Allow camera access for desktop apps in *Windows Settings → Privacy & security → Camera*.

### System requirements

| Item | Requirement |
| --- | --- |
| Operating system | **Windows 11 (64-bit)** — officially supported |
| Windows 10 | 22H2 64-bit, best-effort only (not guaranteed) |
| Camera | Any working webcam (640×480 or higher recommended) |
| Internet | Not required |
| Python | Not required |

## 🖐️ Gesture guide

> ⚠️ AirClick controls your **real** mouse. Try it first in a safe place, and press `P` to pause at any time.

| Hand | Gesture | Action |
| --- | --- | --- |
| Pointer hand | Only the index finger up | Move the pointer |
| Pointer hand | Index + middle fingers up | Drag |
| Click hand | Index folded, middle up | Left click |
| Click hand | Index up, middle folded | Right click |
| Click hand | Fist | Middle click |
| Click hand | Index + middle folded | Double-click |
| Click hand | Ring finger folded, other main fingers up | Scroll |

Keep both hands inside the camera view with good lighting. Mouse input is blocked if your hands get too close together, so their roles don't get mixed up.

## ⌨️ Keyboard shortcuts

| Key | Action |
| --- | --- |
| `P` | Pause / resume mouse control |
| `H` | Open the gesture help window |
| `D` | Show / hide the debug panel |
| `Q` or `Esc` | Exit |

## 🛠️ Troubleshooting

| Problem | Try this |
| --- | --- |
| Camera not found / in use | Close Zoom, Teams, browsers or the Camera app; check Windows camera permission |
| App won't start | Uninstall and reinstall using the Setup file |
| Low or unstable FPS | Improve lighting, press `D` to see what is slow |
| Can't uninstall | Use *Start Menu → AirClick → Uninstall* or *Settings → Apps*. Don't delete the folder manually |

## 🔐 Privacy

- All image processing happens on your device.
- No camera frames are sent to anyone or saved to disk.
- Logging is **optional** and only starts if you agree (limited to 512 KiB, no images).
- The uninstaller removes logs and your saved preferences.

## 📜 License

- AirClick's own code is released under the **[MIT License](LICENSE)**.
- Third-party libraries keep their own licenses — see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- The bundled `hand_landmarker.task` model comes from Google's official MediaPipe source. Its exact redistribution terms have **not yet been officially confirmed**, so check before redistributing a package that contains it.

## 🧑‍💻 For developers (optional)

<details>
<summary>Run from source</summary>

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
& .\.venv\Scripts\python.exe .\main.py
```

Build the Windows installer:

```powershell
python -m venv .release-venv
& .\.release-venv\Scripts\python.exe -m pip --isolated install -r .\requirements-lock.txt
.\packaging\build_installer.ps1
```

Output: `dist\AirClick.exe` and `dist\installer\AirClick-Setup-<version>.exe`

</details>

## 📬 Contact & support

- 📧 **Email:** amir.as.7257@gmail.com
- 📝 [Changelog](CHANGELOG.md)

## ⭐ Support the project

If AirClick helped you, **please click the ⭐ Star button at the top of this page** — it's free, takes one second, and helps others discover the project. Thank you!

---

<div dir="rtl">

# 🇮🇷 فارسی

## 📖 معرفی

**AirClick** یک برنامه‌ی ویندوز است که وب‌کم شما را به یک موس بدون‌دست‌زدن تبدیل می‌کند. یک دست حرکت موس و کشیدن (Drag) را انجام می‌دهد و دست دیگر کلیک و اسکرول. تمام پردازش‌ها **روی خود کامپیوتر شما** انجام می‌شود و تصویر دوربین هرگز به جایی ارسال نمی‌شود.

> 👨‍💻 **کل این پروژه، از طراحی تا توسعه، توسط امیر عسکری ساخته شده است.**

## ✨ چه چیزی AirClick را متمایز می‌کند

| ویژگی | توضیح |
| --- | --- |
| 🙌 **کنترل دو‌دستی** | تفکیک نقش «دست موس» و «دست کلیک» بر اساس موقعیت دست‌ها و حافظه‌ی نقش‌ها |
| 🧠 **ردیابی دست روی خود دستگاه** | استفاده از MediaPipe Hand Landmarker، بدون سرور و بدون ابر |
| 🖱️ **ورودی واقعی موس** | حرکت، Drag، کلیک چپ / راست / وسط، دابل‌کلیک و اسکرول (با PyAutoGUI) |
| 🎯 **پایدارسازی ژست** | ژست باید چند فریم ثابت بماند تا ثبت شود؛ یعنی کلیک اشتباهی کمتر |
| ⏸️ **توقف فوری و امن** | با کلید `P` در هر لحظه کنترل را متوقف یا دوباره شروع کنید |
| 👀 **بازخورد زنده** | پیش‌نمایش دوربین، کادر دست‌ها، ژست فعلی، حالت کنترل و FPS |
| 📊 **پنل عملکرد** | با کلید `D` میانگین دوثانیه‌ای زمان دوربین، مدل، منطق برنامه و رسم را ببینید |
| 📴 **کارکرد آفلاین** | مدل داخل نصب‌کننده است؛ بعد از نصب به اینترنت نیاز ندارید |
| 🔒 **حریم خصوصی** | هیچ تصویری ارسال یا ذخیره نمی‌شود؛ ذخیره‌ی لاگ اختیاری و با رضایت شماست |
| 📦 **نصب‌کننده‌ی حرفه‌ای** | انتخاب پوشه‌ی نصب، میان‌بر Start Menu و دسکتاپ، و Uninstaller تمیز |
| 🧪 **تست‌شده** | تست واحد برای ژست‌ها، ردیابی، کنترل موس، تنظیمات و رابط |

## 📥 دانلود و نصب (بدون نیاز به دانش برنامه‌نویسی!)

**لازم نیست** کد پروژه را دانلود کنید، Python نصب کنید یا چیزی از گیت‌هاب بدانید. فقط فایل نصب‌کننده را بگیرید:

### مرحله به مرحله

1. **نصب‌کننده را دانلود کنید:** 👈 [AirClick-Setup-1.0.0.exe](https://github.com/AMIasakri/AirClick/releases/download/v1.0.0/AirClick-Setup-1.0.0.exe) (یا [صفحه‌ی انتشار نسخه‌ی 1.0.0](https://github.com/AMIasakri/AirClick/releases/tag/v1.0.0) را باز کنید).
2. صبر کنید دانلود تمام شود، سپس روی فایل دانلودشده **دوبار کلیک** کنید.
3. اگر ویندوز صفحه‌ی آبی **«Windows protected your PC»** نشان داد، روی **More info** و بعد **Run anyway** بزنید. (این پیام برای بیشتر برنامه‌های مستقل که امضای تجاری ندارند نمایش داده می‌شود.)
4. مراحل نصب را ادامه دهید: پوشه را انتخاب کنید (یا پیش‌فرض را بپذیرید) و **Install** را بزنید.
5. AirClick را از **Start Menu** یا **میان‌بر دسکتاپ** اجرا کنید. تمام! 🎉

> 💡 **نکته:** دسترسی دوربین برای برنامه‌های دسکتاپ را در *Settings → Privacy & security → Camera* فعال کنید.

### پیش‌نیازها

| مورد | نیاز |
| --- | --- |
| سیستم‌عامل | **Windows 11 (۶۴ بیتی)** — پشتیبانی رسمی |
| Windows 10 | نسخه‌ی 22H2 (۶۴ بیتی)، فقط به‌صورت تلاشی و بدون تضمین |
| دوربین | هر وب‌کم سالم (پیشنهاد: حداقل 640×480) |
| اینترنت | لازم نیست |
| Python | لازم نیست |

## 🖐️ راهنمای ژست‌ها

> ⚠️ AirClick موس **واقعی** شما را کنترل می‌کند. اول در محیطی امن امتحان کنید و هر زمان لازم شد `P` را بزنید.

| دست | ژست | عمل |
| --- | --- | --- |
| دست موس | فقط انگشت اشاره باز | حرکت موس |
| دست موس | اشاره + انگشت وسط باز | کشیدن (Drag) |
| دست کلیک | اشاره خم، وسط باز | کلیک چپ |
| دست کلیک | اشاره باز، وسط خم | کلیک راست |
| دست کلیک | مشت | کلیک وسط |
| دست کلیک | اشاره + وسط خم | دابل‌کلیک |
| دست کلیک | انگشت حلقه خم، بقیه‌ی انگشتان اصلی باز | اسکرول |

هر دو دست را داخل تصویر دوربین و در نور کافی نگه دارید. اگر دست‌ها خیلی به هم نزدیک شوند، ورودی موس مسدود می‌شود تا نقش‌ها اشتباه نشوند.

## ⌨️ کلیدهای میان‌بر

| کلید | کار |
| --- | --- |
| `P` | توقف / ادامه‌ی کنترل موس |
| `H` | نمایش راهنمای ژست‌ها |
| `D` | نمایش / پنهان‌کردن پنل دیباگ |
| `Q` یا `Esc` | خروج |

## 🛠️ عیب‌یابی

| مشکل | راه‌حل |
| --- | --- |
| دوربین پیدا نمی‌شود / مشغول است | Zoom، Teams، مرورگر یا برنامه‌ی Camera را ببندید؛ مجوز دوربین ویندوز را بررسی کنید |
| برنامه اجرا نمی‌شود | با فایل Setup حذف و دوباره نصب کنید |
| FPS پایین یا ناپایدار | نور را بهتر کنید، با `D` ببینید کدام بخش کند است |
| حذف برنامه خطا می‌دهد | از *Start Menu → AirClick → Uninstall* یا *Settings → Apps* استفاده کنید؛ پوشه را دستی پاک نکنید |

## 🔐 حریم خصوصی

- تمام پردازش تصویر روی دستگاه خودتان انجام می‌شود.
- هیچ فریمی از دوربین به جایی ارسال یا روی دیسک ذخیره نمی‌شود.
- ذخیره‌ی لاگ **اختیاری** است و فقط در صورت موافقت شما فعال می‌شود (حداکثر ۵۱۲ کیلوبایت، بدون تصویر).
- Uninstaller لاگ‌ها و تنظیمات ذخیره‌شده را پاک می‌کند.

## 📜 مجوز

- کد خود AirClick تحت **[مجوز MIT](LICENSE)** منتشر شده است.
- کتابخانه‌های شخص ثالث مجوز مخصوص خودشان را دارند؛ [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) را ببینید.
- مدل `hand_landmarker.task` از منبع رسمی MediaPipe گرفته شده و شرایط دقیق بازتوزیع آن **هنوز رسماً تأیید نشده** است؛ پیش از بازتوزیع بسته‌ای که شامل آن است، بررسی کنید.

## 🧑‍💻 برای توسعه‌دهندگان (اختیاری)

برای اجرای سورس و ساخت نسخه‌ی Windows، بخش **For developers** در قسمت انگلیسی بالا را ببینید.

## 📬 ارتباط و پشتیبانی

- 📧 **ایمیل:** amir.as.7257@gmail.com
- 📝 [تاریخچه‌ی تغییرات](CHANGELOG.md)

## ⭐ از پروژه حمایت کنید

اگر AirClick به کارتان آمد، **لطفاً دکمه‌ی ⭐ Star بالای همین صفحه را بزنید** — رایگان است، یک ثانیه طول می‌کشد و به دیده‌شدن پروژه کمک می‌کند. ممنون!

</div>

---

<div align="center">

Made with ❤️ by **Amir Askari** · ساخته‌شده با ❤️ توسط **امیر عسکری**

</div>
