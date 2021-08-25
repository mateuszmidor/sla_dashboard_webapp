import logging

from domain.model.mesh_results import MeshResults
from domain.repo import Repo
from domain.types import TestID

logger = logging.getLogger(__name__)


class MinmumLookbackEvaluator:
    def __init__(self, repo: Repo, test_id: TestID, lookback_seconds: int) -> None:
        self._repo = repo
        self._test_id = test_id
        self._lookback_seconds = lookback_seconds

    def minimum_lookback_seconds(self, mesh: MeshResults) -> int:
        """
        Minimum lookback so that samples for all connections in mesh test are returned,
        but without extensive timeseries data for each connection
        """

        # if test update period is 60s,
        # fetch test data history 120s back to make sure at least 1 sample was collected in requested time window
        UPDATE_PERIOD_MULTIPLIER = 2

        # default test update period, if configuration is not available
        UPDATE_PERIOD_DEFAULT_SECONDS = 60

        # check maximum test update period config, if available
        update_period = mesh.max_test_period_seconds
        if update_period:
            logger.debug("Got maximum test period config from cache: %ds", update_period)
            return update_period * UPDATE_PERIOD_MULTIPLIER

        # fallback to asking the server; this should happen only the first time, when there is no config available yet
        results = self._repo.get_mesh_test_results(self._test_id, [], [], self._lookback_seconds, False)
        update_period = results.max_test_period_seconds
        if update_period:
            logger.debug("Got maximum test period config from server: %ds", update_period)
            return update_period * UPDATE_PERIOD_MULTIPLIER

        # fallback to default test period
        logger.warning("Test update period config not available. Using default of %ds", UPDATE_PERIOD_DEFAULT_SECONDS)
        return UPDATE_PERIOD_DEFAULT_SECONDS * UPDATE_PERIOD_MULTIPLIER
