"""
The starting point for the commandline version of the Bus Trip Announcer
Application
"""

from announcer import TripAnnouncer
from database import LocalDatabase
from io.location_specifier import CommandlineLocationUpdator
from models import RouteLocation
from stops_finder import NextStopsFinder
from io.viewer import CommandlineDisplay


def main() -> None:
    """
    Initialize the application and run the input-output loop in the command
    line.
    """
    database = LocalDatabase()
    stops_finder = NextStopsFinder(database)
    announcer = TripAnnouncer(stops_finder)
    updator = CommandlineLocationUpdator(announcer, RouteLocation())
    display = CommandlineDisplay(announcer)

    while True:
        updator.update_trip_announcer()
        display.show_next_stop_times()


if __name__ == "__main__":
    main()
