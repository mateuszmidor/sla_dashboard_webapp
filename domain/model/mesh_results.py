from typing import List

from domain.model.mesh_row import MeshRow


class MeshResults:
    """ Internal representation of Mesh Test results; independent of source data structure like http or grpc synthetics client """

    def __init__(self) -> None:
        self.rows: List[MeshRow] = []

    def append_row(self, row: MeshRow) -> None:
        self.rows.append(row)
