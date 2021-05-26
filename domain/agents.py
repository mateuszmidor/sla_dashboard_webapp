from domain.model import MeshResults
from domain.types import AgentID


class Agents:
    def __init__(self, mesh: MeshResults) -> None:
        self._mesh = mesh

    def get_id(self, alias: str) -> AgentID:
        for row in self._mesh.rows:
            if row.agent_alias == alias:
                return row.agent_id
        return AgentID()

    def get_alias(self, id: AgentID) -> str:
        for row in self._mesh.rows:
            if row.agent_id == id:
                return row.agent_alias
        return f"[agent_id={id} not found]"
