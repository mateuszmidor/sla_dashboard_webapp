from dataclasses import dataclass
from typing import List


@dataclass
class Metric:
    health: str
    value: int


@dataclass
class MeshColumn:
    name: str
    alias: str
    target: str  # ip address
    jitter: Metric
    latency_microsec: Metric
    packet_loss: Metric


@dataclass
class MeshRow:
    name: str
    alias: str
    id: str
    ip: str
    local_ip: str
    columns: List[MeshColumn]


class MeshResults:
    """Internal representation of Mesh Test results; independent of source data structure like http or grpc synthetics client"""

    def __init__(self) -> None:
        self.rows: List[MeshRow] = []

    def append_row(self, row: MeshRow) -> None:
        self.rows.append(row)
