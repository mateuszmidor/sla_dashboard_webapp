import logging

from domain.cache.cached_mesh_results import CachedMeshResults
from domain.cache.mesh_update_policy import MeshUpdatePolicy
from domain.cache.mesh_update_policy_all import MeshUpdatePolicyAllConnections
from domain.cache.mesh_update_policy_single import MeshUpdatePolicySingleConnection
from domain.model.mesh_results import MeshResults
from domain.rate_limiter import RateLimiter
from domain.repo import Repo
from domain.types import AgentID, TestID

logger = logging.getLogger(__name__)


class CachingRepoRequestDriven:
    """
    CachingRepoRequestDriven allows for automatic, thread-safe cached mesh updates:
    - get_mesh_results_all_connections() allows to get and cache test results for all connections but without timeseries data
    - get_mesh_results_single_connection() allows to get and cache test results for single connection but with timeseries data
    """

    NUM_TEST_UPDATE_PERIODS_FOR_MIN_HISTORY_SECONDS = 2  # min number of periods to get data sample for each connection

    def __init__(
        self,
        source_repo: Repo,
        monitored_test_id: TestID,
        data_request_interval_seconds: int,
        data_history_seconds: int,
    ) -> None:
        self._source_repo = source_repo
        self._test_id = monitored_test_id
        self._full_history_seconds = data_history_seconds
        self._cached_mesh = CachedMeshResults()
        self._rate_limiter = RateLimiter(data_request_interval_seconds)

        test_update_period = source_repo.get_mesh_config(monitored_test_id).update_period_seconds
        self._min_history_seconds = test_update_period * self.NUM_TEST_UPDATE_PERIODS_FOR_MIN_HISTORY_SECONDS

    def get_mesh_results_all_connections(self) -> MeshResults:
        """
        Get results for all connections but with minimum history data
        """

        updater = MeshUpdatePolicyAllConnections(
            self._source_repo,
            self._test_id,
            self._min_history_seconds,
        )
        return self._get_or_update(updater)

    def get_mesh_results_single_connection(self, from_agent, to_agent: AgentID) -> MeshResults:
        """
        Get results for single connection but with full history data
        """

        updater = MeshUpdatePolicySingleConnection(
            self._source_repo,
            self._test_id,
            self._min_history_seconds,
            self._full_history_seconds,
            from_agent,
            to_agent,
        )
        return self._get_or_update(updater)

    def _get_or_update(self, policy: MeshUpdatePolicy) -> MeshResults:
        cached_mesh = self._cached_mesh.get_copy()

        if not self._rate_limiter.check_and_update():
            logger.debug(
                "Minimum update interval %ds not satisfied. Returning cached data", self._rate_limiter.interval_seconds
            )
            return cached_mesh

        policy_name = type(policy).__name__
        try:
            logger.debug("%s start...", policy_name)
            fresh_mesh = policy.get_update(cached_mesh)
            self._update_cache_with(fresh_mesh)
            num_fresh_items = fresh_mesh.connection_matrix.num_connections_with_data()
            logger.debug("%s finished with %d fresh items", policy_name, num_fresh_items)
        except Exception as err:
            logger.exception("%s error", policy_name)

        return self._cached_mesh.get_copy()

    def _update_cache_with(self, mesh: MeshResults) -> None:
        if self._cached_mesh.can_incremental_update(mesh):
            logger.debug("Incremental cache update")
            self._cached_mesh.incremental_update(mesh)
        else:
            logger.debug("New mesh test configuration detected. Full cache update")
            self._cached_mesh.full_update(mesh)
