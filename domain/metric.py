from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

MetricValue = float
""" latency and jitter in milliseconds, packet_loss in percent (0-100) """


class MetricType(Enum):
    """Available mesh test metric types"""

    LATENCY = "Latency[ms]"
    JITTER = "Jitter[ms]"
    PACKET_LOSS = "Packet loss[%]"


@dataclass
class Metric:
    type: MetricType
    value: MetricValue
    unit: str

    @classmethod
    def latency(cls, value: MetricValue, unit: str = "ms") -> Metric:
        return cls(MetricType.LATENCY, value, unit)

    @classmethod
    def jitter(cls, value: MetricValue, unit: str = "ms") -> Metric:
        return cls(MetricType.JITTER, value, unit)

    @classmethod
    def loss(cls, value: MetricValue, unit: str = "%") -> Metric:
        return cls(MetricType.PACKET_LOSS, value, unit)
