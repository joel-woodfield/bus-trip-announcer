"""
Manages the database that stores the route and stop information.
"""

import datetime

from model import Route, Stop, StopTime
from util import Coordinates, Direction


class TransportDatabase:
    """
    The database for the route information that can be queried.
    """

    def get_route(self, number: int, direction: Direction) -> Route:
        """
        Retrieves the Route object with its stop times for the given route
        number and direction.
        :param number: the route number
        :param direction: the direction of the route
        :return: the Route object corresponding to the parameters
        """
        raise NotImplementedError


class LocalDatabase(TransportDatabase):
    """
    The database for the route information stored in `test_database.csv`.
    """

    ROUTE_NUMBER_COLUMN = 4
    DIRECTION_COLUMN = 5
    DATABASE_FILE = "test_database.csv"

    def get_route(self, number: int, direction: Direction) -> Route:
        with open(self.DATABASE_FILE, "r") as file:
            _ = next(file)  # this is the header
            data = (line.rstrip().split(",") for line in file)

            route_data = (
                row
                for row in data
                if int(row[self.ROUTE_NUMBER_COLUMN]) == number
                and Direction[row[self.DIRECTION_COLUMN]] == direction
            )

            stop_times = []
            for row in route_data:
                (
                    stop_name,
                    route_time,
                    latitude,
                    longitude,
                    _,
                    _,
                ) = row
                route_time = datetime.datetime.strptime(route_time, "%H:%M")
                route_time = datetime.timedelta(
                    hours=route_time.hour, minutes=route_time.minute
                )
                stop = Stop(
                    stop_name, Coordinates(float(latitude), float(longitude))
                )
                stop_times.append(StopTime(stop, route_time))

            return Route(number, direction, stop_times)
