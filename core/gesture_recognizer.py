"""
ماژول تشخیص حرکات دست
"""

import sys
import os
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import GESTURE_SETTINGS
from utils.helpers import log_message


class GestureRecognizer:
    """کلاس تشخیص حرکات دست"""

    def __init__(self):
        log_message("در حال راه‌اندازی GestureRecognizer...")
        self.gesture_names = GESTURE_SETTINGS['gesture_names']
        log_message("GestureRecognizer ready")

    def recognize(self, fingers):
        if not fingers or len(fingers) != 5:
            return self.gesture_names['unknown']

        thumb, index, middle, ring, pinky = fingers

        if all(fingers):
            return self.gesture_names['all_open']

        if not any(fingers):
            return self.gesture_names['fist']

        if index and middle and not ring and not pinky:
            return self.gesture_names['index_middle_up']

        if index and not middle and not ring and not pinky:
            return self.gesture_names['only_index']

        if not index and middle and not ring and not pinky:
            return self.gesture_names['index_folded_middle_open']

        if index and not middle:
            return self.gesture_names['middle_folded_index_open']

        return self.gesture_names['unknown']

    def recognize_click_hand(self, fingers):
        """تشخیص دقیق‌تر برای دست کلیک"""
        if not fingers or len(fingers) != 5:
            return self.gesture_names['unknown']

        thumb, index, middle, ring, pinky = fingers

        if not any([index, middle, ring, pinky]):
            return self.gesture_names['fist']

        if not index and not middle:
            return self.gesture_names['index_middle_folded']

        if not index and middle:
            return self.gesture_names['index_folded_middle_open']

        if index and not middle:
            return self.gesture_names['middle_folded_index_open']

        if not ring and index and middle and pinky:
            return self.gesture_names['ring_folded_scroll']

        if all(fingers):
            return self.gesture_names['all_open']

        return self.gesture_names['unknown']

    def is_moving(self, gesture):
        return gesture == self.gesture_names['only_index']

    def is_dragging(self, gesture):
        return gesture == self.gesture_names['index_middle_up']

    def is_left_click(self, gesture):
        return gesture == self.gesture_names['index_folded_middle_open']

    def is_right_click(self, gesture):
        return gesture == self.gesture_names['middle_folded_index_open']

    def is_middle_click(self, gesture):
        return gesture == self.gesture_names['fist']

    def is_double_click(self, gesture):
        return gesture == self.gesture_names['index_middle_folded']

    def is_scroll(self, gesture):
        return gesture == self.gesture_names['ring_folded_scroll']

    def is_ready(self, gesture):
        return gesture == self.gesture_names['all_open']


class GestureStabilizer:
    """Require a gesture to persist for several frames before accepting it."""

    def __init__(self, required_frames=3):
        if required_frames < 1:
            raise ValueError("required_frames must be positive")
        self.required_frames = required_frames
        self._history = []
        self.stable_gesture = None

    def update(self, gesture):
        self._history.append(gesture)
        if len(self._history) > self.required_frames:
            self._history.pop(0)

        if len(self._history) == self.required_frames:
            candidate, count = Counter(self._history).most_common(1)[0]
            if count == self.required_frames:
                self.stable_gesture = candidate
        return self.stable_gesture

    def reset(self):
        self._history.clear()
        self.stable_gesture = None
