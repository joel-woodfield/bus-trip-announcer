"""
The starting point for the commandline version of the Bus Trip Announcer
Application
"""
import flet as ft

from bus_trip_announcer.announcer import TripAnnouncer
from bus_trip_announcer.gui.viewer_updator import GUITripViewerAndUpdator
from bus_trip_announcer.inputs import TripInput, FletInputDevice
from bus_trip_announcer.stops_finder import NextStopsFinder
from database.database import CSVDatabase
from database.finders import DirectionFinder, TripFinder
from specifiers.location_specifier import CommandlineLocationSpecifier
from specifiers.trip_specifier import CommandLineTripSpecifier
from bus_trip_announcer.viewer import CommandlineDisplay


def main() -> None:
    """
    Initialize the application and run the input-output loop in the command
    line.
    """
    database = CSVDatabase("useful_data")
    trip_finder = TripFinder(database)
    direction_finder = DirectionFinder(database)
    trip_specifier = CommandLineTripSpecifier(direction_finder, trip_finder)
    trip_specifier.specify_all()
    announcer = trip_specifier.create_announcer()

    updator = CommandlineLocationSpecifier(
        announcer, trip_specifier.trip_status
    )
    display = CommandlineDisplay(announcer)

    while True:
        display.show_next_stops()
        updator.update_trip_announcer()


def main2(page: ft.Page) -> None:
    """
    Initialize the GUI application
    """
    page.window_width = 500
    page.window_height = 700

    database = CSVDatabase("useful_data")
    trip_finder = TripFinder(database)
    direction_finder = DirectionFinder(database)
    # trip_specifier = GUITripSpecifier(direction_finder, trip_finder, page)
    # trip_specifier.specify_all()
    # announcer = trip_specifier.create_announcer()

    input_device = FletInputDevice(direction_finder, page)
    trip_input = TripInput(input_device)
    trip_input.input_all()

    trip_status = trip_input.get_trip_status()
    time = trip_input.get_time()
    trip = trip_finder.get_trip(trip_status.route_number,
                                trip_status.direction,
                                trip_status.coordinates,
                                time)
    announcer = TripAnnouncer(NextStopsFinder(trip), trip_status)



    viewer_updator = GUITripViewerAndUpdator(
        announcer, page, trip_input.get_trip_status()
    )

    while True:
        viewer_updator.show_next_stops()


if __name__ == "__main__":
    ft.app(target=main2)
