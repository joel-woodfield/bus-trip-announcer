from announcer import TripAnnouncer
from database import DirectionFinder, RouteFinder
from abc import ABC, abstractmethod

from models import TripStatus, Route
from stops_finder import NextStopsFinder
from utils import Coordinates

from datetime import datetime, timedelta


class TripSpecifier(ABC):
    def __init__(
            self, direction_finder: DirectionFinder, route_finder: RouteFinder
    ):
        self._direction_finder = direction_finder
        self._route_finder = route_finder
        self._trip_status = TripStatus()
        self._time = None

    @abstractmethod
    def specify_route_number(self):
        pass

    @abstractmethod
    def specify_direction(self):
        pass

    @abstractmethod
    def specify_coordinates(self):
        pass

    @abstractmethod
    def specify_time(self):
        pass


class CommandLineTripSpecifier(TripSpecifier):

    def specify_route_number(self):
        number = int(input("Input route number: "))
        self._trip_status.route_number = number

    def specify_direction(self):
        if self._trip_status.route_number is None:
            raise NoRouteNumberError
        headsigns = self._direction_finder.get_headsigns(
            self._trip_status.route_number
        )
        print("Which headsign did you see?")
        print(f"1: {headsigns[0]}")
        print(f"2: {headsigns[1]}")
        selection = int(input("Enter number: ")) - 1

        direction = self._direction_finder.get_direction(
            self._trip_status.route_number, headsigns[selection]
        )
        self._trip_status.direction = direction

    def specify_coordinates(self):
        latitude = input("Input Latitude: ")
        longitude = input("Input Longitude: ")
        self._trip_status.coordinates = Coordinates(
            float(latitude), float(longitude)
        )

    def specify_time(self):
        time = input("Input time: ")
        t = datetime.strptime(time, "%H:%M")
        self._time = timedelta(
            hours=t.hour, minutes=t.minute
        )

    def specify_all(self):
        self.specify_route_number()
        self.specify_direction()
        self.specify_coordinates()
        self.specify_time()

    def _get_route(self) -> Route:
        return self._route_finder.get_route(self._trip_status.route_number,
                                            self._trip_status.direction,
                                            self._trip_status.coordinates,
                                            self._time)

    def create_announcer(self) -> TripAnnouncer:
        stops_finder = NextStopsFinder(self._get_route())
        announcer = TripAnnouncer(stops_finder)
        announcer.update_next_stops(self._trip_status)

        return announcer



class NoRouteNumberError(Exception):
    pass
