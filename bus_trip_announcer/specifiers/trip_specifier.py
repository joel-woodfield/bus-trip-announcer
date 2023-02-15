"""
This module allows for the ability to specify the trip for the announcer
to display the next stops for.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import flet as ft

from bus_trip_announcer.announcer import TripAnnouncer
from bus_trip_announcer.database.finders import DirectionFinder, TripFinder
from bus_trip_announcer.models import Trip, TripStatus
from bus_trip_announcer.stops_finder import NextStopsFinder
from bus_trip_announcer.utils import Coordinates


class TripSpecifier(ABC):
    """
    A specifier for the user to specify the trip they are going on.
    """
    def __init__(
        self, direction_finder: DirectionFinder, trip_finder: TripFinder
    ):
        """
        Initializes the trip specifier with the given finders.
        :param direction_finder: the direction finder
        :param trip_finder: the route finder
        """
        self._direction_finder = direction_finder
        self._trip_finder = trip_finder
        self.trip_status = TripStatus()
        self._time = None

    @abstractmethod
    def specify_route_number(self) -> None:
        """
        Specifies the route number.
        """

    @abstractmethod
    def specify_direction(self) -> None:
        """
        Specifies the direction.
        """

    @abstractmethod
    def specify_coordinates(self) -> None:
        """
        Specifies the coordinates.
        """

    @abstractmethod
    def specify_time(self) -> None:
        """
        Specifies the time.
        """


class CommandLineTripSpecifier(TripSpecifier):
    """
    A TripSpecifier with a command line UI.
    """
    def specify_route_number(self):
        number = int(input("Input route number: "))
        self.trip_status.route_number = number

    def specify_direction(self):
        """
        Specifies the direction.

        It prints the possible headsigns for the route number previously input.
        It asks for the user to select the headsign they saw, which is used
        to figure out the direction.

        Requires specify_route_number to have been called first.
        """
        if self.trip_status.route_number is None:
            raise NoRouteNumberError
        headsigns = self._direction_finder.get_headsigns(
            self.trip_status.route_number
        )
        print("Which headsign did you see?")
        for i, headsign in enumerate(headsigns, 1):
            print(f"{i}: {headsign}")
        selection = int(input("Enter number: ")) - 1

        direction = self._direction_finder.get_direction(
            self.trip_status.route_number, headsigns[selection]
        )
        self.trip_status.direction = direction

    def specify_coordinates(self):
        latitude = input("Input Latitude: ")
        longitude = input("Input Longitude: ")
        self.trip_status.coordinates = Coordinates(
            float(latitude), float(longitude)
        )

    def specify_time(self):
        """
        Specifies the current time.

        The input time must be in 24hr time and in the format hours:min.
        """
        time = input("Input time: ")
        t = datetime.strptime(time, "%H:%M")
        self._time = timedelta(hours=t.hour, minutes=t.minute)

    def specify_all(self):
        """
        Specifies all the required information.
        """
        self.specify_route_number()
        self.specify_direction()
        self.specify_coordinates()
        self.specify_time()

    def _get_trip(self) -> Trip:
        """
        Returns the trip with the fully-specified trip status and time.
        """
        return self._trip_finder.get_trip(
            self.trip_status.route_number,
            self.trip_status.direction,
            self.trip_status.coordinates,
            self._time,
        )

    def create_announcer(self) -> TripAnnouncer:
        """
        Creates an announcer with the fully-specified trip status and time.
        """
        stops_finder = NextStopsFinder(self._get_trip())
        announcer = TripAnnouncer(stops_finder)
        announcer.update_next_stops(self.trip_status)

        return announcer


class GUITripSpecifier(TripSpecifier):

    def __init__(self, direction_finder: DirectionFinder, trip_finder: TripFinder, page: ft.Page):
        super().__init__(direction_finder, trip_finder)
        self._page = page

    def specify_route_number(self) -> None:
        def btn_clicked(_):
            self.trip_status.route_number = int(field.value)
            self._page.controls.pop()
            self.specify_direction()

        field = ft.TextField(width=100)
        self._page.add(
            ft.Row(controls=[
                ft.Text("Route Number"),
                field,
                ft.ElevatedButton(text="Enter", on_click=btn_clicked),
            ])
        )

    def specify_direction(self) -> None:
        def btn_i_clicked(i):
            def btn_clicked(e):
                direction = self._direction_finder.get_direction(
                    self.trip_status.route_number, headsigns[i]
                )
                self.trip_status.direction = direction
                self._page.controls.pop()
                self.specify_coordinates()
            return btn_clicked

        headsigns = self._direction_finder.get_headsigns(
            self.trip_status.route_number
        )

        prompt = ft.Text("Which Headsign?")

        headsign_buttons = []
        for i, headsign in enumerate(headsigns):
            headsign_buttons.append(ft.FilledTonalButton(text=headsign,
                                                      on_click=btn_i_clicked(i)))

        self._page.add(ft.Column(controls=[prompt, *headsign_buttons]))

    def specify_coordinates(self) -> None:
        def btn_clicked(e):
            self.trip_status.coordinates = Coordinates(
                float(latitude.value), float(longitude.value)
            )
            self._page.controls.pop()
            self.specify_time()

        latitude = ft.TextField(width=150)
        row1 = ft.Row(controls=[
            ft.Text("Current Latitude"),
            latitude,
        ])

        longitude = ft.TextField(width=150)
        row2 = ft.Row(controls=[
            ft.Text("Current Longitude"),
            longitude,
        ])

        self._page.add(ft.Column(controls=[
            row1,
            row2,
            ft.ElevatedButton("Enter", on_click=btn_clicked)
        ]))

    def specify_time(self) -> None:
        def btn_clicked(e):
            self._time = timedelta(hours=int(hours.value), minutes=int(minutes.value))
            self._page.controls.pop()

        prompt = ft.Text("Enter the time")
        hours = ft.TextField(hint_text="HH", width=100)
        minutes = ft.TextField(hint_text="MM", width=100)
        inputs = ft.Row(controls=[
            hours,
            ft.Text(":"),
            minutes
        ])

        self._page.add(ft.Column(controls=[
            prompt,
            inputs,
            ft.ElevatedButton("Enter", on_click=btn_clicked)
        ]))

    def specify_all(self):
        self.specify_route_number()


class NoRouteNumberError(Exception):
    """
    The Route number has not been specified yet.
    """
