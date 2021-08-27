from typing import Protocol

from domain.model import MeshResults


class MeshUpdatePolicy(Protocol):
    """
    MeshUpdatePolicy fetches an update
    """

    def get_update(self, mesh: MeshResults) -> MeshResults:
        pass
