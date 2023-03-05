"""
The starting point for the commandline version of the Bus Trip Announcer
Application
"""
import flet as ft

from bus_trip_announcer.announcer import TripAnnouncer
from bus_trip_announcer.inputs import TripInput, FletInputDevice, LocationInput
from bus_trip_announcer.models import TripStatus
from bus_trip_announcer.stops_finder import NextStopsFinder
from database.database import CSVDatabase
from database.finders import DirectionFinder, TripFinder
from bus_trip_announcer.viewers import CommandLineTripViewer, FletTripViewer


#
# def main() -> None:
#     """
#     Initialize the application and run the input-output loop in the command
#     line.
#     """
#     database = CSVDatabase("useful_data")
#     trip_finder = TripFinder(database)
#     direction_finder = DirectionFinder(database)
#     trip_specifier = CommandLineTripSpecifier(direction_finder, trip_finder)
#     trip_specifier.specify_all()
#     announcer = trip_specifier.create_announcer()
#
#     updator = CommandlineLocationSpecifier(
#         announcer, trip_specifier.trip_status
#     )
#     display = CommandlineDisplay(announcer)
#
#     while True:
#         display.show_next_stops()
#         updator.update_trip_announcer()


def main2(page: ft.Page) -> None:
    """
    Initialize the GUI application
    """
    page.window_width = 500
    page.window_height = 700

    database = CSVDatabase("useful_data")
    trip_finder = TripFinder(database)
    direction_finder = DirectionFinder(database)

    trip_status = TripStatus()
    announcer = TripAnnouncer(trip_status)
    input_device = FletInputDevice(direction_finder, announcer, page)
    trip_input = TripInput(input_device)

    trip_input.input_all()
    time = trip_input.get_time()
    trip = trip_finder.get_trip(
        trip_status.route_number,
        trip_status.direction,
        trip_status.coordinates,
        time,
    )

    announcer.next_stops_finder = NextStopsFinder(trip)
    announcer.update_next_stops()

    viewer = FletTripViewer(announcer, page)
    location_input = LocationInput(input_device)
    location_input.update_coordinates()

    while True:
        viewer.show_next_stops()


if __name__ == "__main__":
    ft.app(target=main2)
