from typing import Protocol

from domain.config.matrix import Matrix
from domain.config.thresholds import Thresholds
from domain.geo import DistanceUnit
from domain.types import TestID


class Config(Protocol):
    """Config provides persistent app configuration"""

    @property
    def test_id(self) -> TestID:
        """ID of the test to display data matrix for"""
        pass

    @property
    def max_data_age_seconds(self) -> int:
        """Maximum age of the data in the matrix before cache update should be triggered"""
        pass

    @property
    def data_request_interval_seconds(self) -> int:
        """Minimum interval between asking the server for data. This is to save request quota."""
        pass

    @property
    def data_update_lookback_seconds(self) -> int:
        """Time window to fetch the test results for"""
        pass

    @property
    def latency(self) -> Thresholds:
        """Latency thresholds, in milliseconds"""
        pass

    @property
    def jitter(self) -> Thresholds:
        """Jitter thresholds, in milliseconds"""
        pass

    @property
    def packet_loss(self) -> Thresholds:
        """Packet loss thresholds, in percents (0-100)"""
        pass

    @property
    def matrix(self) -> Matrix:
        """Matrix cell colors"""
        pass

    @property
    def distance_unit(self) -> DistanceUnit:
        """Unit for distance between agents"""
        pass
