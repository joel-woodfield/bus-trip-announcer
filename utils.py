"""
Contains utility classes for this application.
"""

import math
from enum import Enum
from time import time
from functools import wraps


class Direction(Enum):
    """A compass direction."""

    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4


class SEQDirection(Enum):
    ZERO = 0
    ONE = 1


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

    @classmethod
    def latitude_displacement_between(
        cls, coordinates1: "Coordinates", coordinates2: "Coordinates"
    ) -> float:
        """
        Returns the latitude distance between the two given coordinates.

        Negative distance is returned when coordinates 1 has a greater latitude
        than coordinate 2.
        :param coordinates1: the first coordinate
        :param coordinates2: the second coordinate
        :return: the latitude distance between the coordinates
        """
        return coordinates2.latitude - coordinates1.latitude

    @classmethod
    def longitude_displacement_between(
        cls, coordinates1: "Coordinates", coordinates2: "Coordinates"
    ) -> float:
        """
        Returns the longitude distance between the two given coordinates.

        Negative distance is returned when coordinates 1 has a greater
        longitude than coordinate 2.
        :param coordinates1: the first coordinate
        :param coordinates2: the second coordinate
        :return: the latitude distance between the coordinates
        """
        return coordinates2.longitude - coordinates1.longitude

    def __repr__(self) -> str:
        """
        The string representation of the coordinates.
        """
        return f"Coordinates({self.latitude}, {self.longitude})"

    def __eq__(self, other):
        if not isinstance(other, Coordinates):
            return False
        return (
            self.latitude == other.latitude
            and self.longitude == other.longitude
        )


class Line:
    def __init__(self, start: Coordinates, end: Coordinates):
        self.start = start
        self.end = end

    @classmethod
    def minimum_distance(cls, line: "Line", point: Coordinates):
        """
        Calculates the minimum distance from the point to the line.

        See the following link for the equation:
        https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points
        :param line: the line
        :param point: the point
        :return: the minimum distance
        """
        x0, y0 = point.longitude, point.latitude
        x1, y1 = line.start.longitude, line.start.latitude
        x2, y2 = line.end.longitude, line.end.latitude

        return abs((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1)) / math.sqrt(
            (x2 - x1) ** 2 + (y2 - y1) ** 2
        )


def timing(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print(
            f"func:{f.__name__} args:[{args}, {kwargs}] took: {te-ts: 2.4f}s"
        )
        return result

    return wrap
