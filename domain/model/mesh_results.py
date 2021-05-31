from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from domain.types import AgentID, MetricValue


@dataclass
class Metric:
    """ Represents single from->to connection metric """

    health: str  # "healthy", "warning", ...
    value: MetricValue


@dataclass
class HealthItem:
    """Represents single from->to connection health timeseries entry"""

    jitter_millisec: MetricValue
    latency_millisec: MetricValue
    packet_loss_percent: MetricValue
    time: datetime


@dataclass
class MeshColumn:
    """ Represents connection "to" endpoint """

    agent_name: str
    agent_alias: str
    agent_id: AgentID
    target_ip: str
    jitter_millisec: Metric
    latency_millisec: Metric
    packet_loss_percent: Metric
    health: List[HealthItem]


@dataclass
class MeshRow:
    """ Represents connection "from" endpoint """

    agent_name: str
    agent_alias: str
    agent_id: AgentID
    ip: str
    local_ip: str
    columns: List[MeshColumn]


class Agents:
    def __init__(self, rows: List[MeshRow]) -> None:
        self._rows = rows

    def get_id(self, alias: str) -> AgentID:
        for row in self._rows:
            if row.agent_alias == alias:
                return row.agent_id
        return AgentID()

    def get_alias(self, id: AgentID) -> str:
        for row in self._rows:
            if row.agent_id == id:
                return row.agent_alias
        return f"[agent_id={id} not found]"


class MeshResults:
    """Internal representation of Mesh Test results; independent of source data structure like http or grpc synthetics client"""

    def __init__(self, utc_timestamp: Optional[datetime] = None) -> None:
        if utc_timestamp is None:
            utc_timestamp = datetime.now(timezone.utc)

        self.utc_timestamp = utc_timestamp
        self.rows: List[MeshRow] = []
        self.agents = Agents(self.rows)

    def append_row(self, row: MeshRow) -> None:
        self.rows.append(row)
