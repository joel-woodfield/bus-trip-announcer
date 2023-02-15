import flet as ft

from bus_trip_announcer.announcer import TripAnnouncer
from bus_trip_announcer.models import TripStatus
from bus_trip_announcer.specifiers.location_specifier import LocationSpecifier
from bus_trip_announcer.utils import Coordinates
from bus_trip_announcer.viewer import TripViewer


class GUITripViewerAndUpdator(TripViewer, LocationSpecifier):
    NUM_STOPS_DISPLAYED = 5

    def __init__(self, announcer: TripAnnouncer, page: ft.Page, current_status: TripStatus):
        self._trip_announcer = announcer
        self._page = page
        self._current_status = current_status

        if self._page.controls:
            self._page.controls.pop()

        self._init_coordinates_field()

    def _init_coordinates_field(self):
        def btn_clicked(e):
            self._current_status.coordinates = Coordinates(
                float(latitude.value),
                float(longitude.value),
            )
            self.specify_coordinates()

        latitude = ft.TextField(value=str(self._current_status.coordinates.latitude),
                                width=150)
        row1 = ft.Row(controls=[
            ft.Text("Current Latitude"),
            latitude,
        ])

        longitude = ft.TextField(value=str(self._current_status.coordinates.longitude),
                                 width=150)
        row2 = ft.Row(controls=[
            ft.Text("Current Longitude"),
            longitude,
        ])

        self._page.add(ft.Column(controls=[
            row1,
            row2,
            ft.ElevatedButton("Update", on_click=btn_clicked)
        ]))

    def show_next_stops(self) -> None:
        if len(self._page.controls) > 1:
            self._page.controls.pop()
        next_stops = self._trip_announcer.next_stops

        stop_names = [stop.name for stop in next_stops]
        stop_times = [self._time_until_stop_format(stop.time_until_stop)
                      for stop in next_stops]

        information = ft.Row(controls=[
            ft.Column(controls=[ft.Text(name) for name in stop_names]),
            ft.Column(controls=[ft.Text(time) for time in stop_times]),
        ])

        self._page.add(ft.Column(controls=[
            ft.Text("Next Stops"),
            information,
        ]))

    def specify_coordinates(self) -> None:
        self._trip_announcer.update_next_stops(self._current_status)