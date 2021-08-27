import logging

from domain.model.mesh_results import MeshResults
from domain.repo import Repo
from domain.types import TestID

logger = logging.getLogger(__name__)


class MeshUpdatePolicyAllConnections:
    """
    Implements MeshUpdatePolicy
    Get an update for every connection, with no timeseries data to minimize response payload
    """

    def __init__(self, repo: Repo, test_id: TestID, min_history_seconds) -> None:
        self._repo = repo
        self._test_id = test_id
        self._min_history_seconds = min_history_seconds

    def get_update(self, _: MeshResults) -> MeshResults:
        logger.debug("History: %ds", self._min_history_seconds)
        return self._repo.get_mesh_test_results(self._test_id, [], [], self._min_history_seconds, True)
