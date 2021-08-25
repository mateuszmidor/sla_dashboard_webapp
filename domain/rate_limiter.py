import threading
from datetime import datetime, timedelta, timezone


class RateLimiter:
    """RateLimiter is used to limit request rate towards API Server"""

    def __init__(self, min_interval_seconds: int) -> None:
        self._lock = threading.Lock()
        self._min_interval = timedelta(seconds=min_interval_seconds)
        self._last_successful_check = datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)

    def check_and_update(self) -> bool:
        """Return True if interval is preserved, False otherwise"""

        with self._lock:
            now = datetime.now(timezone.utc)
            if now - self._last_successful_check > self._min_interval:
                self._last_successful_check = now
                return True
            return False

    @property
    def inverval(self) -> timedelta:
        return self._min_interval
