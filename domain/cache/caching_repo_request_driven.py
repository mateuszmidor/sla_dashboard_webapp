import logging
import threading
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional, Tuple

from domain.model.mesh_config import MeshConfig
from domain.model.mesh_results import MeshResults
from domain.rate_limiter import RateLimiter
from domain.repo import Repo
from domain.types import AgentID, TaskID, TestID

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
        config = source_repo.get_mesh_config(self._test_id)
        test_update_period_seconds = config.update_period_seconds
        self._min_history_seconds = test_update_period_seconds * data_min_periods
        self._full_history_seconds = data_history_length_periods * test_update_period_seconds
        self._rate_limiter = RateLimiter(data_request_interval_periods * test_update_period_seconds)
        self._mesh_config = config
        self._mesh_results = MeshResults()
        self._mesh_lock = threading.Lock()

    @property
    def min_history_seconds(self) -> int:
        return self._min_history_seconds

    def get_mesh_config(self) -> MeshConfig:
        return self._get_config()

    def get_mesh_results_all_connections(self) -> MeshResults:
        """
        Get results for all connections but with minimum history data
        """

        if not self._rate_limiter.check_and_update():
            logger.debug("Returning cached data (minimum update interval: %ds)", self._rate_limiter.interval_seconds)
            return self._get_results()

        getter = self._get_all_connections()
        return self._update(getter)

    def get_mesh_results_single_connection(self, from_agent: AgentID, to_agent: AgentID) -> MeshResults:
        """
        Get results for single connection but with full history data
        """

        if not self._rate_limiter.check_and_update(f"{from_agent}:{to_agent}"):
            logger.debug("Returning cached data (minimum update interval: %ds)", self._rate_limiter.interval_seconds)
            return self._get_results()

        getter = self._get_single_connection(from_agent, to_agent)
        return self._update(getter)

    def _update(self, get_mesh_update: Callable[[], Tuple[MeshResults, MeshConfig]]) -> MeshResults:
        """Condition: returned MeshResults is only read and never modified"""

        try:
            logger.debug("Mesh cache update start...")
            fresh_mesh, fresh_config = get_mesh_update()
            self._update_cache_with(fresh_mesh, fresh_config)
            num_fresh_items = fresh_mesh.connection_matrix.num_connections_with_data()
            logger.debug("Mesh cache update finished with %d fresh items", num_fresh_items)
        except Exception:
            logger.exception("Mesh cache update error")

        return self._get_results()

    def _get_all_connections(self) -> Callable[[], Tuple[MeshResults, MeshConfig]]:
        def getter() -> Tuple[MeshResults, MeshConfig]:
            logger.debug("History: %ds", self.min_history_seconds)
            return (
                self._source_repo.get_mesh_test_results(
                    test_id=self._test_id, history_length_seconds=self.min_history_seconds
                ),
                self._source_repo.get_mesh_config(test_id=self._test_id),
            )

        return getter

    def _get_single_connection(
        self, from_agent: AgentID, to_agent: AgentID
    ) -> Callable[[], Tuple[MeshResults, MeshConfig]]:
        def getter() -> Tuple[MeshResults, MeshConfig]:
            logger.debug("History: %ds", self._full_history_seconds)
            agent_ids = [from_agent]
            task_id = self._agent_id_to_task_id(to_agent)
            if task_id:
                task_ids = [task_id]
            else:
                logger.warning("TaskID for AgentID '%s' not found; requesting entire mesh row", to_agent)
                task_ids = []
            return (
                self._source_repo.get_mesh_test_results(
                    test_id=self._test_id,
                    history_length_seconds=self._full_history_seconds,
                    agent_ids=agent_ids,
                    task_ids=task_ids,
                ),
                self._source_repo.get_mesh_config(test_id=self._test_id),
            )

        return getter

    def _agent_id_to_task_id(self, agent_id: AgentID) -> Optional[TaskID]:
        agent_ip = self._get_config().agents.get_by_id(agent_id).ip
        task = self._get_results().tasks.get_by_ip(agent_ip)
        return task.id if task else None

    def _update_cache_with(self, results: MeshResults, config: MeshConfig) -> None:
        current_config = self._get_config()
        current_results = self._get_results()

        if current_config.agents.equals(config.agents):
            logger.debug("Incremental cache update")
            new_results = deepcopy(current_results)
            new_results.incremental_update(results)
            self._drop_samples_outside_timewindow(new_results)
            new_config = current_config
        else:
            logger.debug("New mesh test configuration detected. Full cache update")
            new_results = results
            new_config = config

        with self._mesh_lock:
            self._mesh_results = new_results
            self._mesh_config = new_config
            self._mesh_config.agents.update_names_aliases(new_results.participating_agents)

    def _get_results(self) -> MeshResults:
        with self._mesh_lock:
            return self._mesh_results

    def _get_config(self) -> MeshConfig:
        with self._mesh_lock:
            return self._mesh_config

    def _drop_samples_outside_timewindow(self, results: MeshResults) -> None:
        threshold = datetime.now(timezone.utc) - timedelta(seconds=self._full_history_seconds)
        results.connection_matrix.drop_samples_older_than(threshold)
