from typing import List

from domain.model import HealthItem, MeshResults
from domain.types import AgentID


class ConnectionHealthData:
    """Represents connection health observations for given from->to connection"""

    def __init__(self, from_agent, to_agent: AgentID, mesh: MeshResults) -> None:
        self.items = ConnectionHealthData._extract_health(mesh, from_agent, to_agent)

    @staticmethod
    def _extract_health(input: MeshResults, from_agent, to_agent: AgentID) -> List[HealthItem]:
        """ Find health time series for givent from_agent->to_agent connection """

        for input_row in input.rows:
            if input_row.agent_id != from_agent:
                continue
            for input_col in input_row.columns:
                if input_col.agent_id == to_agent:
                    return input_col.health

        return []
