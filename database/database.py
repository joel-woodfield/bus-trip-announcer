"""
Manages the database that stores the route and stop information.
"""
from datetime import datetime
from typing import Callable, Protocol

import pandas as pd

from models import Route, Stop
from utils import Coordinates, Direction

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
    DATABASE_FILE = "../data/test_database1.csv"

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
