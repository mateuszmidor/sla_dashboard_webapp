from typing import List, Optional, Protocol

from domain.model.mesh_config import MeshConfig
from domain.model.mesh_results import MeshResults
from domain.types import AgentID, TaskID, TestID


class Repo(Protocol):
    """Repo provides data access to Kentik Synthetic Tests"""

    def get_mesh_config(self, test_id: TestID) -> MeshConfig:
        pass

    def get_mesh_test_results(
        self,
        test_id: TestID,
        history_length_seconds: int,
        timeseries: bool = True,
        agent_ids: Optional[List[AgentID]] = None,
        task_ids: Optional[List[TaskID]] = None,
    ) -> MeshResults:
        """
        agent_ids - filer the response to connections outgoing from listed agents. Empty = do not filter.
        task_ids - filter the response to connections targeting agents related to listed tasks. Empty = do not filter
        """
        pass
