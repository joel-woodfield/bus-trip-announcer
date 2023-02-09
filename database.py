"""
Manages the database that stores the route and stop information.
"""
import pandas as pd
from typing import Protocol, Callable
from utils import Direction, Coordinates, SEQDirection, Line
from models import Route, Stop
from stops_finder import NextStopsFinder
from datetime import datetime, timedelta

DATA_DIRECTORY = "useful_data"
TABLE_FILE_PATH = {
    "routes": DATA_DIRECTORY + "/routes.csv",
    "stops": DATA_DIRECTORY + "/stops.csv",
    "stop_times": DATA_DIRECTORY + "/stop_times.csv",
    "trips": DATA_DIRECTORY + "/trips.csv",
}


class Query:
    SELECT = "select"
    JOIN = "join"
    WHERE = "where"
    ORDER_BY = "order by"

    def __init__(self, table: str):
        self.table = table
        self.operations = []

    def select(self, columns: str | list[str]):
        self.operations.append((self.SELECT, columns))
        return self

    def join(self, table: str, join_column: str):
        self.operations.append((self.JOIN, (table, join_column)))
        return self

    def where(self, condition: Callable):
        self.operations.append((self.WHERE, condition))
        return self

    def order_by(self, column: str, ascending: bool = True):
        self.operations.append((self.ORDER_BY, (column, ascending)))
        return self


class Database(Protocol):
    ALL = 0

    def get(self, query: Query) -> pd.DataFrame:
        """
        Retrieves the table that satisfies the query.
        :return: the table that satisfies the query"""


class CSVDatabase(Database):
    def __init__(self, data_directory: str):
        """
        Specifies the file path to the directory of the csv data files.
        :param data_directory: the file path to the directory of the csv files
        """
        self._data_directory = data_directory

    def get(self, query: Query) -> pd.DataFrame:
        result = pd.read_csv(self._file_path(query.table))
        for operation, args in query.operations:
            result = self._process_operation(operation, result, args)
        return result

    def _file_path(self, table_name) -> str:
        return f"{self._data_directory}/{table_name}.csv"

    def _process_operation(
        self, operation: str, table: pd.DataFrame, args
    ) -> pd.DataFrame:
        if operation == Query.SELECT:
            columns = args
            return table[columns]
        elif operation == Query.JOIN:
            table_name, join_column = args
            join_table = pd.read_csv(self._file_path(table_name))
            return pd.merge(table, join_table, on=join_column)
        elif operation == Query.WHERE:
            condition = args
            return table[condition]
        elif operation == Query.ORDER_BY:
            column, ascending = args
            return table.sort_values(column, ascending=ascending)


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
        query = Query("trips")
        (
            query.select(["trip_headsign", "direction_id"])
            .where(lambda row: row["trip_headsign"] == headsign)
            .select("direction_id")
        )
        direction_id = self._database.get(query).iloc[0]

        return SEQDirection[direction_id]


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
            time = datetime.strptime(stop_data["arrival_time"],
                                     "%H:%M:%S")
            time = timedelta(
                hours=time.hour, minutes=time.minute, seconds=time.second
            )
            stops.append(Stop(name, Coordinates(latitude, longitude), time))
        return Route(route_number, direction, stops)


if __name__ == "__main__":
    database = CSVDatabase(DATA_DIRECTORY)
    route_finder = RouteFinder(database)
    routes = route_finder.get_route(
        66,
        SEQDirection.ZERO,
        Coordinates(-27.48, 153.02),
        timedelta(hours=6, minutes=9),
    )


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
