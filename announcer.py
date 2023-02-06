"""
Contains the announcer that keeps track of the next stops in the bus trip.
"""

from models import User
from stops_finder import NextStopsFinder


class TripAnnouncer:
    """
    Keeps track of what the next stops are and the time until the bus reaches
    those stops.

    The method update_next_stops must be called to update the information
    as the bus travels.

    Attributes
    ----------
    _next_stops_finder: NextStopsFinder
        the NextStopsFinder object for the announcer to retrieve the next
        stops from
    next_stops: List[Stop]
        the next stops in the bus trip
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
        self.next_stops = None
        self.route_number = -1

    def update_next_stops(self, user: User) -> None:
        """
        Updates the next stops the announcer is keeping track of
        for the user with an updated location.
        :param user: the user
        """
        self.route_number = user.bus_route_number
        self.next_stops = self._next_stops_finder.get_next_stops(user)
