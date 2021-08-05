from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from domain.geo import Coordinates
from domain.metric_type import MetricType
from domain.types import AgentID, MetricValue


@dataclass
class Agent:
    id: AgentID = AgentID()
    ip: str = ""
    name: str = ""
    alias: str = ""
    coords: Coordinates = Coordinates()


class Agents:
    def __init__(self) -> None:
        self._agents: Dict[AgentID, Agent] = {}

    def equals(self, other: Agents) -> bool:
        return self._agents == other._agents

    def get_by_id(self, agent_id: AgentID) -> Agent:
        if agent_id in self._agents:
            return self._agents[agent_id]
        return Agent()

    def get_by_alias(self, alias: str) -> Agent:
        for _, v in self._agents.items():
            if v.alias == alias:
                return v
        return Agent()

    def get_alias(self, agent_id: AgentID) -> str:
        agent = self.get_by_id(agent_id)
        if agent.id == AgentID():
            return f"[agent_id={agent_id} not found]"
        return agent.alias

    def insert(self, agent: Agent) -> None:
        self._agents[agent.id] = agent


@dataclass
class Metric:
    """Represents single from->to connection metric"""

    health: str = ""  # "healthy", "warning", ...
    value: MetricValue = MetricValue()


@dataclass
class HealthItem:
    """Represents single from->to connection health time-series entry"""

    jitter_millisec: MetricValue
    latency_millisec: MetricValue
    packet_loss_percent: MetricValue
    time: datetime


@dataclass
class MeshColumn:
    """Represents connection "to" endpoint"""

    agent_id: AgentID = AgentID()
    jitter_millisec: Metric = Metric()
    latency_millisec: Metric = Metric()
    packet_loss_percent: Metric = Metric()
    health: List[HealthItem] = field(default_factory=list)
    last_updated_utc: datetime = datetime(year=1970, month=1, day=1)

    def has_no_data(self) -> bool:
        return self.packet_loss_percent.value == MetricValue(100) or len(self.health) == 0


class MeshRow:
    """Represents connection "from" endpoint"""

    def __init__(self, agent_id: AgentID, columns: List[MeshColumn]):
        self._reset(agent_id, columns)

    def incremental_update(self, src: MeshRow) -> None:
        """Update with src data, add new pieces of data if any, don't remove anything"""

        for src_column in src.columns:
            col_index = self._find_column(src_column.agent_id)
            if col_index is None:
                self.columns.append(src_column)  # append new column even if there is no data
            else:
                if src_column.has_no_data() is False:  # replace existing column only if there is data
                    self.columns[col_index] = src_column
        self._reset(self.agent_id, self.columns)

    def _reset(self, agent_id: AgentID, columns: List[MeshColumn]) -> None:
        """Reset MeshRow state, enforce invariants"""

        self.agent_id = agent_id
        self.columns = sorted(columns, key=lambda x: x.agent_id)

    def _find_column(self, agent_id: AgentID) -> Optional[int]:
        for index, col in enumerate(self.columns):
            if col.agent_id == agent_id:
                return index
        return None


class ConnectionMatrix:
    """
    ConnectionMatrix holds "fromAgent" -> "toAgent" network connection metrics.
    It simplifies rendering test matrix table.
    Usage: matrix.connection("244", "532").latency_millisec
    """

    def __init__(self, rows: List[MeshRow]) -> None:
        connections: Dict[AgentID, Dict[AgentID, MeshColumn]] = {}
        for row in rows:
            connections[row.agent_id] = {}
            for col in row.columns:
                connections[row.agent_id][col.agent_id] = col
        self._connections = connections

    def connection(self, from_agent, to_agent: AgentID) -> MeshColumn:
        if from_agent not in self._connections:
            return MeshColumn()
        if to_agent not in self._connections[from_agent]:
            return MeshColumn()
        return self._connections[from_agent][to_agent]


class MeshResults:
    """
    Internal representation of Mesh Test results; independent of source data structure like http
    or grpc synthetics client
    """

    def __init__(
        self, utc_timestamp: datetime, rows: Optional[List[MeshRow]] = None, agents: Agents = Agents()
    ) -> None:
        self._reset(utc_timestamp, rows, agents)

    def incremental_update(self, src: MeshResults) -> None:
        """Update with src data, add new pieces of data if any, don't remove anything"""

        for src_row in src.rows:
            dst_row = self._get_or_add_row(src_row.agent_id)
            dst_row.incremental_update(src_row)
        self._reset(datetime.now(timezone.utc), self.rows, self.agents)

    def filter(self, from_agent, to_agent: AgentID, metric: MetricType) -> List[Tuple[datetime, MetricValue]]:
        items = self.connection(from_agent, to_agent).health

        if metric == MetricType.LATENCY:
            return [(i.time, i.latency_millisec) for i in items]
        if metric == MetricType.JITTER:
            return [(i.time, i.jitter_millisec) for i in items]
        if metric == MetricType.PACKET_LOSS:
            return [(i.time, i.packet_loss_percent) for i in items]

        return []

    def connection(self, from_agent, to_agent: AgentID) -> MeshColumn:
        return self._connection_matrix.connection(from_agent, to_agent)

    def _reset(self, utc_timestamp: datetime, rows: Optional[List[MeshRow]], agents: Agents) -> None:
        """Reset MeshResults state, enforce invariants"""

        self.utc_timestamp = utc_timestamp
        if rows is None:
            self.rows = []
        else:
            self.rows = sorted(rows, key=lambda x: x.agent_id)
        self.agents = agents
        self._connection_matrix = ConnectionMatrix(self.rows)

    def _get_or_add_row(self, agent_id: AgentID) -> MeshRow:
        # find and return row with matching agent_id
        for row in self.rows:
            if row.agent_id == agent_id:
                return row

        # row not found, append new one
        row = MeshRow(agent_id, [])
        self.rows.append(row)
        return row
