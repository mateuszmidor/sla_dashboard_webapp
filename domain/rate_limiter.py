import threading
import time


class RateLimiter:
    def __init__(self, interval_seconds: int) -> None:
        self._lock = threading.Lock()
        self._interval_seconds = interval_seconds
        self._last_update_seconds = (
            int(time.monotonic()) - interval_seconds - 1
        )  # make sure the first check is always true

    def check_and_update(self) -> bool:
        """Returns True if acting now is within the rate limit, False otherwise"""

        with self._lock:
            now = int(time.monotonic())
            if now - self._last_update_seconds > self._interval_seconds:
                self._last_update_seconds = now
                return True
            return False

    @property
    def interval_seconds(self) -> int:
        return self._interval_seconds
