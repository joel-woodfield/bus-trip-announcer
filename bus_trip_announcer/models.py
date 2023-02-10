"""
Module that contains classes that model the bus network with bus stops, routes,
and trips.
"""

import datetime

from bus_trip_announcer.utils import Coordinates, Direction, SEQDirection


# Make trip status mutable to make it better for vertical scaling
class TripStatus:
    """
    The status of a bus trip.

    Attributes
    ----------
    route_number: int = 0
        the route number of the bus for the trip
    direction: Direction = Direction.NORTH
        the direction of the route of the trip
    coordinates: Coordinates = Coordinates(0, 0)
        the current coordinates of the trip
    """

    def __init__(
        self,
        route_number: int = 0,
        direction: Direction | SEQDirection = Direction.NORTH,
        coordinates: Coordinates = Coordinates(0, 0),
    ):
        """
        Initializes the trip status with the given parameters.
        :param route_number: the route number of the trip's bus
        :param direction: the direction of the trip
        :param coordinates: the current coordinates of the trip
        """
        self.route_number = route_number
        self.direction = direction
        self.coordinates = coordinates

    def __eq__(self, other):
        if not isinstance(other, TripStatus):
            return False
        return (
            self.route_number == other.route_number
            and self.direction == other.direction
            and self.coordinates == other.coordinates
        )


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
        time_until_stop: datetime.timedelta | None,
    ):
        """
        Initializes the stop with the given parameters.
        :param name: the name of the stop
        :param coordinates: the location of the stop
        """
        self.name = name
        self.coordinates = coordinates
        self.time_until_stop = time_until_stop

    # this method isn't used
    @classmethod
    def distance_between(cls, stop1: "Stop", stop2: "Stop") -> float:
        """Returns the distance between two stops."""
        return Coordinates.distance_between(
            stop1.coordinates, stop2.coordinates
        )

    def has_not_been_passed_by(self, trip_status: TripStatus) -> bool:
        """
        Returns whether the given trip has passed this stop on the route.

        :param trip_status: the status of the trip that we want to check
        :return: true if the trip's bus has passed this top, false otherwise
        """
        if trip_status.direction == Direction.NORTH:
            return (
                self.coordinates.latitude >= trip_status.coordinates.latitude
            )
        if trip_status.direction == Direction.SOUTH:
            return (
                self.coordinates.latitude <= trip_status.coordinates.latitude
            )
        if trip_status.direction == Direction.EAST:
            return (
                self.coordinates.longitude >= trip_status.coordinates.longitude
            )
        if trip_status.direction == Direction.WEST:
            return (
                self.coordinates.longitude <= trip_status.coordinates.longitude
            )
        raise ValueError("The direction of the trip is not valid.")

    def __str__(self) -> str:
        """The string representation of the stop."""
        return f"Stop({self.name}, {self.coordinates}, {self.time_until_stop})"

    def __eq__(self, other) -> bool:
        """
        Checks the equality with another Stop.

        A stop is equal with another if the name, coordinates, and time
        until stop are all the same.

        :param other: the other object
        :return: true if the other object is equal with this Route, false
        otherwise
        """
        if not isinstance(other, Stop):
            return False
        return (
            other.name == self.name
            and other.coordinates == self.coordinates
            and other.time_until_stop == self.time_until_stop
        )


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

    def __init__(
        self,
        number: int,
        direction: Direction | SEQDirection,
        stops: list[Stop],
    ):
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

    def __eq__(self, other):
        """
        Checks for equality with the other stop.

        A Route is equal with another Rote if the number, direction, and the
        list of stops are all the same.
        :param other: the other object
        :return: true if the other object is equal with this Route, false
        otherwise
        """
        if not isinstance(other, Route):
            return False
        return (
            self.number == other.number
            and self.direction is other.direction
            and self.stops == other.stops
        )
