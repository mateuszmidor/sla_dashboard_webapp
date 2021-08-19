from typing import List, Protocol

from domain.model.mesh_results import MeshResults
from domain.types import AgentID, TaskID, TestID


class Repo(Protocol):
    """Repo provides data access to Kentik Synthetic Tests"""

    def get_mesh_test_results(
        self,
        test_id: TestID,
        agent_ids: List[AgentID],
        task_ids: List[TaskID],
        results_lookback_seconds: int,
        timeseries: bool,
    ) -> MeshResults:
        """
        agent_ids - filer the response to connections outgoing from listed agents. Empty list = do not filter.
        task_ids - filter the response to connections targeting agents related to listed tasks. Empty list = do not filter
        """
        pass
