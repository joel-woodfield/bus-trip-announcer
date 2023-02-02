import datetime

from util import Coordinates, Direction


class RouteLocation:
    def __init__(
        self,
        route_number: int = 0,
        direction: Direction = Direction.NORTH,
        coordinates: Coordinates = Coordinates(0, 0),
    ):
        self.route_number = route_number
        self.direction = direction
        self.coordinates = coordinates


class Stop:
    def __init__(self, name: str, coordinates: Coordinates):
        self.name = name
        self.coordinates = coordinates

    @classmethod
    def distance_between(cls, stop1: "Stop", stop2: "Stop"):
        return Coordinates.distance_between(
            stop1.coordinates, stop2.coordinates
        )

    def __str__(self):
        return f"Stop({self.name}, {self.coordinates})"


class StopTime:
    def __init__(self, stop: Stop, route_time: datetime.timedelta):
        self.stop = stop
        self.route_time = route_time

    def is_after(self, route_location: RouteLocation) -> bool:
        if route_location.direction == Direction.NORTH:
            return (
                self.stop.coordinates.latitude
                >= route_location.coordinates.latitude
            )
        if route_location.direction == Direction.SOUTH:
            return (
                self.stop.coordinates.latitude
                <= route_location.coordinates.latitude
            )
        if route_location.direction == Direction.EAST:
            return (
                self.stop.coordinates.longitude
                >= route_location.coordinates.longitude
            )
        if route_location.direction == Direction.WEST:
            return (
                self.stop.coordinates.longitude
                <= route_location.coordinates.longitude
            )

    def __repr__(self):
        return f"StopTime({self.stop}, {self.route_time})"


class Route:
    def __init__(
        self, number: int, direction: Direction, stop_times: list[StopTime]
    ):
        self.number = number
        self.direction = direction
        self.stop_times = stop_times

    def __str__(self):
        return f"Route {self.number} {self.direction}:\n{self.stop_times}"
