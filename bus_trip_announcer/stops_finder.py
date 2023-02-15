"""
Module that contains classes that computes the next stops of the trip.
"""

from bus_trip_announcer.models import Trip, Stop
from bus_trip_announcer.utils import Coordinates, Line


class NextStopsFinder:
    """
    A finder that finds the next stops of the trip.
    """

    def __init__(self, trip: Trip):
        """
        Initializes the finder with the given trip.
        :param trip: the trip
        """
        self._trip = trip

    @classmethod
    def get_in_between_stops(
        cls, stops: list[Stop], location: Coordinates
    ) -> tuple[Stop, Stop]:
        """
        Finds the two stops in the list of stops that the location is most
        likely in between.

        For each pair of successive stops, we create a direct line that
        connects them. We then find the minimum distance from the location
        to the line. The line with the minimum of these minimum distances will
        be the line connecting the two desired stops.
        :param stops: the stops of the trip
        :param location: the location in between stops
        :return: a tuple of the two stops:
            (previous_stop, next_stops)
        """
        distances = []
        for i in range(len(stops) - 1):
            stop1 = stops[i]
            stop2 = stops[i + 1]
            direct_line = Line(stop1.coordinates, stop2.coordinates)
            distance_to_line = Line.minimum_distance(direct_line, location)
            distances.append(distance_to_line)

        previous_stop_index = distances.index(min(distances))
        return (stops[previous_stop_index], stops[previous_stop_index + 1])

    def get_next_stops(self, location: Coordinates) -> list[Stop]:
        """
        Gets the next stops on the route based on the given location.
        :param location: the current location
        :return: the next stops
        """
        previous_stop, next_stop = self.get_in_between_stops(
            self._trip.stops, location
        )
        time_since_trip_start = self._time_since_trip_start(
            previous_stop, next_stop, location
        )
        next_stop_index = self._trip.stops.index(next_stop)

        # for each of the next stops, update the time until stop
        next_stops = []
        for stop in self._trip.stops[next_stop_index:]:
            updated_stop = Stop(
                stop.name,
                stop.coordinates,
                stop.time_until_stop - time_since_trip_start,
            )
            next_stops.append(updated_stop)
        return next_stops

    @classmethod
    def _proportion_travelled(
        cls, previous_stop: Stop, next_stop: Stop, location: Coordinates
    ) -> float:
        """
        Returns the proportion travelled between the two stops.

        This is estimated using the following expression:

        $$
        distance(previous_stop, location)
        /
        [distance(previous_stop, location) + distane(location, next_stop)]
        $$
        :param previous_stop: the previous stop
        :param next_stop: the next stop
        :param location: the current location
        :return: the proportion travelled between the two stops
        """
        distance_from_previous = Coordinates.distance_between(
            location, previous_stop.coordinates
        )
        distance_to_next = Coordinates.distance_between(
            location, next_stop.coordinates
        )
        return distance_from_previous / (
            distance_from_previous + distance_to_next
        )

    @classmethod
    def _time_since_trip_start(
        cls, previous_stop: Stop, next_stop: Stop, location: Coordinates
    ):
        """
        Estimates the time it took for the bus to get to its current location.
        :param previous_stop: the previous stop
        :param next_stop: the next stop
        :param location: the current location
        :return: the time it took for the bus to reach its current location
        """
        proportion_travelled = cls._proportion_travelled(
            previous_stop, next_stop, location
        )
        time_between_stops = (
            next_stop.time_until_stop - previous_stop.time_until_stop
        )
        time_since_last_stop = proportion_travelled * time_between_stops
        return previous_stop.time_until_stop + time_since_last_stop
