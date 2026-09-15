"""Unit tests for user-facing tracking and mouse settings."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.settings as settings


def test_default_settings_are_valid():
    settings.validate_settings()


def test_invalid_smoothing_is_rejected():
    original = settings.MOUSE_SETTINGS['smoothing_factor']
    settings.MOUSE_SETTINGS['smoothing_factor'] = 1.1
    try:
        try:
            settings.validate_settings()
        except ValueError as error:
            assert 'smoothing_factor' in str(error)
        else:
            raise AssertionError('Invalid smoothing must be rejected')
    finally:
        settings.MOUSE_SETTINGS['smoothing_factor'] = original


def test_invalid_stability_count_is_rejected():
    original = settings.HAND_SETTINGS['role_stability_frames']
    settings.HAND_SETTINGS['role_stability_frames'] = 0
    try:
        try:
            settings.validate_settings()
        except ValueError as error:
            assert 'role_stability_frames' in str(error)
        else:
            raise AssertionError('Invalid stability count must be rejected')
    finally:
        settings.HAND_SETTINGS['role_stability_frames'] = original


def test_role_switch_distance_multiplier_is_positive():
    assert settings.HAND_SETTINGS['role_switch_distance_multiplier'] > 1


if __name__ == '__main__':
    test_default_settings_are_valid()
    test_invalid_smoothing_is_rejected()
    test_invalid_stability_count_is_rejected()
    print('All settings tests passed.')
