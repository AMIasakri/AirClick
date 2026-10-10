"""Unit tests for bounded application logging."""

import os
import sys
import tempfile
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.helpers as helpers


def test_rolling_fps_tracks_recent_frames():
    counter = helpers.RollingFpsCounter(window_seconds=2.0)
    assert counter.tick(now=0.0) == 0.0
    assert math.isclose(counter.tick(now=1 / 30), 30)
    assert math.isclose(counter.tick(now=2 / 30), 30)

    assert math.isclose(counter.tick(now=1.0), 3)

    for frame in range(1, 91):
        fps = counter.tick(now=1.0 + frame / 30)
    assert math.isclose(fps, 30)


def test_rolling_fps_rejects_invalid_samples():
    try:
        helpers.RollingFpsCounter(window_seconds=0)
    except ValueError:
        pass
    else:
        raise AssertionError("non-positive FPS window should be rejected")

    counter = helpers.RollingFpsCounter()
    counter.tick(now=1.0)
    try:
        counter.tick(now=1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("non-increasing timestamps should be rejected")


def test_rolling_fps_resets_after_a_long_pause():
    counter = helpers.RollingFpsCounter(window_seconds=2.0)
    counter.tick(now=0.0)
    counter.tick(now=1 / 30)

    assert counter.tick(now=5.0) == 0.0
    assert math.isclose(counter.tick(now=5.0 + 1 / 30), 30)


def test_rolling_performance_monitor_averages_recent_samples():
    monitor = helpers.RollingPerformanceMonitor(window_seconds=2.0)
    assert monitor.update({"model": 10.0, "overlay": 2.0}, now=0.0) == {
        "model": 10.0,
        "overlay": 2.0,
    }
    assert monitor.update({"model": 20.0, "overlay": 4.0}, now=1.0) == {
        "model": 15.0,
        "overlay": 3.0,
    }
    assert monitor.update({"model": 30.0, "overlay": 6.0}, now=2.5) == {
        "model": 25.0,
        "overlay": 5.0,
    }


def test_log_file_is_bounded():
    helpers._logging_enabled = True
    original_local_app_data = os.environ.get("LOCALAPPDATA")
    original_limit = helpers.MAX_LOG_BYTES
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["LOCALAPPDATA"] = temp_dir
        helpers.MAX_LOG_BYTES = 256
        helpers._log_path = os.path.join(temp_dir, "AirClick", "logs", "airclick.log")
        try:
            for index in range(30):
                helpers.log_message(f"bounded log entry {index} " + "x" * 40)
            log_path = os.path.join(temp_dir, "AirClick", "logs", "airclick.log")
            assert os.path.getsize(log_path) <= helpers.MAX_LOG_BYTES + 100
            with open(log_path, encoding="utf-8") as log_file:
                contents = log_file.read()
            assert "bounded log entry 29" in contents
        finally:
            helpers.MAX_LOG_BYTES = original_limit
            helpers._log_path = None
            if original_local_app_data is None:
                os.environ.pop("LOCALAPPDATA", None)
            else:
                os.environ["LOCALAPPDATA"] = original_local_app_data
            helpers._logging_enabled = False


if __name__ == "__main__":
    test_rolling_fps_tracks_recent_frames()
    test_rolling_fps_rejects_invalid_samples()
    test_rolling_fps_resets_after_a_long_pause()
    test_rolling_performance_monitor_averages_recent_samples()
    test_log_file_is_bounded()
    print("All helper tests passed.")
