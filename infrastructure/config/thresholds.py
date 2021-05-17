from dataclasses import dataclass
from typing import Any, Dict, Optional

from domain.types import AgentID, Threshold


@dataclass
class ThresholdOverride:
    """ Threshold overrides can be optionally specified; if not specified - default values shall be used """

    deteriorated: Optional[int] = None
    failed: Optional[int] = None


class Thresholds:
    """
    Thresholds allow to read integer threshold values for given agent pair based on configuration.
    It implements domain.config.thresholds.Thresholds protocol
    """

    def deteriorated(self, from_agent: AgentID, to_agent: AgentID) -> Threshold:
        override = self._get_override_or_none(from_agent, to_agent)
        if override is None or override.deteriorated is None:
            return self._default_deteriorated
        return override.deteriorated

    def failed(self, from_agent: AgentID, to_agent: AgentID) -> Threshold:
        override = self._get_override_or_none(from_agent, to_agent)
        if override is None or override.failed is None:
            return self._default_failed
        return override.failed

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Example of config dict structure for thresholds:
        "defaults":{
            "deteriorated":200,
            "failed":400
        },
        "overrides":[
            {
            "from":10,
            "to":11,
            "deteriorated":10,
            "failed":20
            },
            {
            "from":60,
            "to":70,
            "deteriorated":1000,
            "failed":2000
            }
        ]
        """
        try:
            # read defaults config (required)
            self._default_deteriorated = Threshold(config["defaults"]["deteriorated"])
            self._default_failed = Threshold(config["defaults"]["failed"])

            # read overrides config (optional)
            self._overrides: Dict[AgentID, Dict[AgentID, ThresholdOverride]] = dict()
            if "overrides" not in config:
                return

            for override in config["overrides"]:
                from_agent = AgentID(override["from"])
                to_agent = AgentID(override["to"])
                if "deteriorated" in override:
                    self._override_deteriorated(from_agent, to_agent, Threshold(override["deteriorated"]))
                if "failed" in override:
                    self._override_failed(from_agent, to_agent, Threshold(override["failed"]))
        except KeyError as err:
            raise Exception("Incomplete thresholds definition") from err

    def _override_deteriorated(self, from_agent: AgentID, to_agent: AgentID, value: Threshold) -> None:
        override = self._get_or_create_override(from_agent, to_agent)
        override.deteriorated = value

    def _override_failed(self, from_agent: AgentID, to_agent: AgentID, value: Threshold) -> None:
        override = self._get_or_create_override(from_agent, to_agent)
        override.failed = value

    def _get_or_create_override(self, from_agent: AgentID, to_agent: AgentID) -> ThresholdOverride:
        overrides = self._overrides
        if from_agent not in overrides:
            overrides[from_agent] = dict()
        if to_agent not in overrides[from_agent]:
            overrides[from_agent][to_agent] = ThresholdOverride()
        return overrides[from_agent][to_agent]

    def _get_override_or_none(self, from_agent: AgentID, to_agent: AgentID) -> Optional[ThresholdOverride]:
        overrides = self._overrides
        if from_agent not in overrides:
            return None
        if to_agent not in overrides[from_agent]:
            return None
        return overrides[from_agent][to_agent]
