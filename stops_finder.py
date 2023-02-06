"""
Contains classes that computes the next stops in the route.
"""

import datetime

from database import TransportDatabase
from models import User, Stop
from utils import Coordinates, Direction


class NextStopsFinder:
    """
    Finds the next stops in the user's bus trip.

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

    def get_next_stops(self, user: User) -> list[Stop]:
        """
        Returns the next stops for the given user.
        :param user: the user
        :return: the list of the next stops for the user
        """
        route = self._transport_database.get_route(
            user.bus_route_number, user.direction
        )

        try:
            next_stop_index = self._get_next_stop_index(route.stops, user)
        except NoMoreStopsError:
            # the user is past the last stop, so there are no more
            # next stops
            return []

        if next_stop_index == 0:
            # the user is at the start of the route, so no updates
            # to the route times are required
            return route.stops

        # update the route times
        next_stop = route.stops[next_stop_index]
        previous_stop = route.stops[next_stop_index - 1]
        current_time_until_stop = self._current_time_on_route_estimate(
            previous_stop, next_stop, user
        )
        next_stops = [
            Stop(
                stop.name,
                stop.coordinates,
                stop.time_until_stop - current_time_until_stop,
            )
            for stop in route.stops[next_stop_index:]
        ]

        return next_stops

    @classmethod
    def _get_next_stop_index(cls, stops: list[Stop], user: User) -> int:
        """
        Returns the index in the route's list of stops for the next stop
        in the trip after the user's current location.
        :param stops: the stops for the route
        :param user: the user
        :return: the index in the list for the next stop
        :raises NoMoreStopsError: if there is no more stops in the route after
        the current user's location.
        """
        for i, stop in enumerate(stops):
            if stop.is_after(user):
                return i
        raise NoMoreStopsError

    @classmethod
    def _current_time_on_route_estimate(
        cls,
        previous_stop: Stop,
        next_stop: Stop,
        user: User,
    ) -> datetime.timedelta:
        """
        Estimates the time it has taken for the bus to reach the user's current
        location.

        This is calculated by calculating the proportion the user has travelled
        between the previous and next stops in the direction of the route.
        The estimated time is then:

        $$ proportion * time_between_stops + previous_stop.time_until_stop $$

        :param previous_stop: the stop of the stop preceding the
            current location
        :param next_stop: the stop of the stop succeeding the current
            location
        :param user: the user
        :return: the estimated time it has taken for the bus to reach the
            user's location
        """
        proportion_travelled = cls._proportion_travelled(
            user, previous_stop, next_stop
        )

        time_between_stops = (
            next_stop.time_until_stop - previous_stop.time_until_stop
        )

        return (
            proportion_travelled * time_between_stops
            + previous_stop.time_until_stop
        )

    @classmethod
    def _proportion_travelled(
        cls,
        user_location: User,
        previous_stop: Stop,
        next_stop: Stop,
    ) -> float:
        """
        Returns the proportion the user has travelled between the previous and
        the next stops in the direction of the route.

        If the user has travelled backwards, it will return 0.
        :param user_location: the user's current location
        :param next_stop: the next stop
        :param previous_stop: the previous stop
        :return: the proportion the user has travelled between the stops
        """
        if user_location.direction is Direction.NORTH:
            stops_distance = Coordinates.latitude_distance_between(
                previous_stop.coordinates, next_stop.coordinates
            )
            user_distance = Coordinates.latitude_distance_between(
                previous_stop.coordinates, user_location.coordinates
            )
        elif user_location.direction is Direction.SOUTH:
            stops_distance = -Coordinates.latitude_distance_between(
                previous_stop.coordinates, next_stop.coordinates
            )
            user_distance = -Coordinates.latitude_distance_between(
                previous_stop.coordinates, user_location.coordinates
            )
        elif user_location.direction is Direction.EAST:
            stops_distance = Coordinates.longitude_distance_between(
                previous_stop.coordinates, next_stop.coordinates
            )
            user_distance = Coordinates.longitude_distance_between(
                previous_stop.coordinates, user_location.coordinates
            )
        elif user_location.direction is Direction.WEST:
            stops_distance = -Coordinates.longitude_distance_between(
                previous_stop.coordinates, next_stop.coordinates
            )
            user_distance = -Coordinates.longitude_distance_between(
                previous_stop.coordinates, user_location.coordinates
            )

        return max(user_distance / stops_distance, 0)


class NoMoreStopsError(Exception):
    """
    There are no more stops left in the route.
    """
