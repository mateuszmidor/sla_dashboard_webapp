from dataclasses import dataclass


@dataclass
class Coordinates:
    longitude: float = 0.0  # east-west axis, in degrees [180..-180], eg -0.1278 for London
    latitude: float = 0.0  # north-south axis, in degrees [90..-90], eg 51.5074 for London
