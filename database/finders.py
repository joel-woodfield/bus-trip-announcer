from datetime import timedelta, datetime

from database.database import Database, Query
from models import Route, Stop
from stops_finder import NextStopsFinder
from utils import SEQDirection, Coordinates

class DirectionFinder:
    def __init__(self, database: Database):
        self._database = database

    def get_headsigns(self, route_number: int) -> list[str]:
        query = Query("routes")
        (
            query.select(["route_id", "route_short_name"])
            .where(lambda row: row["route_short_name"] == str(route_number))
            .join("trips", "route_id")
            .select("trip_headsign")
        )
        return list(self._database.get(query).unique())

    def get_direction(self, route_number: int, headsign: str) -> SEQDirection:
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


class RouteFinder:
    def __init__(self, database: Database):
        self._database = database

    def get_route(
        self,
        route_number: int,
        direction: SEQDirection,
        coordinates: Coordinates,
        time: timedelta,
    ) -> Route:
        route_id = self._database.get(
            Query("routes")
            .where(lambda row: row["route_short_name"] == str(route_number))
            .select("route_id")
        ).iloc[0]

        example_trip_id = self._database.get(
            Query("trips")
            .where(
                lambda row: (row["route_id"] == route_id)
                & (row["direction_id"] == direction.value)
            )
            .select("trip_id")
        ).iloc[0]

        route = self._create_route(example_trip_id, route_number, direction)

        _, next_stop = NextStopsFinder.get_in_between_stops(
            route.stops, coordinates
        )

        next_stop_id = self._database.get(
            Query("stops")
            .where(lambda row: row["stop_name"] == next_stop.name)
            .select("stop_id")
        ).iloc[0]

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

        return self._create_route(trip_id, route_number, direction)

    def _create_route(
        self, trip_id: str, route_number: int, direction: SEQDirection
    ):
        route_stops_data = self._database.get(
            Query("stop_times")
            .where(lambda row: row["trip_id"] == trip_id)
            .order_by("stop_sequence")
            .select(["stop_id", "arrival_time"])
            .join("stops", "stop_id")
        )

        stops = []
        for _, stop_data in route_stops_data.iterrows():
            name = stop_data["stop_name"]
            latitude = stop_data["stop_lat"]
            longitude = stop_data["stop_lon"]
            time = datetime.strptime(stop_data["arrival_time"], "%H:%M:%S")
            time = timedelta(
                hours=time.hour, minutes=time.minute, seconds=time.second
            )
            stops.append(Stop(name, Coordinates(latitude, longitude), time))
        return Route(route_number, direction, stops)