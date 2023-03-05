"""
Contains the announcer that keeps track of the next stops in the bus trip.
"""

from bus_trip_announcer.models import Stop, TripStatus
from bus_trip_announcer.stops_finder import NextStopsFinder


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
    next_stops: list[Stop]
        the next stops in the bus trip
    route_number: int
        the route number of the bus trip the announcer is getting the stops for
    """

    def __init__(self, trip_status: TripStatus):
        """
        Initializes the announcer with a NextStopsFinder object to be able to
        retrieve the next stops.
        """
        self.next_stops_finder = None
        self.trip_status = trip_status
        self.next_stops = None

    def update_next_stops(self) -> None:
        """
        Updates the next stops the announcer is keeping track of
        for the updated trip status.
        """
        self.next_stops = self.next_stops_finder.get_next_stops(
            self.trip_status.coordinates
        )
