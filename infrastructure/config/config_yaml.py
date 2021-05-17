import yaml

from infrastructure.config.thresholds import Thresholds


class ConfigYAML:
    """ ConfigYAML implements domain.config.config.Config protocol """

    @property
    def test_id(self) -> str:
        return self._test_id

    @property
    def data_update_period_seconds(self) -> int:
        return self._data_update_seconds

    @property
    def data_update_lookback_seconds(self) -> int:
        return self._data_update_lookback_seconds

    @property
    def latency(self) -> Thresholds:
        return self._latency

    @property
    def jitter(self) -> Thresholds:
        return self._jitter

    @property
    def packet_loss(self) -> Thresholds:
        return self._packet_loss

    def __init__(self, filename: str) -> None:
        try:
            with open(filename, "r") as file:
                config = yaml.load(file, yaml.SafeLoader)

            self._test_id = str(config["test_id"])
            self._data_update_seconds = int(config["data_update_period_seconds"])
            self._data_update_lookback_seconds = int(config["data_update_lookback_seconds"])
            self._latency = Thresholds(config["thresholds"]["latency"])
            self._jitter = Thresholds(config["thresholds"]["jitter"])
            self._packet_loss = Thresholds(config["thresholds"]["packet_loss"])
        except Exception as err:
            raise Exception(f"Configuration error") from err
