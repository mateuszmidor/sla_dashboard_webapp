from dataclasses import dataclass


@dataclass
class Metric:
    health: str
    value: int