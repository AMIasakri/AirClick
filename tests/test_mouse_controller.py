"""Unit tests for MouseController state transitions without moving the real mouse."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import core.mouse_controller as mouse_module
from core.mouse_controller import MouseController


def make_controller():
    controller = MouseController.__new__(MouseController)
    controller.relative_mode = True
    controller.screen_width = 1000
    controller.screen_height = 800
    controller.movement_speed = 1.0
    controller.dead_zone = 2
    controller.menu_mode_dead_zone = 1
    controller.smoothing = 1.0
    controller.current_x = 500
    controller.current_y = 400
    controller.smooth_x = 500.0
    controller.smooth_y = 400.0
    controller.last_tip_x = None
    controller.last_tip_y = None
    controller.tracking_active = False
    controller.drag_active = False
    controller.drag_button = "left"
    controller.last_scroll_y = None
    controller.scroll_active = False
    controller.scroll_dead_zone = 8
    controller.scroll_speed = 3
    controller.last_action_time = 0
    return controller


def test_relative_move_reanchors_without_jumping():
    controller = make_controller()
    original_move_to = mouse_module.pyautogui.moveTo
    mouse_module.pyautogui.moveTo = lambda *args, **kwargs: None

    try:
        assert controller.move(300, 200, 640, 480, reanchor=True) == (500, 400)
        assert controller.move(300, 200, 640, 480) == (500, 400)
        assert controller.tracking_active is True
    finally:
        mouse_module.pyautogui.moveTo = original_move_to


def test_relative_move_clamps_to_screen():
    controller = make_controller()
    original_move_to = mouse_module.pyautogui.moveTo
    mouse_module.pyautogui.moveTo = lambda *args, **kwargs: None

    try:
        controller.move(0, 0, 640, 480, reanchor=True)
        position = controller.move(-1000, -1000, 640, 480)
    finally:
        mouse_module.pyautogui.moveTo = original_move_to

    assert position == (0, 0)


def test_invalid_frame_dimensions_are_rejected():
    controller = make_controller()

    for dimensions in ((0, 480), (640, 0), (-1, 480)):
        try:
            controller.move(10, 10, *dimensions)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid frame dimensions must raise ValueError")


def test_scroll_reanchors_and_respects_dead_zone():
    controller = make_controller()
    scrolls = []
    original_scroll = mouse_module.pyautogui.scroll
    mouse_module.pyautogui.scroll = lambda clicks: scrolls.append(clicks)

    try:
        assert controller.scroll(200, reanchor=True) == 0
        assert controller.scroll(205) == 0
        assert controller.scroll(224) == 6
        assert scrolls == [-6]
    finally:
        mouse_module.pyautogui.scroll = original_scroll


def test_pause_tracking_releases_active_drag():
    controller = make_controller()
    events = []
    controller.drag_active = True
    controller.drag_button = "left"
    original_mouse_up = mouse_module.pyautogui.mouseUp
    mouse_module.pyautogui.mouseUp = lambda **kwargs: events.append(kwargs)

    try:
        controller.pause_tracking()
    finally:
        mouse_module.pyautogui.mouseUp = original_mouse_up

    assert events == [{"button": "left"}]
    assert controller.drag_active is False
    assert controller.tracking_active is False
    assert controller.last_tip_x is None
    assert controller.last_tip_y is None


if __name__ == "__main__":
    test_relative_move_reanchors_without_jumping()
    test_relative_move_clamps_to_screen()
    test_invalid_frame_dimensions_are_rejected()
    test_scroll_reanchors_and_respects_dead_zone()
    test_pause_tracking_releases_active_drag()
    print("All MouseController tests passed.")
