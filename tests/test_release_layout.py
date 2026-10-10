"""Checks for files required by the Windows release package."""

import os
import re

from PIL import Image


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_project_version():
    version_path = os.path.join(PROJECT_ROOT, "config", "version.py")
    with open(version_path, encoding="utf-8") as version_file:
        contents = version_file.read()

    match = re.search(r'^APP_VERSION = "(\d+\.\d+\.\d+)"$', contents, re.MULTILINE)
    assert match, "config/version.py must define a semantic APP_VERSION"
    return match.group(1)


def test_release_files_exist():
    required = (
        "hand_landmarker.task",
        "packaging/AirClick.spec",
        "packaging/AirClick.iss",
        "packaging/build_installer.ps1",
        "config/version.py",
    )
    for relative_path in required:
        assert os.path.exists(os.path.join(PROJECT_ROOT, relative_path))


def test_installer_exposes_uninstall():
    script_path = os.path.join(PROJECT_ROOT, "packaging", "AirClick.iss")
    with open(script_path, encoding="utf-8") as installer_script:
        contents = installer_script.read()

    assert "Uninstallable=yes" in contents
    assert 'Name: "{group}\\Uninstall {#AppName}"; Filename: "{uninstallexe}"' in contents


def test_application_icon_is_valid():
    icon_path = os.path.join(PROJECT_ROOT, "packaging", "AirClick.ico")
    with Image.open(icon_path) as icon:
        assert icon.format == "ICO"
        assert icon.ico.sizes() == {
            (16, 16),
            (24, 24),
            (32, 32),
            (48, 48),
            (64, 64),
            (128, 128),
            (256, 256),
        }


def test_build_uses_the_application_version():
    read_project_version()
    version_path = os.path.join(PROJECT_ROOT, "config", "version.py")
    installer_path = os.path.join(PROJECT_ROOT, "packaging", "AirClick.iss")
    build_path = os.path.join(PROJECT_ROOT, "packaging", "build_installer.ps1")

    with open(version_path, encoding="utf-8") as version_file:
        version_contents = version_file.read()
    with open(installer_path, encoding="utf-8") as installer_script:
        installer_contents = installer_script.read()
    with open(build_path, encoding="utf-8") as build_script:
        build_contents = build_script.read()

    assert version_contents.count("APP_VERSION = ") == 1
    assert "AppVersion={#AppVersion}" in installer_contents
    assert "OutputBaseFilename=AirClick-Setup-{#AppVersion}" in installer_contents
    assert "/DAppVersion={1}" in build_contents
    assert 'AirClick-Setup-1.0.0.exe' not in build_contents


if __name__ == "__main__":
    test_release_files_exist()
    test_installer_exposes_uninstall()
    test_application_icon_is_valid()
    test_build_uses_the_application_version()
    print("All release layout tests passed.")
