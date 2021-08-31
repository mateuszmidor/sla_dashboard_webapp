import threading
import time
from typing import Dict

from domain.types import AgentID


class RateLimiter:
    def __init__(self, interval_seconds: int) -> None:
        self._lock = threading.Lock()
        self._interval_seconds = interval_seconds
        self._mesh: Dict[AgentID, Dict[AgentID, int]] = {}

    def check_and_update(self, from_agent=AgentID(), to_agent: AgentID = AgentID()) -> bool:
        now = int(time.monotonic())
        with self._lock:
            last_update_seconds = self._get_last_update(from_agent, to_agent)
            if now - last_update_seconds > self._interval_seconds:
                self._set_last_update(from_agent, to_agent, now)
                return True
            return False

    @property
    def interval_seconds(self) -> int:
        return self._interval_seconds

    def _get_last_update(self, from_agent, to_agent: AgentID) -> int:
        if from_agent not in self._mesh:
            self._mesh[from_agent] = {}
        if to_agent not in self._mesh[from_agent]:
            self._mesh[from_agent][to_agent] = 0
        return self._mesh[from_agent][to_agent]

    def _set_last_update(self, from_agent, to_agent: AgentID, value: int) -> None:
        if from_agent not in self._mesh:
            self._mesh[from_agent] = {}
        self._mesh[from_agent][to_agent] = value
