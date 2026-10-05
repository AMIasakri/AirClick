"""Checks for files required by the Windows release package."""

import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_release_files_exist():
    required = (
        "hand_landmarker.task",
        "packaging/AirClick.spec",
        "packaging/AirClick.iss",
        "packaging/build_installer.ps1",
    )
    for relative_path in required:
        assert os.path.exists(os.path.join(PROJECT_ROOT, relative_path))


def test_installer_exposes_uninstall():
    script_path = os.path.join(PROJECT_ROOT, "packaging", "AirClick.iss")
    with open(script_path, encoding="utf-8") as installer_script:
        contents = installer_script.read()

    assert "Uninstallable=yes" in contents
    assert 'Name: "{group}\\Uninstall {#AppName}"; Filename: "{uninstallexe}"' in contents


if __name__ == "__main__":
    test_release_files_exist()
    test_installer_exposes_uninstall()
    print("All release layout tests passed.")
