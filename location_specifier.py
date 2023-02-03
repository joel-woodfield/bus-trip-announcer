"""
Contains classes that specify the current location to the announcer for it to
update its next stops.
"""

from announcer import TripAnnouncer
from model import RouteLocation
from util import Coordinates, Direction


class LocationSpecifier:
    """
    Specifies the current route location to the announcer.
    """

    def input_coordinates(self) -> None:
        """Specifies the coordinates to the announcer."""
        raise NotImplementedError

    def input_route_number(self) -> None:
        """Specifies the route number to the announcer."""
        raise NotImplementedError

    def input_direction(self) -> None:
        """Specifies the direction to the announcer."""
        raise NotImplementedError

    def update_trip_announcer(self) -> None:
        """Specifies the current route location to the announcer."""
        raise NotImplementedError


class CommandlineLocationUpdator(LocationSpecifier):
    """
    Specifies the current route location to the announcer by asking for input
    in the command line.
    """

    def __init__(
        self, trip_announcer: TripAnnouncer, current_location: RouteLocation
    ):
        self._trip_announcer = trip_announcer
        self._current_location = current_location

    def input_route_number(self) -> None:
        new_route_number = int(input("Input route number: "))

        current = self._current_location
        self._current_location = RouteLocation(
            new_route_number, current.direction, current.coordinates
        )

    def input_direction(self) -> None:
        new_direction = Direction[input("Input the direction: ")]

        current = self._current_location
        self._current_location = RouteLocation(
            current.route_number, new_direction, current.coordinates
        )

    def input_coordinates(self) -> None:
        latitude = input("Input Latitude: ")
        longitude = input("Input Longitude: ")
        new_coordinates = Coordinates(float(latitude), float(longitude))

        current = self._current_location
        self._current_location = RouteLocation(
            current.route_number, current.direction, new_coordinates
        )

    def update_trip_announcer(self) -> None:
        self.input_route_number()
        self.input_direction()
        self.input_coordinates()
        self._trip_announcer.update_next_stop_times(self._current_location)
