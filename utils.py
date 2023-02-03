"""
Contains utility classes for this application.
"""

import math
from enum import Enum


class Direction(Enum):
    """A compass direction."""

    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4


class Coordinates:
    """
    A latitude and longitude coordinates.

    Attributes
    ----------
    latitude: float
        the latitude coordinate
    longitude: float
        the longitude coordinate
    """

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def distance_between(
        cls, coordinates1: "Coordinates", coordinates2: "Coordinates"
    ) -> float:
        """
        Returns the distance between the two given coordinates.
        :param coordinates1: the first coordinate
        :param coordinates2: the second coordinate
        :return: the distance between the coordinates
        """
        return math.sqrt(
            (coordinates1.latitude - coordinates2.latitude) ** 2
            + (coordinates1.longitude - coordinates2.longitude) ** 2
        )

    def __repr__(self) -> str:
        """
        The string representation of the coordinates.
        """
        return f"Coordinates({self.latitude}, {self.longitude})"
