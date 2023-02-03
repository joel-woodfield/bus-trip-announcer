"""
Contains classes that computes the next stops in the route.
"""

import datetime

from database import TransportDatabase
from models import RouteLocation, Stop, StopTime
from utils import Coordinates


class NextStopsFinder:
    """
    Finds the next stops for a given route and the route location.

    Attributes
    ----------
    _transport_database: TransportDatabase
        the database of the routes and stops for the finder to use
    """

    def __init__(self, transport_database: TransportDatabase):
        """
        Initializes the finder with the give database
        :param transport_database: the database for the finder to use
        """
        self._transport_database = transport_database

    def get_next_stop_times(
        self, route_location: RouteLocation
    ) -> list[StopTime]:
        """
        Returns the next stop times for the given route location.
        :param route_location: the route location
        :return: the list of the next stop times.
        """
        route = self._transport_database.get_route(
            route_location.route_number, route_location.direction
        )

        try:
            next_stop_index = self._get_next_stop_index(
                route.stop_times, route_location
            )
        except NoMoreStopsError:
            # the route location is past the last stop, so there are no more
            # next stops
            return []

        if next_stop_index == 0:
            # the route location is at the start of the route, so no updates
            # to the route times are required
            return route.stop_times

        # update the route times
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

    @classmethod
    def _get_next_stop_index(
        cls, stop_times: list[StopTime], route_location: RouteLocation
    ) -> int:
        """
        Returns the index in the route's list of stop times for the next stop
        in the trip after the current route location.
        :param stop_times: the stop times for the route
        :param route_location: the current route location
        :return: the index in the list for the next stop
        :raises NoMoreStopsError: if there is no more stops in the route after
        the current route location.
        """
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
        """
        Estimates the time it has taken for the bus to reach the current
        location.

        This is calculated by calculating the distance from the previous stop
        to the current location, the distance from the previous stop to the
        next stop, and taking the proportion:

        $$ distance(previous stop, current location)
            / distance(previous stop, next stop) $$

        :param previous_stop_time: the stop time of the stop preceding the
            current location
        :param next_stop_time: the stop time of the stop succeeding the current
            location
        :param current_location: the current route location
        :return: the estimated time it has taken for the bus to reach the
            current location
        """
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

        return (
            proportion_travelled * time_between_stops
            + previous_stop_time.route_time
        )


class NoMoreStopsError(Exception):
    """
    There are no more stops left in the route.
    """

    pass
