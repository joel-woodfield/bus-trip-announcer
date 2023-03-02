from __future__ import annotations

import functools
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import flet as ft
from waiting import wait

from bus_trip_announcer.database.finders import DirectionFinder, TripFinder
from bus_trip_announcer.models import TripStatus
from bus_trip_announcer.utils import Coordinates


class LocationInput:
    def __init__(self, input_device: InputDevice):
        self._input_device = input_device

    def input_coordinates(self):
        self._input_device.input_coordinates()


class TripInput:
    def __init__(self, input_device: InputDevice):
        self._input_device = input_device
        self._location_input = LocationInput(input_device)

    def input_coordinates(self) -> None:
        self._location_input.input_coordinates()

    def input_time(self) -> None:
        self._input_device.input_time()

    def input_route_number(self) -> None:
        self._input_device.input_route_number()

    def input_direction(self) -> None:
        self._input_device.input_direction()

    def input_all(self) -> None:
        self.input_route_number()
        self.input_direction()
        self.input_coordinates()
        self.input_time()

    def get_trip_status(self) -> TripStatus:
        return self._input_device.trip_status

    def get_time(self) -> timedelta:
        return self._input_device.time


class InputDevice(ABC):
    def __init__(self, direction_finder: DirectionFinder):
        self._direction_finder = direction_finder
        self.trip_status = TripStatus()
        self.time = None

    @abstractmethod
    def input_coordinates(self) -> None:
        pass

    @abstractmethod
    def input_time(self) -> None:
        pass

    @abstractmethod
    def input_route_number(self) -> None:
        pass

    @abstractmethod
    def input_direction(self) -> None:
        pass


class CommandLineInputDevice(InputDevice):
    def input_coordinates(self) -> None:
        latitude = input("Input Latitude: ")
        longitude = input("Input Longitude: ")
        new_coordinates = Coordinates(float(latitude), float(longitude))

        current = self.trip_status
        self.trip_status = TripStatus(
            current.route_number, current.direction, new_coordinates
        )

    def input_time(self) -> None:
        """
        Specifies the current time.

        The input time must be in 24hr time and in the format hours:min.
        """
        time = input("Input time: ")
        t = datetime.strptime(time, "%H:%M")
        self.time = timedelta(hours=t.hour, minutes=t.minute)

    def input_route_number(self) -> None:
        number = int(input("Input route number: "))
        self.trip_status.route_number = number

    def input_direction(self) -> None:
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


class FletInputDevice(InputDevice):
    def __init__(
        self,
        direction_finder: DirectionFinder,
        page: ft.Page,
    ):
        super().__init__(direction_finder)
        self._page = page

    def _has_been_called(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wrapper.has_been_called = True
            return func(*args, **kwargs)
        wrapper.has_been_called = False
        return wrapper

    def input_route_number(self) -> None:
        @self._has_been_called
        def btn_clicked(_):
            self.trip_status.route_number = int(field.value)
            self._page.controls.pop(0)

        field = ft.TextField(width=100)
        self._page.add(
            ft.Row(
                controls=[
                    ft.Text("Route Number"),
                    field,
                    ft.ElevatedButton(text="Enter", on_click=btn_clicked),
                ]
            )
        )
        wait(lambda: btn_clicked.has_been_called)

    def input_direction(self) -> None:
        def btn_i_clicked(i):
            @self._has_been_called
            def btn_clicked(_):
                direction = self._direction_finder.get_direction(
                    self.trip_status.route_number, headsigns[i]
                )
                self.trip_status.direction = direction
                self._page.controls.pop(0)
            return btn_clicked

        headsigns = self._direction_finder.get_headsigns(
            self.trip_status.route_number
        )

        prompt = ft.Text("Which Headsign?")

        headsign_buttons = []
        button_functions = []
        for i, headsign in enumerate(headsigns):
            btn_clicked = btn_i_clicked(i)
            button_functions.append(btn_clicked)
            headsign_buttons.append(
                ft.FilledTonalButton(text=headsign, on_click=btn_clicked)
            )

        self._page.add(ft.Column(controls=[prompt, *headsign_buttons]))

        wait(lambda: True in [btn.has_been_called for btn in button_functions])

    def input_coordinates(self) -> None:
        @self._has_been_called
        def btn_clicked(_):
            self.trip_status.coordinates = Coordinates(
                float(latitude.value), float(longitude.value)
            )
            self._page.controls.pop(0)

        latitude = ft.TextField(width=150)
        row1 = ft.Row(
            controls=[
                ft.Text("Current Latitude"),
                latitude,
            ]
        )

        longitude = ft.TextField(width=150)
        row2 = ft.Row(
            controls=[
                ft.Text("Current Longitude"),
                longitude,
            ]
        )

        self._page.add(
            ft.Column(
                controls=[
                    row1,
                    row2,
                    ft.ElevatedButton("Enter", on_click=btn_clicked),
                ]
            )
        )
        wait(lambda: btn_clicked.has_been_called)

    def input_time(self) -> None:
        @self._has_been_called
        def btn_clicked(e):
            self.time = timedelta(
                hours=int(hours.value), minutes=int(minutes.value)
            )
            self._page.controls.pop(0)

        prompt = ft.Text("Enter the time")
        hours = ft.TextField(hint_text="HH", width=100)
        minutes = ft.TextField(hint_text="MM", width=100)
        inputs = ft.Row(controls=[hours, ft.Text(":"), minutes])

        self._page.add(
            ft.Column(
                controls=[
                    prompt,
                    inputs,
                    ft.ElevatedButton("Enter", on_click=btn_clicked),
                ]
            )
        )
        wait(lambda: btn_clicked.has_been_called)


class NoRouteNumberError(Exception):
    """
    The Route number has not been specified yet.
    """
