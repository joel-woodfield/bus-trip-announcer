"""
The starting point for the commandline version of the Bus Trip Announcer
Application
"""
import flet as ft

from bus_trip_announcer.gui.trip_specifier import GUITripSpecifier
from bus_trip_announcer.gui.viewer_updator import GUITripViewerAndUpdator
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
    trip_specifier = GUITripSpecifier(direction_finder, trip_finder, page)
    trip_specifier.specify_all()
    announcer = trip_specifier.create_announcer()

    viewer_updator = GUITripViewerAndUpdator(
        announcer, page, trip_specifier.trip_status
    )

    while True:
        viewer_updator.show_next_stops()


if __name__ == "__main__":
    ft.app(target=main2)
