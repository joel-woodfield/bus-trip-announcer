"""
Module containing classes that specify the current location to the announcer
for it to update its next stops.
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
    def specify_coordinates(self) -> None:
        """Specifies the coordinates to the announcer."""

    def update_trip_announcer(self) -> None:
        self.specify_coordinates()
        self._trip_announcer.update_next_stops(self._current_status)

    # @abstractmethod
    # def input_route_number(self) -> None:
    #     """Specifies the route number to the announcer."""
    #
    # @abstractmethod
    # def input_direction(self) -> None:
    #     """Specifies the direction to the announcer."""
    #
    # @abstractmethod
    # def update_trip_announcer(self) -> None:
    #     """Specifies the current trip status to the announcer."""


class CommandlineLocationSpecifier(LocationSpecifier):
    """
    Specifies the current trip status to the announcer by asking for
    input in the command line.
    """

    #
    # def input_route_number(self) -> None:
    #     new_route_number = int(input("Input route number: "))
    #
    #     current = self._current_status
    #     self._current_status = TripStatus(
    #         new_route_number, current.direction, current.coordinates
    #     )
    #
    # def input_direction(self) -> None:
    #     new_direction = Direction[input("Input the direction: ")]
    #
    #     current = self._current_status
    #     self._current_status = TripStatus(
    #         current.route_number, new_direction, current.coordinates
    #     )

    def specify_coordinates(self) -> None:
        latitude = input("Input Latitude: ")
        longitude = input("Input Longitude: ")
        new_coordinates = Coordinates(float(latitude), float(longitude))

        current = self._current_status
        self._current_status = TripStatus(
            current.route_number, current.direction, new_coordinates
        )


# class FileLocationSpecifier(LocationSpecifier):
#
#     LATITUDE_ROW = 0
#     LONGITUDE_ROW = 1
#
#     def __init__(self, trip_announcer: TripAnnouncer, current_status: TripStatus, input_file_path: str):
#         super().__init__(trip_announcer, current_status)
#         self._input_file_path = input_file_path
#         self._data = None
#
#     def _read_file(self):
#         with open(self._input_file_path, 'r') as f:
#             self._data = f.readlines()
#
#     def input_coordinates(self) -> None:
#         self._read_file()
#         latitude, longitude = 0, 0
#         for line in self._data:
#             if line.startswith("Latitude"):
#                 _, latitude = line.split(": ")
#             if line.startswith("Longitude"):
#                 _, longitude = line.split(": ")
#         new_coordinates = Coordinates(float(latitude), float(longitude))
#
#         current = self._current_status
#         self._current_status = TripStatus(
#             current.route_number, current.direction, new_coordinates
#         )
