from typing import List, Dict
from domain.model import MeshResults, MeshColumn


class Matrix:
    """
    Matrix holds "fromAgent" -> "toAgent" network connection metrics.
    It simplifies rendering test matrix table.
    Usage: matrix.cells["delhi"]["colombo"].latency
    """

    def __init__(self, mesh: MeshResults) -> None:
        agents: List[str] = []
        for row in mesh.rows:
            agents.append(row.alias)
        self.agents = agents

        cells: Dict[str, Dict[str, MeshColumn]] = {}
        for row in mesh.rows:
            cells[row.alias] = {}
            for col in row.columns:
                cells[row.alias][col.alias] = col
        self.cells = cells
