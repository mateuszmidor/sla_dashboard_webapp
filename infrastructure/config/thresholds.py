from dataclasses import dataclass
from typing import Any, Dict, Optional

from domain.types import AgentID, Threshold


@dataclass
class ThresholdOverride:
    """ Threshold overrides can be optionally specified; if not specified - default values shall be used """

    warning: Optional[int] = None
    error: Optional[int] = None


class Thresholds:
    """
    Thresholds allow to read integer threshold values for given agent pair based on configuration.
    It implements domain.config.thresholds.Thresholds protocol
    """

    def warning(self, from_agent: AgentID, to_agent: AgentID) -> Threshold:
        override = self._get_override_or_none(from_agent, to_agent)
        if override is None or override.warning is None:
            return self._default_warning
        return override.warning

    def error(self, from_agent: AgentID, to_agent: AgentID) -> Threshold:
        override = self._get_override_or_none(from_agent, to_agent)
        if override is None or override.error is None:
            return self._default_error
        return override.error

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Example of config dict structure for thresholds:
        "defaults":{
            "warning":200,
            "error":400
        },
        "overrides":[
            {
            "from":10,
            "to":11,
            "warning":10,
            "error":20
            },
            {
            "from":60,
            "to":70,
            "warning":1000,
            "error":2000
            }
        ]
        """
        try:
            # read defaults config (required)
            self._default_warning = Threshold(config["defaults"]["warning"])
            self._default_error = Threshold(config["defaults"]["error"])

            # read overrides config (optional)
            self._overrides: Dict[AgentID, Dict[AgentID, ThresholdOverride]] = dict()
            if "overrides" not in config:
                return

            for override in config["overrides"]:
                from_agent = AgentID(override["from"])
                to_agent = AgentID(override["to"])
                if "warning" in override:
                    self._override_warning(from_agent, to_agent, Threshold(override["warning"]))
                if "error" in override:
                    self._override_error(from_agent, to_agent, Threshold(override["error"]))
        except KeyError as err:
            raise Exception("Incomplete thresholds definition") from err

    def _override_warning(self, from_agent: AgentID, to_agent: AgentID, value: Threshold) -> None:
        override = self._get_or_create_override(from_agent, to_agent)
        override.warning = value

    def _override_error(self, from_agent: AgentID, to_agent: AgentID, value: Threshold) -> None:
        override = self._get_or_create_override(from_agent, to_agent)
        override.error = value

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
