from typing import Protocol


class Thresholds(Protocol):
    """ Thresholds provides values of deteriorated and failed thresholds specific to given agent pairs """

    def deteriorated(self, from_agent_id: int, to_agent_id: int) -> int:
        pass

    def failed(self, from_agent_id: int, to_agent_id: int) -> int:
        pass
