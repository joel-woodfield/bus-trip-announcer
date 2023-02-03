"""
Contains the announcer that keeps track of the next stops in the bus trip.
"""

from models import RouteLocation
from stops_finder import NextStopsFinder


class TripAnnouncer:
    """
    Keeps track of what the next stops are and the time until the bus reaches
    those stops (StopTime objects).

    The method update_next_stop_times must be called to update the information
    as the bus travels.

    Attributes
    ----------
    _next_stops_finder: NextStopsFinder
        the NextStopsFinder object for the announcer to retrieve the next
        stops from
    next_stop_times: List[StopTime]
        the next stop times in the bus trip
    route_number: int
        the route number of the bus trip the announcer is getting the stops for
    """

    def __init__(self, next_stops_finder: NextStopsFinder):
        """
        Initializes the announcer with a NextStopsFinder object to be able to
         retrieve the next stops.
        :param next_stops_finder: the NextStopsFinder object for the announcer
            to retrieve the next stops from
        """
        self._next_stops_finder = next_stops_finder
        self.next_stop_times = None
        self.route_number = -1

    def update_next_stop_times(self, location: RouteLocation) -> None:
        """
        Updates the next stop times the announcer is keeping track of
        for the new route location.
        :param location: the new route location
        """
        self.route_number = location.route_number
        self.next_stop_times = self._next_stops_finder.get_next_stop_times(
            location
        )
