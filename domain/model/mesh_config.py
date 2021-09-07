from dataclasses import dataclass

from domain.model.agents import Agents


@dataclass
class MeshConfig:
    agents: Agents = Agents()
    update_period_seconds: int = int()  # test update period
