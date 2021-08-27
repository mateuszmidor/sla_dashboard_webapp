import threading
from copy import deepcopy

from domain.model import MeshResults


class CachedMeshResults:
    def __init__(self) -> None:
        self._mesh = MeshResults()
        self._lock = threading.Lock()

    def can_incremental_update(self, src: MeshResults) -> bool:
        with self._lock:
            return self._mesh.same_agents(src)

    def incremental_update(self, src: MeshResults) -> None:
        copy = self.get_copy()
        copy.incremental_update(src)
        with self._lock:
            self._mesh = copy

    def full_update(self, src: MeshResults) -> None:
        with self._lock:
            self._mesh = deepcopy(src)

    def get_copy(self) -> MeshResults:
        with self._lock:
            return deepcopy(self._mesh)

    def get_read_only(self) -> MeshResults:
        # TODO: forbid updating the returned data
        with self._lock:
            return self._mesh

    def __enter__(self):
        self._lock.acquire()
        return self._mesh

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()
