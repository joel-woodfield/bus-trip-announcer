from database import DirectionFinder, RouteFinder
from abc import ABC, abstractmethod

from models import TripStatus
from utils import Coordinates

from datetime import datetime, timedelta


class TripSpecifier(ABC):
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
    def __init__(
        self, direction_finder: DirectionFinder, route_finder: RouteFinder
    ):
        self._direction_finder = direction_finder
        self._route_finder = route_finder
        self._trip_status = TripStatus()
        self._time = None

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
        selection = int(input("Enter number: "))

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
        t = datetime.strptime(time, "%H:%M:%S")
        self._time = timedelta(
            hours=t.hour, minutes=t.minute, seconds=t.second
        )


class NoRouteNumberError(Exception):
    pass
