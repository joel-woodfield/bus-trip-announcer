import math
from enum import Enum


class Direction(Enum):
    """Test."""

    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4


class Coordinates:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def distance_between(
        cls, coordinates1: "Coordinates", coordinates2: "Coordinates"
    ):
        return math.sqrt(
            (coordinates1.latitude - coordinates2.latitude) ** 2
            + (coordinates1.longitude - coordinates2.longitude) ** 2
        )

    def __repr__(self):
        return f"Coordinates({self.latitude}, {self.longitude})"
