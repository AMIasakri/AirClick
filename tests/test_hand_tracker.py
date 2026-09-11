"""Unit tests for HandTracker logic without camera or MediaPipe startup."""

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hand_tracker import HandTracker


def make_hand(index_up=False, middle_up=False):
    points = [SimpleNamespace(x=0.5, y=0.6) for _ in range(21)]
    for tip, pip, up in (
        (8, 6, index_up),
        (12, 10, middle_up),
        (16, 14, False),
        (20, 18, False),
    ):
        points[pip].y = 0.4
        points[tip].y = 0.2 if up else 0.55
    points[5].y = 0.5
    return points


def make_tracker(landmarks):
    tracker = HandTracker.__new__(HandTracker)
    tracker.all_landmarks = landmarks
    tracker.all_bounding_boxes = []
    tracker.all_fingers_status = []
    tracker.hand_types = []
    tracker.hand_is_live = []
    tracker.hands_detected = []
    return tracker


def test_invalid_indices_do_not_read_from_end_of_lists():
    tracker = make_tracker([make_hand(index_up=True)])
    assert tracker.get_landmarks(-1) is None
    assert tracker.get_bounding_box(-1) is None
    assert tracker.get_fingers_status(-1) is None
    assert tracker.get_hand_type(-1) == "Unknown"
    assert tracker.is_hand_live(-1) is False


def test_pointer_gesture_accepts_slightly_bent_index():
    tracker = make_tracker([make_hand(index_up=True)])
    landmarks = tracker.all_landmarks[0]
    landmarks[8].y = landmarks[6].y + 0.01
    assert tracker.is_pointer_gesture(0) is True


def test_drag_gesture_requires_index_and_middle():
    tracker = make_tracker([make_hand(index_up=True, middle_up=True)])
    assert tracker.is_drag_gesture(0) is True
    assert tracker.is_pointer_gesture(0) is False


def test_role_assignment_separates_two_hands():
    tracker = HandTracker.__new__(HandTracker)
    tracker.hand_is_live = [True, True]
    tracker.all_bounding_boxes = [
        ((80, 100), (180, 220)),
        ((420, 100), (520, 220)),
    ]
    tracker.role_memory = {
        "mouse": {"center": None, "lost": 0},
        "click": {"center": None, "lost": 0},
    }
    tracker.mouse_hand_index = -1
    tracker.click_hand_index = -1
    tracker.hand_separation = None
    tracker.hands_too_close = False
    tracker.role_hand_types = {"mouse": None, "click": None}
    tracker.role_candidate = None
    tracker.role_candidate_frames = 0
    tracker.hand_types = ["Right", "Left"]

    tracker._assign_hand_roles(640, 480)

    assert tracker.mouse_hand_index == 0
    assert tracker.click_hand_index == 1
    assert tracker.hand_separation == 340
    assert tracker.hands_too_close is False


def test_role_change_requires_multiple_frames():
    tracker = HandTracker.__new__(HandTracker)
    tracker.hand_is_live = [True]
    tracker.all_bounding_boxes = [((80, 100), (180, 220))]
    tracker.role_memory = {
        "mouse": {"center": None, "lost": 0},
        "click": {"center": None, "lost": 0},
    }
    tracker.mouse_hand_index = 0
    tracker.click_hand_index = 1
    tracker.hand_separation = None
    tracker.hands_too_close = False
    tracker.role_candidate = None
    tracker.role_candidate_frames = 0
    tracker.role_hand_types = {"mouse": None, "click": None}
    tracker.hand_types = ["Right"]

    tracker._resolve_single_hand_role = lambda detection, width: "click"
    for _ in range(2):
        tracker._assign_hand_roles(640, 480)
        assert (tracker.mouse_hand_index, tracker.click_hand_index) == (0, 1)

    tracker._assign_hand_roles(640, 480)
    assert (tracker.mouse_hand_index, tracker.click_hand_index) == (-1, 0)


def test_fast_reordering_keeps_roles_by_handedness():
    tracker = HandTracker.__new__(HandTracker)
    tracker.hand_is_live = [True, True]
    tracker.all_bounding_boxes = [
        ((80, 100), (180, 220)),
        ((420, 100), (520, 220)),
    ]
    tracker.hand_types = ["Right", "Left"]
    tracker.role_memory = {
        "mouse": {"center": None, "lost": 0},
        "click": {"center": None, "lost": 0},
    }
    tracker.mouse_hand_index = -1
    tracker.click_hand_index = -1
    tracker.hand_separation = None
    tracker.hands_too_close = False
    tracker.role_candidate = None
    tracker.role_candidate_frames = 0
    tracker.role_hand_types = {"mouse": None, "click": None}

    tracker._assign_hand_roles(640, 480)
    assert (tracker.mouse_hand_index, tracker.click_hand_index) == (0, 1)

    tracker.hand_is_live = [True, True]
    tracker.all_bounding_boxes = [
        ((430, 100), (530, 220)),
        ((70, 100), (170, 220)),
    ]
    tracker.hand_types = ["Left", "Right"]
    tracker._assign_hand_roles(640, 480)

    assert (tracker.mouse_hand_index, tracker.click_hand_index) == (1, 0)


if __name__ == "__main__":
    test_invalid_indices_do_not_read_from_end_of_lists()
    test_pointer_gesture_accepts_slightly_bent_index()
    test_drag_gesture_requires_index_and_middle()
    test_role_assignment_separates_two_hands()
    test_role_change_requires_multiple_frames()
    test_fast_reordering_keeps_roles_by_handedness()
    print("All HandTracker tests passed.")
