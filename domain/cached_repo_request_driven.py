import logging
import threading
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Optional

from domain.model.mesh_results import MeshResults
from domain.repo import Repo
from domain.types import AgentID, TaskID, TestID

logger = logging.getLogger(__name__)


class CachedRepoRequestDriven:
    """
    CachedRepoRequestDriven allows for automatic, thread-safe cached data updates
    when the data is requested and cache is older than 'max_data_age_seconds'.
    get_mesh_results_all_connections() allows to get and cache test results for all connections but without timeseries data
    get_mesh_results_single_connection() allows to get and update cache with timeseries data for given connection
    """

    TIMESTAMP_NEVER_UPDATED = datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)

    def __init__(
        self, source_repo: Repo, monitored_test_id: TestID, max_data_age_seconds: int, lookback_seconds: int
    ) -> None:
        self._source_repo = source_repo
        self._test_id = monitored_test_id
        self._max_data_age_seconds = max_data_age_seconds
        self._lookback_seconds = lookback_seconds
        self._cache_access_lock = threading.Lock()
        self._cache_test_results = MeshResults(self.TIMESTAMP_NEVER_UPDATED)

    def get_mesh_results_all_connections(self) -> MeshResults:
        """
        Get results for all connections but with minimum lookback time (without timeseries data)
        """

        self._update_cache_all_connections_if_needed()
        with self._cache_access_lock:
            return deepcopy(self._cache_test_results)

    def get_mesh_results_single_connection(self, from_agent, to_agent: AgentID) -> MeshResults:
        """
        Get results for single connection but with full lookback time (with timeseries data)
        Prerequisite: get_mesh_results_all_connections was executed before, so now incremental update can be used
        """

        self._update_cache_single_connection_if_needed(from_agent, to_agent)
        with self._cache_access_lock:
            return deepcopy(self._cache_test_results)

    def _update_cache_all_connections_if_needed(self) -> None:
        if self._cached_data_all_connections_fresh_enough():
            return

        logger.debug("Updating cache all connections start...")
        lookback = self.get_minimum_lookback_seconds()
        logger.debug("Lookback: %ds", lookback)
        try:
            results = self._source_repo.get_mesh_test_results(self._test_id, [], [], lookback, True)
            self._update_cache_with(results)
            logger.debug(
                "Updating data cache finished with %d items", results.connection_matrix.num_connections_with_data()
            )
        except Exception as err:
            logger.exception("Updating cache all connections error")

    def _cached_data_all_connections_fresh_enough(self) -> bool:
        with self._cache_access_lock:
            oldest_timestamp = self._cache_test_results.utc_timestamp_low
        if not oldest_timestamp:
            return False
        max_age = timedelta(seconds=self._max_data_age_seconds)
        return datetime.now(timezone.utc) - oldest_timestamp <= max_age

    def _update_cache_single_connection_if_needed(self, from_agent, to_agent: AgentID) -> None:
        if self._cached_data_single_connection_complete_and_fresh_enough(from_agent, to_agent):
            return

        logger.debug("Updating cache single connection start...")
        lookback = self._lookback_seconds
        logger.debug("Lookback: %ds", lookback)
        try:
            task_id = self._get_task_id(to_agent)
            task_ids = [task_id] if task_id else []  # only filter by "to_agent" if task_id is known
            results = self._source_repo.get_mesh_test_results(self._test_id, [from_agent], task_ids, lookback, True)
            self._update_cache_with(results)
            logger.debug(
                "Updating data cache finished with %d items", results.connection_matrix.num_connections_with_data()
            )
        except Exception as err:
            logger.exception("Updating cache single connection error")

    def _cached_data_single_connection_complete_and_fresh_enough(self, from_agent, to_agent: AgentID) -> bool:
        with self._cache_access_lock:
            conn = self._cache_test_results.connection(from_agent, to_agent)
            if not conn.health:
                return False
            newest_timestamp = conn.health[0].timestamp
            oldest_timestamp = conn.health[-1].timestamp

        # check cached data covers expected timespan
        cached_data_timespan = newest_timestamp - oldest_timestamp
        min_lookback = self.get_minimum_lookback_seconds()
        expected_data_timespan = timedelta(seconds=self._lookback_seconds - min_lookback)  # reduced by min_lookback
        if cached_data_timespan < expected_data_timespan:
            return False

        # check cached data is fresh enough
        max_age = timedelta(seconds=self._max_data_age_seconds)
        return datetime.now(timezone.utc) - newest_timestamp <= max_age

    def _get_task_id(self, agent_id: AgentID) -> Optional[TaskID]:
        with self._cache_access_lock:
            agent_ip = self._cache_test_results.agents.get_by_id(agent_id).ip
            task = self._cache_test_results.tasks.get_by_ip(agent_ip)
            if not task:
                logger.debug("TaskID for AgentID '%s' not found", agent_id)
                return None

        return task.id

    def _update_cache_with(self, results: MeshResults) -> None:
        with self._cache_access_lock:
            if self._cache_test_results.same_configuration(results):
                logger.debug("Incremental cache update")
                self._cache_test_results.incremental_update(results)
            else:
                logger.debug("New mesh test configuration detected. Full cache update")
                self._cache_test_results = results

    def get_minimum_lookback_seconds(self) -> int:
        """
        Minimum time window so that entire connection matrix is populated, but without extensive timeseries data for each connection
        """

        # if test data is updated every 60s,
        # fetch data history 120s back to make sure at least 1 sample was collected in requested time window
        UPDATE_PERIOD_MULTIPLIER = 2

        # use default if configuration is not available
        UPDATE_PERIOD_DEFAULT_SECONDS = 60

        # check maximum test update period config in cache, if available
        with self._cache_access_lock:
            update_period = self._cache_test_results.max_test_period_seconds
        if update_period:
            logger.debug("Got maximum test period config from cache: %ds", update_period)
            return update_period * UPDATE_PERIOD_MULTIPLIER

        # fallback to asking the server; this should happen only the first time, when there is no cached config available
        results = self._source_repo.get_mesh_test_results(self._test_id, [], [], self._lookback_seconds, False)
        update_period = results.max_test_period_seconds
        if update_period:
            logger.debug("Got maximum test period config from server: %ds", update_period)
            return update_period * UPDATE_PERIOD_MULTIPLIER

        # fallback to default test period
        logger.warning("Test update period config not available. Using default of %ds", UPDATE_PERIOD_DEFAULT_SECONDS)
        return UPDATE_PERIOD_DEFAULT_SECONDS * UPDATE_PERIOD_MULTIPLIER
