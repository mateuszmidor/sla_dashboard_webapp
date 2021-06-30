from dataclasses import dataclass
from enum import Enum

import great_circle_calculator.great_circle_calculator as gcc

from domain.geo import Coordinates


class DistanceUnit(Enum):
    KILOMETERS = "kilometers"
    MILES = "miles"


def calc_distance(p1: Coordinates, p2: Coordinates, unit: DistanceUnit) -> float:
    distance = gcc.distance_between_points(
        (p1.longitude, p1.latitude),
        (p2.longitude, p2.latitude),
        unit=unit.value,
        haversine=True,
    )
    return distance
