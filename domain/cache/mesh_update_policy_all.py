import logging
from datetime import datetime, timedelta, timezone

from domain.model.mesh_results import MeshResults
from domain.repo import Repo
from domain.types import TestID

logger = logging.getLogger(__name__)


class MeshUpdatePolicyAllConnections:
    """
    Implements MeshUpdatePolicy
    Get an update for every connection, with no timeseries data to minimize response payload
    """

    def __init__(self, repo: Repo, test_id: TestID, min_history_seconds, max_data_age_seconds: int) -> None:
        self._repo = repo
        self._test_id = test_id
        self._max_data_age_seconds = max_data_age_seconds
        self._min_history_seconds = min_history_seconds

    def need_update(self, mesh: MeshResults) -> bool:
        if not mesh.data_complete():
            return True

        oldest_timestamp = mesh.utc_timestamp_oldest
        if not oldest_timestamp:
            return True
        max_age = timedelta(seconds=self._max_data_age_seconds)
        return datetime.now(timezone.utc) - oldest_timestamp > max_age

    def get_update(self, _: MeshResults) -> MeshResults:
        logger.debug("History: %ds", self._min_history_seconds)
        return self._repo.get_mesh_test_results(self._test_id, [], [], self._min_history_seconds, True)
