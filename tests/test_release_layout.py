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


if __name__ == "__main__":
    test_release_files_exist()
    print("All release layout tests passed.")
