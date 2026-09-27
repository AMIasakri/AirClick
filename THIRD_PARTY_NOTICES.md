# Third-Party Notices

AirClick is distributed under the MIT License. The third-party components
listed below remain subject to their own licenses. Nothing in this file
changes or replaces those licenses.

## AirClick project

- Project: AirClick
- Repository: https://github.com/AMIasakri/AirClick
- Copyright: 2026 Amir_askari
- Support and bug reports: amir.as.7257@gmail.com

## Direct Python dependencies

The following packages are declared directly by AirClick in
`requirements.txt`:

| Component | License | Official project |
| --- | --- | --- |
| OpenCV Python | Apache License 2.0 | https://github.com/opencv/opencv-python |
| MediaPipe | Apache License 2.0 | https://github.com/google/mediapipe |
| PyAutoGUI | BSD License | https://github.com/asweigart/pyautogui |
| NumPy | BSD-3-Clause and additional component licenses | https://github.com/numpy/numpy |

The installed distributions may include transitive dependencies and bundled
third-party notices. Their license files are distributed with the relevant
Python packages and must remain available when those components are
redistributed.

## MediaPipe hand landmarker model

AirClick includes `hand_landmarker.task`, a MediaPipe Hand Landmarker model
asset used for on-device hand tracking. The model is obtained from the
official MediaPipe model distribution:

- MediaPipe repository: https://github.com/google/mediapipe
- MediaPipe license: https://github.com/google/mediapipe/blob/master/LICENSE
- MediaPipe models documentation:
  https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker

Before each public release, confirm that the model asset and its associated
metadata may be redistributed with the installer under the applicable
upstream terms.

## OpenCV bundled notices

OpenCV distributions may include additional third-party components. Their
notices are included by the installed package in:

- `cv2/LICENSE.txt`
- `cv2/LICENSE-3RD-PARTY.txt`

Those notices must be preserved in any redistributable bundle where the
corresponding OpenCV files are included.

## Contact

For licensing questions, bug reports, or distribution concerns, contact:

- GitHub: https://github.com/AMIasakri/AirClick
- Email: amir.as.7257@gmail.com
