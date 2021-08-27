import logging

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
        from_agent,
        to_agent: AgentID,
    ) -> None:
        self._repo = repo
        self._test_id = test_id
        self._full_history_seconds = full_history_seconds
        self._min_history_seconds = min_history_seconds
        self._from_agent = from_agent
        self._to_agent = to_agent

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
