from typing import Protocol

from domain.model import MeshResults


class MeshUpdatePolicy(Protocol):
    """
    MeshUpdatePolicy determines if update for given mesh is needed and fetches an update
    """

    def need_update(self, mesh: MeshResults) -> bool:
        pass

    def get_update(self, mesh: MeshResults) -> MeshResults:
        pass
