from announcer import TripAnnouncer
from model import RouteLocation
from util import Coordinates, Direction


class LocationSpecifier:
    def input_coordinates(self):
        raise NotImplementedError

    def input_route_number(self):
        raise NotImplementedError

    def input_direction(self):
        raise NotImplementedError

    def update_trip_announcer(self):
        raise NotImplementedError


class CommandlineLocationUpdator(LocationSpecifier):
    def __init__(
        self, trip_announcer: TripAnnouncer, current_location: RouteLocation
    ):
        self._trip_announcer = trip_announcer
        self._current_location = current_location

    def input_route_number(self):
        new_route_number = int(input("Input route number: "))

        current = self._current_location
        self._current_location = RouteLocation(
            new_route_number, current.direction, current.coordinates
        )

    def input_direction(self):
        new_direction = Direction[input("Input the direction: ")]

        current = self._current_location
        self._current_location = RouteLocation(
            current.route_number, new_direction, current.coordinates
        )

    def input_coordinates(self):
        latitude = input("Input Latitude: ")
        longitude = input("Input Longitude: ")
        new_coordinates = Coordinates(float(latitude), float(longitude))

        current = self._current_location
        self._current_location = RouteLocation(
            current.route_number, current.direction, new_coordinates
        )

    def update_trip_announcer(self):
        self.input_route_number()
        self.input_direction()
        self.input_coordinates()
        self._trip_announcer.update_next_stop_times(self._current_location)
