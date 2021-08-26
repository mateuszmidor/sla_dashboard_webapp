import logging
from datetime import datetime, timedelta, timezone

from domain.model.mesh_results import MeshResults
from domain.repo import Repo
from domain.types import AgentID, TestID

logger = logging.getLogger(__name__)


class MeshUpdatePolicySingleConnection:
    """
    Implements MeshUpdatePolicy
    Get an update for a single connection, with deep timeseries data
    """

    def __init__(
        self,
        repo: Repo,
        test_id: TestID,
        min_history_seconds: int,
        full_history_seconds: int,
        max_data_age_seconds: int,
        from_agent,
        to_agent: AgentID,
    ) -> None:
        self._repo = repo
        self._test_id = test_id
        self._full_history_seconds = full_history_seconds
        self._min_history_seconds = min_history_seconds
        self._max_data_age_seconds = max_data_age_seconds
        self._from_agent = from_agent
        self._to_agent = to_agent

    def need_update(self, mesh: MeshResults) -> bool:
        conn = mesh.connection(self._from_agent, self._to_agent)
        if not conn.health:
            return True
        newest_timestamp = conn.health[0].timestamp
        oldest_timestamp = conn.health[-1].timestamp

        # check cached data covers expected timespan
        cached_data_timespan = newest_timestamp - oldest_timestamp
        expected_data_timespan = timedelta(seconds=self._full_history_seconds - self._min_history_seconds)
        if cached_data_timespan < expected_data_timespan:
            return True

        # check cached data is fresh enough
        max_age = timedelta(seconds=self._max_data_age_seconds)
        return datetime.now(timezone.utc) - newest_timestamp > max_age

    def get_update(self, mesh: MeshResults) -> MeshResults:
        logger.debug("History: %ds", self._full_history_seconds)
        agent_ids = [self._from_agent]
        task_id = mesh.agent_id_to_task_id(self._to_agent)
        if task_id:
            task_ids = [task_id]
        else:
            logger.debug("TaskID for AgentID '%s' not found; requesting entire mesh row", self._to_agent)
            task_ids = []
        return self._repo.get_mesh_test_results(self._test_id, agent_ids, task_ids, self._full_history_seconds, True)
