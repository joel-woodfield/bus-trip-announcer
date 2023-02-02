import datetime
import math
from enum import Enum


class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4


class Coordinates:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def distance_between(cls, coordinates1: "Coordinates", coordinates2: "Coordinates"):
        return math.sqrt(
            (coordinates1.latitude - coordinates2.latitude) ** 2
            + (coordinates1.longitude - coordinates2.longitude) ** 2
        )

    def __repr__(self):
        return f"Coordinates({self.latitude}, {self.longitude})"


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
        return Coordinates.distance_between(stop1.coordinates, stop2.coordinates)

    def __str__(self):
        return f"Stop({self.name}, {self.coordinates})"


class StopTime:
    def __init__(self, stop: Stop, route_time: datetime.timedelta):
        self.stop = stop
        self.route_time = route_time

    def is_after(self, route_location: RouteLocation) -> bool:
        if route_location.direction == Direction.NORTH:
            return self.stop.coordinates.latitude > route_location.coordinates.latitude
        if route_location.direction == Direction.SOUTH:
            return self.stop.coordinates.latitude < route_location.coordinates.latitude
        if route_location.direction == Direction.EAST:
            return (
                self.stop.coordinates.longitude > route_location.coordinates.longitude
            )
        if route_location.direction == Direction.WEST:
            return (
                self.stop.coordinates.longitude < route_location.coordinates.longitude
            )

    def __repr__(self):
        return f"StopTime({self.stop}, {self.route_time})"


class Route:
    def __init__(self, number: int, direction: Direction, stop_times: list[StopTime]):
        self.number = number
        self.direction = direction
        self.stop_times = stop_times

    def __str__(self):
        return f"Route {self.number} {self.direction}:\n{self.stop_times}"


class TransportDatabase:
    def get_route(self, number: int, direction: Direction) -> Route:
        raise NotImplementedError


class LocalDatabase(TransportDatabase):
    def get_route(self, number: int, direction: Direction) -> Route:
        with open("test_database.csv", "r") as file:
            headers = next(file)
            data = (line.rstrip().split(",") for line in file)

            route_data = (
                row
                for row in data
                if int(row[4]) == number and Direction[row[5]] == direction
            )

            stop_times = []
            for row in route_data:
                stop_name, route_time, latitude, longitude, route_number, _ = row
                route_time = datetime.datetime.strptime(route_time, "%H:%M")
                route_time = datetime.timedelta(
                    hours=route_time.hour, minutes=route_time.minute
                )
                stop = Stop(stop_name, Coordinates(float(latitude), float(longitude)))
                stop_times.append(StopTime(stop, route_time))

            return Route(number, direction, stop_times)


class NextStopsFinder:
    def __init__(self, transport_database: TransportDatabase):
        self._transport_database = transport_database

    def get_next_stop_times(self, route_location: RouteLocation) -> list[StopTime]:
        route = self._transport_database.get_route(
            route_location.route_number, route_location.direction
        )

        try:
            next_stop_index = self._get_next_stop_index(
                route.stop_times, route_location
            )
        except NoMoreStopsError:
            return []

        if next_stop_index == 0:
            return route.stop_times

        next_stop_time = route.stop_times[next_stop_index]
        previous_stop_time = route.stop_times[next_stop_index - 1]
        current_route_time = self._current_route_time_estimate(
            previous_stop_time, next_stop_time, route_location
        )

        next_stop_times = [
            StopTime(stop_time.stop, stop_time.route_time - current_route_time)
            for stop_time in route.stop_times[next_stop_index:]
        ]

        return next_stop_times

    def _get_next_stop_index(
        self, stop_times: list[StopTime], route_location: RouteLocation
    ):
        for i, stop_time in enumerate(stop_times):
            if stop_time.is_after(route_location):
                return i
        raise NoMoreStopsError

    @classmethod
    def _current_route_time_estimate(
        cls,
        previous_stop_time: StopTime,
        next_stop_time: StopTime,
        current_location: RouteLocation,
    ) -> datetime.timedelta:
        distance_between_stops = Stop.distance_between(
            previous_stop_time.stop, next_stop_time.stop
        )
        proportion_travelled = (
            Coordinates.distance_between(
                current_location.coordinates, previous_stop_time.stop.coordinates
            )
            / distance_between_stops
        )

        time_between_stops = next_stop_time.route_time - previous_stop_time.route_time

        return proportion_travelled * time_between_stops


class NoMoreStopsError(Exception):
    pass


class TripAnnouncer:
    def __init__(self, next_stops_finder: NextStopsFinder):
        self._next_stops_finder = next_stops_finder
        self.next_stop_times = None

    def update_next_stop_times(self, location: RouteLocation):
        self.next_stop_times = self._next_stops_finder.get_next_stop_times(location)


class TripViewer:
    def show_next_stop_times(self):
        raise NotImplementedError


class CommandlineDisplay(TripViewer):
    def __init__(self, trip_announcer: TripAnnouncer):
        self._trip_announcer = trip_announcer

    def show_next_stop_times(self):
        print(self._trip_announcer.next_stop_times)


class LocationSpecifier:
    def input_coordinates(self):
        raise NotImplementedError

    def input_route_number(self):
        raise NotImplementedError

    def input_direction(self):
        raise NotImplementedError

    def update_trip_announcer(self):
        raise NotImplementedError


class CommandlineLocationUpdator(LocationSpecifier):
    def __init__(self, trip_announcer: TripAnnouncer, current_location: RouteLocation):
        self._trip_announcer = trip_announcer
        self._current_location = current_location

    def input_route_number(self):
        new_route_number = int(input("Input route number: "))

        current = self._current_location
        self._current_location = RouteLocation(
            new_route_number, current.direction, current.coordinates
        )

    def input_direction(self):
        new_direction = Direction[input("Input the direction: ")]

        current = self._current_location
        self._current_location = RouteLocation(
            current.route_number, new_direction, current.coordinates
        )

    def input_coordinates(self):
        latitude = input("Input Latitude: ")
        longitude = input("Input Longitude: ")
        new_coordinates = Coordinates(float(latitude), float(longitude))

        current = self._current_location
        self._current_location = RouteLocation(
            current.route_number, current.direction, new_coordinates
        )

    def update_trip_announcer(self):
        self.input_route_number()
        self.input_direction()
        self.input_coordinates()
        self._trip_announcer.update_next_stop_times(self._current_location)


def main():
    database = LocalDatabase()
    stops_finder = NextStopsFinder(database)
    announcer = TripAnnouncer(stops_finder)
    updator = CommandlineLocationUpdator(announcer, RouteLocation())

    updator.update_trip_announcer()
    print(announcer.next_stop_times)


if __name__ == "__main__":
    main()
