"""
Contains the classes that display the trip information.
"""

import datetime
from typing import Protocol

import flet as ft

from bus_trip_announcer.announcer import TripAnnouncer
from bus_trip_announcer.models import TripStatus
from bus_trip_announcer.utils import Coordinates


class TripViewer(Protocol):
    """
    Displays the next stop.
    """

    def show_next_stops(self) -> None:
        """Displays the next stop."""

    @classmethod
    def _time_until_stop_format(
        cls, time_until_stop: datetime.timedelta
    ) -> str:
        """
        Returns the formatted route time for the display.
        :param time_until_stop: the route time
        :return: the formatted route time
        """
        hours, minutes, _ = str(time_until_stop).split(":")
        if int(hours) == 0:
            return f"{int(minutes)}min"
        return f"{int(hours)}hr {int(minutes)}min"


class CommandLineTripViewer(TripViewer):
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
            f" | {self._time_until_stop_format(stop.time_until_stop)}"
            for stop in self._trip_announcer.next_stops
        )

        header_length = max(len(line) for line in stops_display.split("\n"))
        header = f"Route {self._trip_announcer.trip_status.route_number}".center(
            header_length, "-"
        )
        print("\n" + header)
        print(stops_display + "\n")


class FletTripViewer(TripViewer):
    NUM_STOPS_DISPLAYED = 5

    def __init__(
        self,
        announcer: TripAnnouncer,
        page: ft.Page,
    ):
        self._trip_announcer = announcer
        self._page = page

        if self._page.controls:
            self._page.controls.pop()

    def show_next_stops(self) -> None:
        if len(self._page.controls) > 1:
            self._page.controls.pop()
        next_stops = self._trip_announcer.next_stops

        stop_names = [stop.name for stop in next_stops]
        stop_times = [
            self._time_until_stop_format(stop.time_until_stop)
            for stop in next_stops
        ]

        information = ft.Row(
            controls=[
                ft.Column(controls=[ft.Text(name) for name in stop_names]),
                ft.Column(controls=[ft.Text(time) for time in stop_times]),
            ]
        )

        self._page.add(
            ft.Column(
                controls=[
                    ft.Text("Next Stops"),
                    information,
                ]
            )
        )


