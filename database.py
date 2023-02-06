"""
Manages the database that stores the route and stop information.
"""

import datetime
from typing import Protocol

from models import Route, Stop
from utils import Coordinates, Direction


class TransportDatabase(Protocol):
    """
    The database for the route information that can be queried.
    """

    def get_route(self, number: int, direction: Direction) -> Route:
        """
        Retrieves the Route object with its stops for the given route
        number and direction.
        :param number: the route number
        :param direction: the direction of the route
        :return: the Route object corresponding to the parameters
        """


class LocalDatabase(TransportDatabase):
    """
    The database for the route information stored in `test_database.csv`.
    """

    ROUTE_NUMBER_COLUMN = 4
    DIRECTION_COLUMN = 5
    DATABASE_FILE = "data/test_database.csv"

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

            stops = []
            for row in route_data:
                (
                    stop_name,
                    time_until_stop,
                    latitude,
                    longitude,
                    _,
                    _,
                ) = row
                time_until_stop = datetime.datetime.strptime(time_until_stop, "%H:%M")
                time_until_stop = datetime.timedelta(
                    hours=time_until_stop.hour, minutes=time_until_stop.minute
                )
                stops.append(
                    Stop(
                        stop_name,
                        Coordinates(float(latitude), float(longitude)),
                        time_until_stop,
                    )
                )

            return Route(number, direction, stops)
