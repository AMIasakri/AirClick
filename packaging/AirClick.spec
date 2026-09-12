# PyInstaller build configuration for the standalone AirClick application.

from pathlib import Path

from PyInstaller.utils.hooks import collect_all


project_root = Path.cwd()
main_script = project_root / 'main.py'
mediapipe_datas, mediapipe_binaries, mediapipe_hiddenimports = collect_all('mediapipe')


a = Analysis(
    [str(main_script)],
    pathex=[str(project_root)],
    binaries=mediapipe_binaries,
    datas=[
        (str(project_root / 'hand_landmarker.task'), '.'),
        *mediapipe_datas,
    ],
    hiddenimports=mediapipe_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AirClick',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
