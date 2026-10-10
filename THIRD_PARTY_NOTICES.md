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

- Model file:
  https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
- SHA-256 of the included file:
  `fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1`
- MediaPipe repository license:
  https://github.com/google-ai-edge/mediapipe/blob/master/LICENSE
- MediaPipe models documentation:
  https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
- Google model card for MediaPipe Hands (Lite/Full):
  https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Hand%20Tracking%20(Lite_Full)%20with%20Fairness%20Oct%202021.pdf

The official task documentation and model card describe the model but do not
explicitly state the license for this binary asset. The MediaPipe repository's
Apache 2.0 license alone is not sufficient evidence of the model asset's
redistribution terms. Confirm those terms with an authoritative model-specific
source or the model publisher before public release.

A MediaPipe maintainer has separately confirmed that a specific Pose Landmarker
task bundle is Apache 2.0 in
[google-ai-edge/mediapipe#6306](https://github.com/google-ai-edge/mediapipe/issues/6306).
That answer concerns a different model asset and does not establish the license
for this Hand Landmarker bundle.

## Application icon

`packaging/AirClick.ico` is original artwork created specifically for AirClick
on 2026-10-10, replacing an earlier icon whose source was not recorded. The
replacement is composed from geometric shapes and contains no third-party
image assets.

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
