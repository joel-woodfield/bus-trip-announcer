import datetime

from model import Route, Stop, StopTime
from util import Coordinates, Direction


class TransportDatabase:
    def get_route(self, number: int, direction: Direction) -> Route:
        raise NotImplementedError


class LocalDatabase(TransportDatabase):
    def get_route(self, number: int, direction: Direction) -> Route:
        with open("test_database.csv", "r") as file:
            _ = next(file)  # this is the header
            data = (line.rstrip().split(",") for line in file)

            route_data = (
                row
                for row in data
                if int(row[4]) == number and Direction[row[5]] == direction
            )

            stop_times = []
            for row in route_data:
                (
                    stop_name,
                    route_time,
                    latitude,
                    longitude,
                    route_number,
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
