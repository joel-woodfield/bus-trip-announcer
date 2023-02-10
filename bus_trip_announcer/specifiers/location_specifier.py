"""
Contains classes that specify the current location to the announcer for it to
update its next stops.
"""
from abc import ABC, abstractmethod

from bus_trip_announcer.announcer import TripAnnouncer
from bus_trip_announcer.models import TripStatus
from bus_trip_announcer.utils import Coordinates, Direction


class LocationSpecifier(ABC):
    """
    Specifies the current trip status to the announcer.
    """

    def __init__(
        self, trip_announcer: TripAnnouncer, current_status: TripStatus
    ):
        self._trip_announcer = trip_announcer
        self._current_status = current_status

    @abstractmethod
    def input_coordinates(self) -> None:
        """Specifies the coordinates to the announcer."""

    @abstractmethod
    def input_route_number(self) -> None:
        """Specifies the route number to the announcer."""

    @abstractmethod
    def input_direction(self) -> None:
        """Specifies the direction to the announcer."""

    @abstractmethod
    def update_trip_announcer(self) -> None:
        """Specifies the current trip status to the announcer."""


class CommandlineLocationUpdator(LocationSpecifier):
    """
    Specifies the current trip status to the announcer by asking for
    input in the command line.
    """

    def input_route_number(self) -> None:
        new_route_number = int(input("Input route number: "))

        current = self._current_status
        self._current_status = TripStatus(
            new_route_number, current.direction, current.coordinates
        )

    def input_direction(self) -> None:
        new_direction = Direction[input("Input the direction: ")]

        current = self._current_status
        self._current_status = TripStatus(
            current.route_number, new_direction, current.coordinates
        )

    def input_coordinates(self) -> None:
        latitude = input("Input Latitude: ")
        longitude = input("Input Longitude: ")
        new_coordinates = Coordinates(float(latitude), float(longitude))

        current = self._current_status
        self._current_status = TripStatus(
            current.route_number, current.direction, new_coordinates
        )

    def update_trip_announcer(self) -> None:
        self.input_coordinates()
        self._trip_announcer.update_next_stops(self._current_status)
