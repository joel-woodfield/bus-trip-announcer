import time
from datetime import timedelta

import flet as ft

from bus_trip_announcer.database.finders import TripFinder, DirectionFinder
from bus_trip_announcer.specifiers.trip_specifier import TripSpecifier
from bus_trip_announcer.utils import Coordinates


class GUITripSpecifier(TripSpecifier):
    def __init__(
        self,
        direction_finder: DirectionFinder,
        trip_finder: TripFinder,
        page: ft.Page,
    ):
        super().__init__(direction_finder, trip_finder)
        self._page = page
        self._fully_specified = False

    def specify_route_number(self) -> None:
        def btn_clicked(_):
            self.trip_status.route_number = int(field.value)
            self._page.controls.pop()
            self.specify_direction()

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
            headsign_buttons.append(
                ft.FilledTonalButton(text=headsign, on_click=btn_i_clicked(i))
            )

        self._page.add(ft.Column(controls=[prompt, *headsign_buttons]))

    def specify_coordinates(self) -> None:
        def btn_clicked(e):
            self.trip_status.coordinates = Coordinates(
                float(latitude.value), float(longitude.value)
            )
            self._page.controls.pop()
            self.specify_time()

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

    def specify_time(self) -> None:
        def btn_clicked(e):
            self._time = timedelta(
                hours=int(hours.value), minutes=int(minutes.value)
            )
            self._page.controls.pop()
            self._fully_specified = True

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

    def specify_all(self):
        self.specify_route_number()
        while not self._fully_specified:
            time.sleep(1)
