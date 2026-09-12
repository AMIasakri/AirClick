"""Unit tests for bounded application logging."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.helpers as helpers


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
    test_log_file_is_bounded()
    print("All helper tests passed.")
