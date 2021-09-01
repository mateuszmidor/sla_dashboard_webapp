import logging
import threading
from copy import deepcopy
from typing import Callable

from domain.model.mesh_config import MeshConfig
from domain.model.mesh_results import MeshResults
from domain.rate_limiter import RateLimiter
from domain.repo import Repo
from domain.types import AgentID, TestID

logger = logging.getLogger(__name__)


class CachingRepoRequestDriven:
    """
    Get and cache mesh test results:
    - get_mesh_results_all_connections() allows to get and cache test results for all connections but without timeseries data
    - get_mesh_results_single_connection() allows to get and cache test results for single connection but with timeseries data
    """

    def __init__(
        self,
        source_repo: Repo,
        monitored_test_id: TestID,
        data_request_interval_periods: int,
        data_history_length_periods: int,
        data_min_periods: int,
    ) -> None:
        self._source_repo = source_repo
        self._test_id = monitored_test_id
        self._mesh_config = source_repo.get_mesh_config(monitored_test_id)
        test_update_period_seconds = self._mesh_config.update_period_seconds
        self._full_history_seconds = data_history_length_periods * test_update_period_seconds
        self._rate_limiter = RateLimiter(data_request_interval_periods * test_update_period_seconds)
        self._mesh_cache = MeshResults()
        self._mesh_lock = threading.Lock()

        self._min_history_seconds = test_update_period_seconds * data_min_periods

    @property
    def min_history_seconds(self) -> int:
        return self._min_history_seconds

    def get_mesh_results_all_connections(self) -> MeshResults:
        """
        Get results for all connections but with minimum history data
        """

        if not self._rate_limiter.check_and_update():
            logger.debug("Returning cached data (minimum update interval: %ds)", self._rate_limiter.interval_seconds)
            return self._get_mesh()

        getter = self._get_all_connections()
        return self._update(getter)

    def get_mesh_results_single_connection(self, from_agent: AgentID, to_agent: AgentID) -> MeshResults:
        """
        Get results for single connection but with full history data
        """

        if not self._rate_limiter.check_and_update(f"{from_agent}:{to_agent}"):
            logger.debug("Returning cached data (minimum update interval: %ds)", self._rate_limiter.interval_seconds)
            return self._get_mesh()

        getter = self._get_single_connection(from_agent, to_agent)
        return self._update(getter)

    def _update(self, get_mesh_update: Callable[[], MeshResults]) -> MeshResults:
        """Condition: returned MeshResults is only read and never modified"""

        try:
            logger.debug("Mesh cache update start...")
            fresh_mesh = get_mesh_update()
            self._update_cache_with(fresh_mesh)
            num_fresh_items = fresh_mesh.connection_matrix.num_connections_with_data()
            logger.debug("Mesh cache update finished with %d fresh items", num_fresh_items)
        except Exception:
            logger.exception("Mesh cache update error")

        return self._get_mesh()

    def _get_all_connections(self) -> Callable[[], MeshResults]:
        def getter() -> MeshResults:
            logger.debug("History: %ds", self.min_history_seconds)
            return self._source_repo.get_mesh_test_results(
                test_id=self._test_id, history_length_seconds=self.min_history_seconds
            )

        return getter

    def _get_single_connection(self, from_agent: AgentID, to_agent: AgentID) -> Callable[[], MeshResults]:
        def getter() -> MeshResults:
            logger.debug("History: %ds", self._full_history_seconds)
            agent_ids = [from_agent]
            task_id = self._get_mesh().agent_id_to_task_id(to_agent)
            if task_id:
                task_ids = [task_id]
            else:
                logger.warning("TaskID for AgentID '%s' not found; requesting entire mesh row", to_agent)
                task_ids = []
            return self._source_repo.get_mesh_test_results(
                test_id=self._test_id,
                history_length_seconds=self._full_history_seconds,
                agent_ids=agent_ids,
                task_ids=task_ids,
            )

        return getter

    def _update_cache_with(self, mesh: MeshResults) -> None:
        current_mesh = self._get_mesh()

        if current_mesh.same_agents(mesh):
            logger.debug("Incremental cache update")
            new_mesh = deepcopy(current_mesh)
            new_mesh.incremental_update(mesh)
        else:
            logger.debug("New mesh test configuration detected. Full cache update")
            new_mesh = mesh

        with self._mesh_lock:
            self._mesh_cache = new_mesh

    def _get_mesh(self) -> MeshResults:
        with self._mesh_lock:
            return self._mesh_cache
