from typing import Protocol

from domain.model.mesh_results import MeshResults


class Repo(Protocol):
    """ Repo provides data access to Kentik Synthetic Tests """

    def get_mesh_test_results(self, test_id: str, results_lookback_minutes: int) -> MeshResults:
        pass
