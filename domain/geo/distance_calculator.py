from dataclasses import dataclass

import great_circle_calculator.great_circle_calculator as gcc

from domain.geo import Coordinates


def calc_distance_in_kilometers(p1: Coordinates, p2: Coordinates) -> float:
    distance_in_meters = gcc.distance_between_points(
        (p1.longitude, p1.latitude),
        (p2.longitude, p2.latitude),
        unit="meters",
        haversine=True,
    )
    return distance_in_meters / 1000.0
