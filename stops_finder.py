import datetime

from database import TransportDatabase
from model import RouteLocation, Stop, StopTime
from util import Coordinates


class NextStopsFinder:
    def __init__(self, transport_database: TransportDatabase):
        self._transport_database = transport_database

    def get_next_stop_times(
        self, route_location: RouteLocation
    ) -> list[StopTime]:
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
                current_location.coordinates,
                previous_stop_time.stop.coordinates,
            )
            / distance_between_stops
        )

        time_between_stops = (
            next_stop_time.route_time - previous_stop_time.route_time
        )

        return proportion_travelled * time_between_stops


class NoMoreStopsError(Exception):
    pass
