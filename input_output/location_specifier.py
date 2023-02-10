"""
Contains classes that specify the current location to the announcer for it to
update its next stops.
"""
from abc import ABC, abstractmethod

from announcer import TripAnnouncer
from models import TripStatus
from utils import Coordinates, Direction


class LocationSpecifier(ABC):
    """
    Specifies the current trip status to the announcer.
    """

    def __init__(
        self, trip_announcer: TripAnnouncer, current_location: TripStatus
    ):
        self._trip_announcer = trip_announcer
        self._current_location = current_location

    @abstractmethod
    def input_coordinates(self) -> None:
        """Specifies the coordinates to the announcer."""

    def input_route_number(self) -> None:
        """Specifies the route number to the announcer."""

    def input_direction(self) -> None:
        """Specifies the direction to the announcer."""

    def update_trip_announcer(self) -> None:
        """Specifies the current trip status to the announcer."""


class CommandlineLocationUpdator(LocationSpecifier):
    """
    Specifies the current trip status to the announcer by asking for
    input in the command line.
    """

    def input_route_number(self) -> None:
        new_route_number = int(input("Input route number: "))

        current = self._current_location
        self._current_location = TripStatus(
            new_route_number, current.direction, current.coordinates
        )

    def input_direction(self) -> None:
        new_direction = Direction[input("Input the direction: ")]

        current = self._current_location
        self._current_location = TripStatus(
            current.route_number, new_direction, current.coordinates
        )

    def input_coordinates(self) -> None:
        latitude = input("Input Latitude: ")
        longitude = input("Input Longitude: ")
        new_coordinates = Coordinates(float(latitude), float(longitude))

        current = self._current_location
        self._current_location = TripStatus(
            current.route_number, current.direction, new_coordinates
        )

    def update_trip_announcer(self) -> None:
        self.input_coordinates()
        self._trip_announcer.update_next_stops(self._current_location)
