"""
The starting point for the commandline version of the Bus Trip Announcer
Application
"""
from database import CSVDatabase, RouteFinder, DirectionFinder
from specifiers.location_specifier import CommandlineLocationUpdator
from viewer import CommandlineDisplay
from specifiers.trip_specifier import CommandLineTripSpecifier


def main() -> None:
    """
    Initialize the application and run the input-output loop in the command
    line.
    """
    database = CSVDatabase("useful_data")
    route_finder = RouteFinder(database)
    direction_finder = DirectionFinder(database)
    trip_specifier = CommandLineTripSpecifier(direction_finder, route_finder)
    trip_specifier.specify_all()
    announcer = trip_specifier.create_announcer()

    updator = CommandlineLocationUpdator(announcer, trip_specifier.trip_status)
    display = CommandlineDisplay(announcer)

    while True:
        display.show_next_stops()
        updator.update_trip_announcer()


if __name__ == "__main__":
    main()
