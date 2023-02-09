"""
Manages the database that stores the route and stop information.
"""

import datetime
import time
from typing import Protocol
import pandas as pd

from models import Route, Stop
from utils import Coordinates, Direction, SEQDirection, timing


class TransportDatabase(Protocol):
    """
    The database for the route information that can be queried.
    """

    def get_route(self, number: int, direction: Direction) -> Route:
        """
        Retrieves the Route object with its stops for the given route
        number and direction. The stops are ordered ascending on the time until
        stop attribute.
        :param number: the route number
        :param direction: the direction of the route
        :return: the Route object corresponding to the parameters
        """


class LocalDatabase(TransportDatabase):
    """
    The database for the route information stored in `test_database1.csv`.
    """

    ROUTE_NUMBER_COLUMN = 4
    DIRECTION_COLUMN = 5
    DATABASE_FILE = "data/test_database1.csv"

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
                time_until_stop = datetime.datetime.strptime(
                    time_until_stop, "%H:%M"
                )
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
                stops = sorted(stops, key=lambda stop: stop.time_until_stop)

            return Route(number, direction, stops)

    def set_database_file(self, file_location: str) -> None:
        self.DATABASE_FILE = file_location


class SEQDatabase(Protocol):
    def get_headsigns(self, route_number: int) -> list[str]:
        """"""


class LocalSEQDatabase:

    DATA_PATH = "useful_data"

    def __init__(self):
        self._route_number = None
        self._direction = None
        self._route = None

    def get_headsigns(self, route_number: int) -> list[str]:
        route_id = self._get_route_id(route_number)

        trips = pd.read_csv(f"{self.DATA_PATH}/trips.csv")
        route_trips = trips[trips["route_id"] == route_id]
        # this can be made faster as there should only be two headsigns
        return list(route_trips["trip_headsign"].unique())

    def get_direction(self, route_number: int, headsign: str) -> SEQDirection:
        route_id = self._get_route_id(route_number)

        trips = pd.read_csv(f"{self.DATA_PATH}/trips.csv")
        direction_id = trips.loc[
            (trips["route_id"] == route_id)
            & (trips["trip_headsign"] == headsign),
            "direction_id",
        ].iloc[0]
        return SEQDirection(direction_id)

    def get_route(
            self,
            number: int,
            direction: SEQDirection,
            coordinates: Coordinates,
            time: datetime.timedelta,
    ) -> Route:
        if self._route_number != number or self._direction != direction:
            trip_id = self._get_trip_id(number, direction, coordinates, time)

            # create route from trip id
            route = self._get_stops_and_arrival_times(trip_id)
            stops = []
            for _, stop in route.iterrows():
                name = stop["stop_name"]
                coordinates = Coordinates(stop["stop_lat"], stop["stop_lon"])
                time_until_stop = stop["arrival_time"]
                stops.append(Stop(name, coordinates, time_until_stop))
            self._route = Route(number, direction, stops)
        return self._route

    def _get_trip_id(
        self,
        route_number: int,
        direction: SEQDirection,
        coordinates: Coordinates,
        time: datetime.timedelta,
    ) -> str:
        route_id = self._get_route_id(route_number)
        # get all trips for the given route and direction
        trips = pd.read_csv(f"{self.DATA_PATH}/trips.csv")
        trip_ids = trips.loc[
            (trips["route_id"] == route_id)
            & (trips["direction_id"] == direction.value),
            "trip_id",
        ]

        # get the stop times for the trips we are considering
        stop_times = pd.read_csv(f"{self.DATA_PATH}/stop_times.csv")[
            ["trip_id", "arrival_time", "stop_id"]
        ]
        stop_times = pd.merge(trip_ids, stop_times)

        # get the next stop estimates' stop id
        next_stop_id = self._get_id_of_two_closest_stops(
            route_number, direction, coordinates
        ).iloc[1]

        # find the earliest stop time of the next stop that is after the
        # current time
        return stop_times.loc[
            (stop_times["stop_id"] == int(next_stop_id))
            & (stop_times["arrival_time"].astype("timedelta64") > time),
            "trip_id",
        ].iloc[0]

    def _get_route_id(self, route_number: int):
        routes = pd.read_csv(f"{self.DATA_PATH}/routes.csv")
        return routes.loc[
            routes["route_short_name"] == str(route_number), "route_id"
        ].iloc[0]

    def _get_route_stops_and_arrival_times(
        self, route_number: int, direction: SEQDirection
    ) -> pd.DataFrame:
        """Returns sorted route stops with its id and coordinates"""
        route_id = self._get_route_id(route_number)
        trips = pd.read_csv(f"{self.DATA_PATH}/trips.csv")
        trip_id_example = trips.loc[
            (trips["route_id"] == route_id)
            & (trips["direction_id"] == direction.value),
            "trip_id",
        ].iloc[0]
        return self._get_stops_and_arrival_times(trip_id_example)

    def _get_id_of_two_closest_stops(
        self,
        route_number: int,
        direction: SEQDirection,
        coordinates: Coordinates,
    ):
        stops = self._get_route_stops_and_arrival_times(route_number, direction)
        j = -1
        min_pair_distance = 1_000_000
        for i in range(len(stops) - 1):
            stop_latitude = stops.loc[i, "stop_lat"]
            stop_longitude = stops.loc[i, "stop_lon"]
            pair_distance = Coordinates.distance_between(
                Coordinates(stop_latitude, stop_longitude), coordinates
            )
            if pair_distance < min_pair_distance:
                j = i
                min_pair_distance = pair_distance

        return stops.loc[j : (j + 1), "stop_id"]

    def _get_stops_and_arrival_times(self, trip_id: str):
        stop_times = pd.read_csv(f"{self.DATA_PATH}/stop_times.csv")
        stop_times = stop_times[stop_times["trip_id"] == trip_id]
        stops = pd.read_csv(f"{self.DATA_PATH}/stops.csv")
        stop_times["stop_id"] = stop_times["stop_id"].astype(str)
        stops = pd.merge(stops, stop_times, on="stop_id")
        stops = stops.sort_values("stop_sequence")
        return stops[
            ["stop_id", "stop_name", "arrival_time", "stop_lat", "stop_lon"]
        ]


if __name__ == "__main__":
    database = LocalSEQDatabase()
    print(
        database.get_route(
            704,
            SEQDirection.ZERO,
            Coordinates(-27.48, 153.02),
            datetime.timedelta(hours=6, minutes=9),
        )
    )
