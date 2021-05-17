import logging
import threading
from copy import deepcopy
from datetime import datetime

from domain.model.mesh_results import MeshResults
from domain.repo import Repo

logger = logging.getLogger(__name__)


class CachedRepo:
    """ CachedRepo allows for thread-safe, periodic updates of the repo data """

    NEVER_UPDATED = datetime(1970, 1, 1)

    def __init__(self, source_repo: Repo, monitored_test_id: str) -> None:
        self._source_repo = source_repo
        self._test_id = monitored_test_id
        self._test_results = MeshResults()
        self._update_timestamp = CachedRepo.NEVER_UPDATED
        self._repo_access_lock = threading.Lock()

    def update(self, lookback_seconds: int) -> None:
        """ update is intended to be called periodically from an update thread """

        try:
            results = self._source_repo.get_mesh_test_results(self._test_id, lookback_seconds)
            with self._repo_access_lock:
                self._test_results = results
            self._update_timestamp = datetime.now()
        except Exception as err:
            raise Exception(f"error updating repository data: {err}")

    def data_timestamp(self) -> datetime:
        return self._update_timestamp

    def get_mesh_test_results(self) -> MeshResults:
        with self._repo_access_lock:
            return deepcopy(self._test_results)
