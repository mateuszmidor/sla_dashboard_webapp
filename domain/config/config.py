from typing import Protocol

from domain.config.matrix import Matrix
from domain.config.thresholds import Thresholds
from domain.geo import DistanceUnit
from domain.metric import MetricType
from domain.types import TestID


class Config(Protocol):
    """Config provides persistent app configuration"""

    @property
    def test_id(self) -> TestID:
        """ID of the test to display data matrix for"""
        pass

    @property
    def data_request_interval_periods(self) -> int:
        """Minimum interval between asking the server for data. In test update periods. This is to save request quota."""
        pass

    @property
    def data_history_length_periods(self) -> int:
        """Number of test update periods into the past to fetch the results for"""
        pass

    @property
    def data_min_periods(self) -> int:
        """Number of test update periods into the past to get most recent measurement"""
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
    def logging_level(self) -> int:
        """Logging verbosity"""
        pass

    @property
    def agent_label(self) -> str:
        """Agent label format string. Available fields: [name, alias, id, ip]"""
        pass

    @property
    def distance_unit(self) -> DistanceUnit:
        """Unit for distance between agents"""
        pass

    @property
    def show_measurement_values(self) -> bool:
        """Show measurement values in matrix cells"""
        pass

    @property
    def default_metric(self) -> MetricType:
        """MetricType to display when not explicitly specified in matrix view query string"""
        pass
