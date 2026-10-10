"""UI overlay tests for shortcut visibility and HUD layout."""

import os
import sys
import unittest.mock

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.overlay import OverlayRenderer


def test_panel_blending_matches_full_frame_reference():
    frame = np.random.default_rng(1).integers(0, 256, (120, 160, 3), dtype=np.uint8)
    expected = frame.copy()
    overlay = expected.copy()
    cv2.rectangle(overlay, (12, 18), (94, 70), (18, 18, 32), -1)
    cv2.rectangle(overlay, (12, 18), (94, 70), (60, 60, 90), 1, cv2.LINE_AA)
    expected = cv2.addWeighted(overlay, 0.75, expected, 0.25, 0)

    OverlayRenderer().draw_panel(frame, 12, 18, 94, 70, 0.75, (60, 60, 90))

    np.testing.assert_array_equal(frame, expected)


def test_pill_blending_matches_full_frame_reference():
    frame = np.random.default_rng(2).integers(0, 256, (120, 160, 3), dtype=np.uint8)
    expected = frame.copy()
    text, x, y, color, scale = "30 FPS", 72, 32, (102, 207, 81), 0.36
    (text_width, text_height), _ = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, scale, 1,
    )
    pad_x, pad_y = 10, 5
    x1, y1 = x, y - text_height - pad_y
    x2, y2 = x + text_width + pad_x * 2, y + pad_y
    overlay = expected.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1, cv2.LINE_AA)
    expected = cv2.addWeighted(overlay, 0.16, expected, 0.84, 0)
    cv2.rectangle(expected, (x1, y1), (x2, y2), color, 1, cv2.LINE_AA)
    cv2.putText(
        expected, text, (x + pad_x, y), cv2.FONT_HERSHEY_SIMPLEX,
        scale, (240, 240, 250), 1, cv2.LINE_AA,
    )

    OverlayRenderer().draw_pill(frame, text, x, y, color, scale)

    np.testing.assert_array_equal(frame, expected)


def test_zone_blending_matches_full_frame_reference():
    frame = np.random.default_rng(3).integers(0, 256, (120, 160, 3), dtype=np.uint8)
    expected = frame.copy()
    split_x, top_bar, bottom_bar = 80, 12, 16
    height, width = expected.shape[:2]
    zone = expected.copy()
    cv2.rectangle(zone, (0, top_bar), (split_x, height - bottom_bar), (40, 80, 40), -1)
    cv2.rectangle(zone, (split_x, top_bar), (width, height - bottom_bar), (80, 50, 30), -1)
    expected[:] = cv2.addWeighted(zone, 0.10, expected, 0.90, 0)
    for y in range(top_bar, height - bottom_bar, 14):
        cv2.line(
            expected, (split_x, y), (split_x, min(y + 7, height - bottom_bar)),
            (180, 180, 210), 1, cv2.LINE_AA,
        )
    cv2.putText(
        expected, "MOUSE / DRAG", (split_x // 2 - 55, top_bar + 18),
        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 0), 1, cv2.LINE_AA,
    )
    cv2.putText(
        expected, "CLICK / SCROLL", (split_x + split_x // 2 - 55, top_bar + 18),
        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 165, 255), 1, cv2.LINE_AA,
    )

    OverlayRenderer().draw_zones(frame, split_x, top_bar, bottom_bar)

    np.testing.assert_array_equal(frame, expected)


def test_header_shortcuts_and_fps_do_not_overlap():
    renderer = OverlayRenderer()
    frame = np.zeros((540, 680, 3), dtype=np.uint8)
    shortcuts = "Q  H  D  P"
    fps_label = "30 FPS"

    with unittest.mock.patch("ui.overlay.cv2.putText", wraps=cv2.putText) as put_text:
        with unittest.mock.patch.object(
            renderer, "draw_pill", wraps=renderer.draw_pill,
        ) as draw_pill:
            renderer.draw_header(frame, fps=30)

    shortcut_call = next(
        call for call in put_text.call_args_list
        if call.args[1] == shortcuts
    )
    shortcut_x = shortcut_call.args[2][0]
    (shortcut_width, _), _ = cv2.getTextSize(
        shortcuts, cv2.FONT_HERSHEY_SIMPLEX, 0.34, 1,
    )
    assert shortcut_x + shortcut_width <= frame.shape[1] - 18

    fps_call = next(call for call in draw_pill.call_args_list if call.args[1] == fps_label)
    fps_x = fps_call.args[2]
    (fps_width, _), _ = cv2.getTextSize(
        fps_label, cv2.FONT_HERSHEY_SIMPLEX, 0.36, 1,
    )
    assert fps_x + fps_width + 20 < shortcut_x


if __name__ == "__main__":
    test_panel_blending_matches_full_frame_reference()
    test_pill_blending_matches_full_frame_reference()
    test_zone_blending_matches_full_frame_reference()
    test_header_shortcuts_and_fps_do_not_overlap()
    print("All overlay tests passed.")
