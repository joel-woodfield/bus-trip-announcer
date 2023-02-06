"""
Contains the classes that display the trip information.
"""

import datetime
from typing import Protocol

from announcer import TripAnnouncer


class TripViewer(Protocol):
    """
    Displays the next stop.
    """

    def show_next_stops(self) -> None:
        """Displays the next stop."""


class CommandlineDisplay(TripViewer):
    """
    Displays the next stop on the commandline.
    """

    def __init__(self, trip_announcer: TripAnnouncer):
        """
        Initializes the display with the given announcer
        :param trip_announcer: the announcer that tells the next stops and
            their times
        """
        self._trip_announcer = trip_announcer

    def show_next_stops(self) -> None:
        """Displays the next stops on the commandline."""
        stops_display = "\n".join(
            f"{stop.name}"
            f" | {self._route_time_format(stop.time_until_stop)}"
            for stop in self._trip_announcer.next_stops
        )

        header_length = max(len(line) for line in stops_display.split("\n"))
        header = f"Route {self._trip_announcer.route_number}".center(
            header_length, "-"
        )
        print("\n" + header)
        print(stops_display + "\n")

    @classmethod
    def _route_time_format(cls, route_time: datetime.timedelta) -> str:
        """
        Returns the formatted route time for the display.
        :param route_time: the route time
        :return: the formatted route time
        """
        hours, minutes, _ = str(route_time).split(":")
        if int(hours) == 0:
            return f"{int(minutes)}min"
        return f"{int(hours)}hr {int(minutes)}min"
