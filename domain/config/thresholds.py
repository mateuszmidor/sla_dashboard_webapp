from typing import Protocol

from domain.types import AgentID, Threshold


class Thresholds(Protocol):
    """ Thresholds provides values of deteriorated and failed thresholds specific to given agent pairs """

    def deteriorated(self, from_agent: AgentID, to_agent: AgentID) -> Threshold:
        pass

    def failed(self, from_agent: AgentID, to_agent: AgentID) -> Threshold:
        pass
