import threading
from copy import deepcopy

from domain.model import MeshResults
from domain.model.mesh_results import ConnectionUpdatePolicy


class CachedMeshResults:
    def __init__(self, update_policy: ConnectionUpdatePolicy) -> None:
        self._mesh = MeshResults()
        self._lock = threading.RLock()
        self._connection_update_policy = update_policy

    def can_incremental_update(self, src: MeshResults) -> bool:
        with self._lock:
            return self._mesh.same_configuration(src)

    def incremental_update(self, src: MeshResults) -> None:
        with self._lock:
            self._mesh.incremental_update(src, self._connection_update_policy)

    def full_update(self, src: MeshResults) -> None:
        with self._lock:
            self._mesh = deepcopy(src)

    def get_copy(self) -> MeshResults:
        with self._lock:
            return deepcopy(self._mesh)

    def __enter__(self):
        self._lock.acquire()
        return self._mesh

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()
