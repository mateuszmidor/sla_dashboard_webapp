import logging
from typing import Tuple

import yaml

from domain.config import Matrix, defaults
from domain.geo import DistanceUnit
from domain.types import TestID
from infrastructure.config.thresholds import Thresholds


class ConfigYAML:
    """ConfigYAML implements domain.config.config.Config protocol"""

    @property
    def test_id(self) -> TestID:
        return self._test_id

    @property
    def data_request_interval_periods(self) -> int:
        return self._data_request_interval_periods

    @property
    def data_history_length_periods(self) -> int:
        return self._data_history_length_periods

    @property
    def data_min_periods(self) -> int:
        return self._data_min_periods

    @property
    def latency(self) -> Thresholds:
        return self._latency

    @property
    def jitter(self) -> Thresholds:
        return self._jitter

    @property
    def packet_loss(self) -> Thresholds:
        return self._packet_loss

    @property
    def timeout(self) -> Tuple[float, float]:
        return self._timeout  # type: ignore

    @property
    def logging_level(self) -> int:
        return self._logging_level

    @property
    def matrix(self) -> Matrix:
        return self._matrix

    @property
    def distance_unit(self) -> DistanceUnit:
        return self._distance_unit

    def __init__(self, filename: str) -> None:
        try:
            with open(filename, "r") as file:
                config = yaml.load(file, yaml.SafeLoader)

            self._test_id = TestID(config["test_id"])
            self._data_request_interval_periods = int(
                config.get("data_request_interval_periods", defaults.data_request_interval_periods)
            )
            self._data_history_length_periods = int(
                config.get("data_history_length_periods", defaults.data_history_length_periods)
            )
            self._data_min_periods = int(config.get("data_min_periods", defaults.data_min_periods))
            self._latency = Thresholds(config["thresholds"]["latency"])
            self._jitter = Thresholds(config["thresholds"]["jitter"])
            self._packet_loss = Thresholds(config["thresholds"]["packet_loss"])
            self._timeout = tuple(config.get("timeout", defaults.timeout_seconds))
            self._logging_level = self._parse_logging_level(config.get("logging_level", defaults.logging_level))
            self._matrix = Matrix(
                config["matrix"]["cell_color_healthy"],
                config["matrix"]["cell_color_warning"],
                config["matrix"]["cell_color_critical"],
                config["matrix"]["cell_color_nodata"],
            )
            self._distance_unit = DistanceUnit(config["distance_unit"])
        except Exception as err:
            raise Exception("Configuration error") from err

    def _parse_logging_level(self, level_str: str) -> int:
        try:
            return {
                "CRITICAL": logging.CRITICAL,
                "FATAL": logging.CRITICAL,
                "ERROR": logging.ERROR,
                "WARNING": logging.WARNING,
                "WARN": logging.WARNING,
                "INFO": logging.INFO,
                "DEBUG": logging.DEBUG,
            }[level_str.upper()]
        except KeyError:
            raise ValueError(f"unknown loggging level '{level_str}'")
