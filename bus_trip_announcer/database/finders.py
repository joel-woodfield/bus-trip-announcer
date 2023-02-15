"""
Module containing classes that query from the database.
"""

from datetime import datetime, timedelta

from bus_trip_announcer.database.database import Database, Query
from bus_trip_announcer.models import Trip, Stop
from bus_trip_announcer.stops_finder import NextStopsFinder
from bus_trip_announcer.utils import Coordinates, SEQDirection


class DirectionFinder:
    """
    Helper for finding the SEQDirection of a bus trip.
    """

    def __init__(self, database: Database):
        """
        Initializes the finder with the given database.
        :param database: the database for the finder to look into
        """
        self._database = database

    def get_headsigns(self, route_number: int) -> list[str]:
        """
        Returns the possible headsigns for the given route.
        :param route_number: the route number
        :return: the possible headsigns
        """
        query = Query("routes")
        (
            query.select(["route_id", "route_short_name"])
            .where(lambda row: row["route_short_name"] == str(route_number))
            .join("trips", "route_id")
            .select("trip_headsign")
        )
        return list(self._database.get(query).unique())

    def get_direction(self, route_number: int, headsign: str) -> SEQDirection:
        """
        Returns the SEQDirection that matches the given route and headsign
        :param route_number: the route number
        :param headsign: the headsign
        :return: the SEQDirection for the given route and headsign
        """
        query = Query("routes")
        (
            query.select(["route_id", "route_short_name"])
            .where(lambda row: row["route_short_name"] == str(route_number))
            .join("trips", "route_id")
            .where(lambda row: row["trip_headsign"] == headsign)
            .select("direction_id")
        )
        direction_id = self._database.get(query).iloc[0]
        return SEQDirection(direction_id)


class TripFinder:
    """
    Helper for finding the exact trip of the bus at a given coordinates
    and at the given time.
    """

    def __init__(self, database: Database):
        """
        Initializes the finder with the given database.
        :param database: the database for the finder to look into
        """
        self._database = database

    def get_trip(
        self,
        route_number: int,
        direction: SEQDirection,
        coordinates: Coordinates,
        time: timedelta,
    ) -> Trip:
        """
        Returns the Trip object for the bus trip corresponding to the given
        parameters at the given time.
        :param route_number: the route number of the trip
        :param direction: the direction of the bus trip
        :param coordinates: the coordinates of the bus at the given time
        :param time: the time
        :return: the Trip object
        """
        route_id = self._database.get(
            Query("routes")
            .where(lambda row: row["route_short_name"] == str(route_number))
            .select("route_id")
        ).iloc[0]

        # get one trip_id with the same route_id
        example_trip_id = self._database.get(
            Query("trips")
            .where(
                lambda row: (row["route_id"] == route_id)
                & (row["direction_id"] == direction.value)
            )
            .select("trip_id")
        ).iloc[0]

        # use this Trip object to find the two stops we are in between
        trip = self._create_trip(example_trip_id, route_number, direction)
        _, next_stop = NextStopsFinder.get_in_between_stops(
            trip.stops, coordinates
        )

        next_stop_id = self._database.get(
            Query("stops")
            .where(lambda row: row["stop_name"] == next_stop.name)
            .select("stop_id")
        ).iloc[0]

        # find the trip that arrives at the next stop with the earliest
        # arrival time after the current time
        trip_id = self._database.get(
            Query("trips")
            .where(
                lambda row: (row["route_id"] == route_id)
                & (row["direction_id"] == direction.value)
            )
            .select("trip_id")
            .join("stop_times", "trip_id")
            .where(
                lambda row: (row["stop_id"] == next_stop_id)
                & (row["arrival_time"].astype("timedelta64") >= time)
            )
            .order_by("arrival_time")
            .select("trip_id")
        ).iloc[0]

        return self._create_trip(trip_id, route_number, direction)

    def _create_trip(
        self, trip_id: str, route_number: int, direction: SEQDirection
    ) -> Trip:
        """
        Creates the Trip object for the given trip id.
        :param trip_id: the trip id
        :param route_number: the route number of the trip
        :param direction: the direction of the trip
        :return: the Trip object
        """
        trip_data = self._database.get(
            Query("stop_times")
            .where(lambda row: row["trip_id"] == trip_id)
            .order_by("stop_sequence")
            .select(["stop_id", "arrival_time"])
            .join("stops", "stop_id")
        )

        stops = []
        for _, stop_data in trip_data.iterrows():
            name = stop_data["stop_name"]
            latitude = stop_data["stop_lat"]
            longitude = stop_data["stop_lon"]
            time = datetime.strptime(stop_data["arrival_time"], "%H:%M:%S")
            time = timedelta(
                hours=time.hour, minutes=time.minute, seconds=time.second
            )
            stops.append(Stop(name, Coordinates(latitude, longitude), time))
        return Trip(route_number, direction, stops)
