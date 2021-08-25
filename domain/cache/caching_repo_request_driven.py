import logging

from domain.cache.cached_mesh_results import CachedMeshResults
from domain.cache.connection_update_policy_replace import ConnectionUpdatePolicyReplace
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

    def __init__(
        self,
        source_repo: Repo,
        monitored_test_id: TestID,
        max_data_age_seconds,
        data_request_interval_seconds: int,
        data_lookback_seconds: int,
    ) -> None:
        self._source_repo = source_repo
        self._test_id = monitored_test_id
        self._max_data_age_seconds = max_data_age_seconds
        self._data_lookback_seconds = data_lookback_seconds
        self._cached_mesh = CachedMeshResults(ConnectionUpdatePolicyReplace())
        self._rate_limiter = RateLimiter(data_request_interval_seconds)

    def get_mesh_results_all_connections(self) -> MeshResults:
        """
        Get results for all connections but with minimum lookback time (without timeseries data)
        """

        updater = MeshUpdatePolicyAllConnections(
            self._source_repo,
            self._test_id,
            self._data_lookback_seconds,
            self._max_data_age_seconds,
        )
        return self._get_or_update(updater)

    def get_mesh_results_single_connection(self, from_agent, to_agent: AgentID) -> MeshResults:
        """
        Get results for single connection but with full lookback time (with timeseries data)
        """

        updater = MeshUpdatePolicySingleConnection(
            self._source_repo,
            self._test_id,
            self._data_lookback_seconds,
            self._max_data_age_seconds,
            from_agent,
            to_agent,
        )
        return self._get_or_update(updater)

    def _get_or_update(self, policy: MeshUpdatePolicy) -> MeshResults:
        cached_mesh = self._cached_mesh.get_copy()

        if not self._rate_limiter.check_and_update():
            logger.debug("Minimum update interval %s not satisfied. Returning cached data", self._rate_limiter.inverval)
            return cached_mesh

        if not policy.need_update(cached_mesh):
            logger.debug("Cache fresh enough. Returning cached data")
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
