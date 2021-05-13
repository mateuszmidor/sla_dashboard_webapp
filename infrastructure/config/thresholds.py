from typing import Any, Dict, Optional

from infrastructure.config.threshold_override import ThresholdOverride


class Thresholds:
    """ Thresholds implements domain.config.thresholds.Thresholds protocol """

    def deteriorated(self, from_agent_id: int, to_agent_id: int) -> int:
        override = self._get_override_or_none(from_agent_id, to_agent_id)
        if override is None or override.deteriorated is None:
            return self._default_deteriorated
        return override.deteriorated

    def failed(self, from_agent_id: int, to_agent_id: int) -> int:
        override = self._get_override_or_none(from_agent_id, to_agent_id)
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
            self._default_deteriorated = int(config["defaults"]["deteriorated"])
            self._default_failed = int(config["defaults"]["failed"])

            # read overrides config (optional)
            self._overrides: Dict[int, Dict[int, ThresholdOverride]] = dict()
            if "overrides" not in config:
                return

            for override in config["overrides"]:
                from_agent = int(override["from"])
                to_agent = int(override["to"])
                if "deteriorated" in override:
                    self._override_deteriorated(from_agent, to_agent, int(override["deteriorated"]))
                if "failed" in override:
                    self._override_failed(from_agent, to_agent, int(override["failed"]))
        except KeyError as err:
            raise Exception(f"Incomplete configuration: {err}")

    def _override_deteriorated(self, from_agent: int, to_agent: int, value: int) -> None:
        override = self._get_or_create_override(from_agent, to_agent)
        override.deteriorated = value

    def _override_failed(self, from_agent: int, to_agent: int, value: int) -> None:
        override = self._get_or_create_override(from_agent, to_agent)
        override.failed = value

    def _get_or_create_override(self, from_agent: int, to_agent: int) -> ThresholdOverride:
        overrides = self._overrides
        if from_agent not in overrides:
            overrides[from_agent] = dict()
        if to_agent not in overrides[from_agent]:
            overrides[from_agent][to_agent] = ThresholdOverride()
        return overrides[from_agent][to_agent]

    def _get_override_or_none(self, from_agent: int, to_agent: int) -> Optional[ThresholdOverride]:
        overrides = self._overrides
        if from_agent not in overrides:
            return None
        if to_agent not in overrides[from_agent]:
            return None
        return overrides[from_agent][to_agent]
