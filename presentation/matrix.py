from typing import Dict, List

from domain.model import MeshColumn, MeshResults


class Matrix:
    """
    Matrix holds "fromAgent" -> "toAgent" network connection metrics.
    It simplifies rendering test matrix table.
    Usage: matrix.cells["delhi"]["colombo"].latency
    """

    def __init__(self, mesh: MeshResults) -> None:
        agents: List[str] = []
        for row in mesh.rows:
            agents.append(row.agent_alias)
        self.agents = agents

        cells: Dict[str, Dict[str, MeshColumn]] = {}
        for row in mesh.rows:
            cells[row.agent_alias] = {}
            for col in row.columns:
                cells[row.agent_alias][col.agent_alias] = col
        self.cells = cells
