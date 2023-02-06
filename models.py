"""
Contains classes that model the world with bus stops, routes, and locations
within the route.
"""

import datetime

from utils import Coordinates, Direction


class User:
    """
    A user riding a bus on a bus route.

    Attributes
    ----------
    bus_route_number: int = 0
        the route number of the bus the user is on
    direction: Direction = Direction.NORTH
        the direction of the route of the bus the user is on
    coordinates: Coordinates = Coordinates(0, 0)
        the coordinates of the user's location
    """

    def __init__(
        self,
        bus_route_number: int = 0,
        direction: Direction = Direction.NORTH,
        coordinates: Coordinates = Coordinates(0, 0),
    ):
        """
        Initializes the user with the given parameters.
        :param bus_route_number: the route number of the bus the user is on
        :param direction: the direction of the route of the bus the user is on
        :param coordinates: the coordinates of the user's location
        """
        self.bus_route_number = bus_route_number
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
    time_until_stop: datetime.timedelta
        the time until the bus reaches the stop
    """

    def __init__(
        self,
        name: str,
        coordinates: Coordinates,
        time_until_stop: datetime.timedelta,
    ):
        """
        Initializes the stop with the given parameters.
        :param name: the name of the stop
        :param coordinates: the location of the stop
        """
        self.name = name
        self.coordinates = coordinates
        self.time_until_stop = time_until_stop

    @classmethod
    def distance_between(cls, stop1: "Stop", stop2: "Stop") -> float:
        """Returns the distance between two stops."""
        return Coordinates.distance_between(
            stop1.coordinates, stop2.coordinates
        )

    def is_after(self, user: User) -> bool:
        """
        Returns whether the given user has passed this stop on the route.

        :param user: the user
        :return: true if the user has passed this top, false otherwise
        """
        if user.direction == Direction.NORTH:
            return self.coordinates.latitude >= user.coordinates.latitude
        if user.direction == Direction.SOUTH:
            return self.coordinates.latitude <= user.coordinates.latitude
        if user.direction == Direction.EAST:
            return self.coordinates.longitude >= user.coordinates.longitude
        if user.direction == Direction.WEST:
            return self.coordinates.longitude <= user.coordinates.longitude
        raise ValueError("The direction of the user is not valid.")

    def __str__(self) -> str:
        """The string representation of the stop."""
        return f"Stop({self.name}, {self.coordinates}, {self.time_until_stop})"


class Route:
    """
    The bus route with its stops and the time it takes to reach them.

    Attributes
    ----------
    number: int
        the route number
    direction: Direction
        the direction of the route
    stops: list[Stop]
        the stops of the route and the time it takes to reach them.
    """

    def __init__(self, number: int, direction: Direction, stops: list[Stop]):
        """
        Initializes the route with the given parameters.
        :param number: the route number
        :param direction: the direction of the route
        :param stops: the stops of the route
        """
        self.number = number
        self.direction = direction
        self.stops = stops

    def __str__(self) -> str:
        """
        The string representation of the route.
        """
        return f"Route {self.number} {self.direction}:\n{self.stops}"
