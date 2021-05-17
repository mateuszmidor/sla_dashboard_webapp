from dataclasses import dataclass
from typing import List

from domain.types import AgentID


@dataclass
class Metric:
    """ Represents single from->to connection metric """

    health: str  # "healthy", "warning", ...
    value: int  # latency in microseconds, jitter in microseconds, packet_loss in percents (0-100)


@dataclass
class MeshColumn:
    """ Represents connection "to" endpoint """

    agent_name: str
    agent_alias: str
    agent_id: AgentID
    target_ip: str
    jitter_microsec: Metric
    latency_microsec: Metric
    packet_loss_percent: Metric


@dataclass
class MeshRow:
    """ Represents connection "from" endpoint """

    agent_name: str
    agent_alias: str
    agent_id: AgentID
    ip: str
    local_ip: str
    columns: List[MeshColumn]


class MeshResults:
    """Internal representation of Mesh Test results; independent of source data structure like http or grpc synthetics client"""

    def __init__(self) -> None:
        self.rows: List[MeshRow] = []

    def append_row(self, row: MeshRow) -> None:
        self.rows.append(row)
