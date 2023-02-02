from model import RouteLocation
from stops_finder import NextStopsFinder


class TripAnnouncer:
    def __init__(self, next_stops_finder: NextStopsFinder):
        self._next_stops_finder = next_stops_finder
        self.next_stop_times = None
        self.route_number = -1

    def update_next_stop_times(self, location: RouteLocation):
        self.route_number = location.route_number
        self.next_stop_times = self._next_stops_finder.get_next_stop_times(
            location
        )
