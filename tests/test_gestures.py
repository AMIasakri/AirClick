"""Unit tests for gesture recognition (no camera required)."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gesture_recognizer import GestureRecognizer, GestureStabilizer


def test_click_gestures():
    gr = GestureRecognizer()
    cases = [
        ([True, False, True, False, False], "LEFT CLICK"),
        ([True, True, False, False, False], "RIGHT CLICK"),
        ([True, False, False, False, False], "MIDDLE CLICK"),
        ([True, False, False, True, True], "DOUBLE CLICK"),
        ([True, True, True, False, True], "SCROLL"),
    ]
    for fingers, expected in cases:
        result = gr.recognize_click_hand(fingers)
        assert result == expected, f"Expected {expected}, got {result} for {fingers}"


def test_mouse_gestures():
    gr = GestureRecognizer()
    assert gr.recognize([True, True, True, True, True]) == "READY"
    assert gr.recognize([True, True, False, False, False]) == "MOVING"
    assert gr.recognize([True, True, True, False, False]) == "DRAG"


def test_gesture_stabilizer_requires_consistent_frames():
    stabilizer = GestureStabilizer(required_frames=3)
    assert stabilizer.update("LEFT CLICK") is None
    assert stabilizer.update("RIGHT CLICK") is None
    assert stabilizer.update("LEFT CLICK") is None
    assert stabilizer.update("LEFT CLICK") is None
    assert stabilizer.update("LEFT CLICK") == "LEFT CLICK"


def test_gesture_stabilizer_resets():
    stabilizer = GestureStabilizer(required_frames=2)
    stabilizer.update("LEFT CLICK")
    stabilizer.reset()
    assert stabilizer.stable_gesture is None


if __name__ == "__main__":
    test_click_gestures()
    test_mouse_gestures()
    print("All gesture tests passed.")
