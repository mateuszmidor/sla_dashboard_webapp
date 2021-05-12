from typing import Protocol


class Config(Protocol):
    """ Config provides persistent app configuration """

    @property
    def test_id(self) -> str:
        pass

    @property
    def latency_deteriorated_ms(self) -> int:
        pass

    @property
    def latency_failed_ms(self) -> int:
        pass

    @property
    def data_update_period_seconds(self) -> int:
        pass

    @property
    def data_update_lookback_minutes(self) -> int:
        pass
