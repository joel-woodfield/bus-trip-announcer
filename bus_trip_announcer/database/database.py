"""
Module that provides query access to the SEQ transport database.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Protocol

import pandas as pd

from models import Route, Stop
from utils import Coordinates, Direction

# file paths to the csv files
DATA_DIRECTORY = "useful_data"
TABLE_FILE_PATH = {
    "routes": DATA_DIRECTORY + "/routes.csv",
    "stops": DATA_DIRECTORY + "/stops.csv",
    "stop_times": DATA_DIRECTORY + "/stop_times.csv",
    "trips": DATA_DIRECTORY + "/trips.csv",
}


class QueryOperation(Enum):
    """
    The operations supported by the Query class.

    SELECT: Retrieves specified columns.
    JOIN: An inner join is performed on the specified columns.
    WHERE: Retrieves rows that satisfy the condition.
    ORDER_BY: Sorts the table on a column.
    """

    SELECT = 1
    JOIN = 2
    WHERE = 3
    ORDER_BY = 4


class Query:
    """
    An object that specifies the query instructions to the Database.

    It currently supports four operations. They are identified by the
    QueryOperation enum.

    SELECT: Retrieves specified columns.
    JOIN: An inner join is performed on the specified columns.
    WHERE: Retrieves rows that satisfy the condition.
    ORDER_BY: Sorts the table on a column.

    The methods correspond to the operations the user wants to do on the
    database. Each time a method is called, it stores the operation and its
    arguments, which is processed by the Database classes.

    Each method will return the query itself, so many operations
    can be chained like as follows:
    ```
    query = Query("routes").join("trips", "route_id").select("route_id")
    ```
    """

    # constants that identify an operation
    SELECT = "select"
    JOIN = "join"
    WHERE = "where"
    ORDER_BY = "order by"

    def __init__(self, table_name: str):
        """
        Initializes the query on the table with the given table name.
        :param table_name: the name of the table to be queried
        """
        self.table_name = table_name
        self.operations = []

    def select(self, columns: str | list[str]):
        """
        Adds a select operation to the query.

        It retrieves the columns of the table specified by the parameter to
        this method.
        :param columns: The column(s) to be retrieved from the table
        :return: the query object itself.
        """
        self.operations.append((QueryOperation.SELECT, columns))
        return self

    def join(self, table_name: str, join_column: str):
        """
        Adds a join operation to the query.

        It joins the current table with the new table on the specified join
        column.
        :param table_name: the name of the table to be joined
        :param join_column: the column the new table is joining on
        :return: the query object itself
        """
        self.operations.append(
            (QueryOperation.JOIN, (table_name, join_column))
        )
        return self

    def where(self, condition: Callable):
        """
        Adds a where operation to the query.

        It retrieves the rows of the table that satisfy the given condition.
        The condition must be a Callable of the form
        ```
        f(row) -> bool
        ```
        :param condition: the condition to be placed on each row.
        :return: the query object itself
        """
        self.operations.append((QueryOperation.WHERE, condition))
        return self

    def order_by(self, column: str, ascending: bool = True):
        """
        Adds an order by operation to the query.

        It sorts the rows of the tabl on the specified column.
        :param column: the column to be sorted on
        :param ascending: the sorting order
        :return: the query object itself
        """
        self.operations.append((QueryOperation.ORDER_BY, (column, ascending)))
        return self


class Database(Protocol):
    """
    An interface for the transport database.
    """

    def get(self, query: Query) -> pd.DataFrame:
        """
        Retrieves the table that satisfies the query.
        :return: the table that satisfies the query
        """


class CSVDatabase(Database):
    """
    The class that supports query access to the local database of csv files.

    Attributes
    ----------
    _data_directory:
        the file path to the directory of the csv files
    """

    def __init__(self, data_directory: str):
        """
        Specifies the file path to the directory of the csv data files.
        :param data_directory: the file path to the directory of the csv files
        """
        self._data_directory = data_directory

    def get(self, query: Query) -> pd.DataFrame:
        result = pd.read_csv(self._file_path(query.table_name))
        for operation, args in query.operations:
            result = self._process_operation(operation, result, args)
        return result

    def _file_path(self, table_name) -> str:
        """
        Retrieves the file path to the table with the given name.
        :param table_name: the name of the table
        :return: the file path to the table
        """
        return f"{self._data_directory}/{table_name}.csv"

    def _process_operation(
        self, operation: QueryOperation, table: pd.DataFrame, args: tuple
    ) -> pd.DataFrame:
        """
        Processes the given query operation on the given table.
        :param operation: the operation type
        :param table: the table to do the operation on
        :param args: the arguments to the operation
        :return: the table with the operations done on it
        """
        if operation == QueryOperation.SELECT:
            columns = args
            return table[columns]
        elif operation == QueryOperation.JOIN:
            table_name, join_column = args
            join_table = pd.read_csv(self._file_path(table_name))
            return pd.merge(table, join_table, on=join_column)
        elif operation == QueryOperation.WHERE:
            condition = args
            return table[condition]
        elif operation == QueryOperation.ORDER_BY:
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
    DATABASE_FILE = "../../data/test_database1.csv"

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
                time_until_stop = datetime.strptime(
                    time_until_stop, "%H:%M"
                )
                time_until_stop = timedelta(
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
