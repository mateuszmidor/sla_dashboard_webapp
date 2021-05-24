from typing import Protocol

from domain.types import AgentID, Threshold


class Thresholds(Protocol):
    """ Thresholds provides values of warning and error thresholds specific to given agent pairs """

    def warning(self, from_agent: AgentID, to_agent: AgentID) -> Threshold:
        pass

    def error(self, from_agent: AgentID, to_agent: AgentID) -> Threshold:
        pass
