"""
Contains classes that model the world with bus stops, routes, and locations within the route.
"""

import datetime

from util import Coordinates, Direction


class RouteLocation:
    """
    The location within a bus route.

    Attributes
    ----------
    route_number: int = 0
        the route number
    direction: Direction = Direction.NORTH
        the direction of the route
    coordinates: Coordinates = Coordinates(0, 0)
        the coordinates of the location within the bus route
    """
    def __init__(
        self,
        route_number: int = 0,
        direction: Direction = Direction.NORTH,
        coordinates: Coordinates = Coordinates(0, 0),
    ):
        """
        Initializes the route location with the given parameters.
        :param route_number: the route number
        :param direction: the direction of the route
        :param coordinates: the coordinates of the location within the bus route
        """
        self.route_number = route_number
        self.direction = direction
        self.coordinates = coordinates


class Stop:
    """
    A bus stop.

    Attributes
    ----------
    name: str
        the name of the stop
    coordinates: Coordinates
        the location of the stop
    """
    def __init__(self, name: str, coordinates: Coordinates):
        """
        Initializes the stop with the given parameters.
        :param name: the name of the stop
        :param coordinates: the location of the stop
        """
        self.name = name
        self.coordinates = coordinates

    @classmethod
    def distance_between(cls, stop1: "Stop", stop2: "Stop") -> float:
        """Returns the distance between two stops."""
        return Coordinates.distance_between(
            stop1.coordinates, stop2.coordinates
        )

    def __str__(self) -> str:
        """The string representation of the stop."""
        return f"Stop({self.name}, {self.coordinates})"


class StopTime:
    """
    The bus stop and the time it takes for the bus to reach the stop for a given route.

    Attributes
    ----------
    stop: Stop
        the bus stop
    route_time: datetime.timedelta
        the time it takes for the bus to reach the stop for a given route
    """
    def __init__(self, stop: Stop, route_time: datetime.timedelta):
        """
        Initializes the stop time with the given parameters.
        :param stop: the bus stop
        :param route_time: the time it takes for the bus to reach the stop for a given route
        """
        self.stop = stop
        self.route_time = route_time

    def is_after(self, route_location: RouteLocation) -> bool:
        """
        Returns whether the given route location is after this stop in the route.
        :param route_location: the route location
        :return: true if the route location is after this top, false otherwise
        """
        if route_location.direction == Direction.NORTH:
            return (
                self.stop.coordinates.latitude
                >= route_location.coordinates.latitude
            )
        if route_location.direction == Direction.SOUTH:
            return (
                self.stop.coordinates.latitude
                <= route_location.coordinates.latitude
            )
        if route_location.direction == Direction.EAST:
            return (
                self.stop.coordinates.longitude
                >= route_location.coordinates.longitude
            )
        if route_location.direction == Direction.WEST:
            return (
                self.stop.coordinates.longitude
                <= route_location.coordinates.longitude
            )

    def __repr__(self) -> str:
        """
        The representation of the stop time.
        """
        return f"StopTime({self.stop}, {self.route_time})"


class Route:
    """
    The bus route with its stops and the time it takes to reach them (StopTime).

    Attributes
    ----------
    number: int
        the route number
    direction: Direction
        the direction of the route
    stop_times: list[StopTime]
        the stop times of the route (the stop and the time it takes to reach them).
    """
    def __init__(
        self, number: int, direction: Direction, stop_times: list[StopTime]
    ):
        """
        Initializes the route with the given parameters.
        :param number: the route number
        :param direction: the direction of the route
        :param stop_times: the stop times of the route
        """
        self.number = number
        self.direction = direction
        self.stop_times = stop_times

    def __str__(self) -> str:
        """
        The string representation of the route.
        """
        return f"Route {self.number} {self.direction}:\n{self.stop_times}"
