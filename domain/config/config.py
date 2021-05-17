from typing import Protocol

from domain.config.thresholds import Thresholds
from domain.types import TestID


class Config(Protocol):
    """ Config provides persistent app configuration """

    @property
    def test_id(self) -> TestID:
        """ ID of the test to display data matrix for """
        pass

    @property
    def data_update_period_seconds(self) -> int:
        """ How often to fetch fresh test results from the server """
        pass

    @property
    def data_update_lookback_seconds(self) -> int:
        """ Time window to fetch the test results for """
        pass

    @property
    def latency(self) -> Thresholds:
        """ Latency thresholds, in microseconds """
        pass

    @property
    def jitter(self) -> Thresholds:
        """ Jitter thresholds, in microseconds """
        pass

    @property
    def packet_loss(self) -> Thresholds:
        """ Packet loss thresholds, in percents (0-100) """
        pass
