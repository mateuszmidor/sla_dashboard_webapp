import toml


class ConfigTOML:
    """ ConfigTOML implements domain.config.Config protocol """

    def __init__(self, filename: str) -> None:
        with open(filename, "r") as file:
            config = toml.load(file)

        self._test_id = str(config["DEFAULT"]["test_id"])
        self._latency_deteriorated_ms = int(config["DEFAULT"]["latency_deteriorated_ms"])  # lower bound
        self._latency_failed_ms = int(config["DEFAULT"]["latency_failed_ms"])  # lower bound
        self._data_update_period_seconds = int(config["DEFAULT"]["data_update_period_seconds"])
        self._data_update_lookback_minutes = int(config["DEFAULT"]["data_update_lookback_minutes"])

    @property
    def test_id(self) -> str:
        return self._test_id

    @property
    def latency_deteriorated_ms(self) -> int:
        return self._latency_deteriorated_ms

    @property
    def latency_failed_ms(self) -> int:
        return self._latency_failed_ms

    @property
    def data_update_period_seconds(self) -> int:
        return self._data_update_period_seconds

    @property
    def data_update_lookback_minutes(self) -> int:
        return self._data_update_lookback_minutes
