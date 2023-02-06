from stops_finder import *
from database import LocalDatabase


class TestNextStopsFinder:
    # get_next_stops tests also tests for _get_next_stop_index
    def test_get_next_stops_empty(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database1.csv")
        stops_finder = NextStopsFinder(database)
        user = User(12345, Direction.NORTH, Coordinates(45.6, 123.4))
        stops = stops_finder.get_next_stops(user)
        assert stops == []

    def test_get_next_stops_full(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database1.csv")
        stops_finder = NextStopsFinder(database)
        user = User(200, Direction.NORTH, Coordinates(45.6, 123.4))
        stops = stops_finder.get_next_stops(user)
        assert stops == [
            Stop(
                "Brisbane Street",
                Coordinates(45.6, 123.4),
                datetime.timedelta(minutes=0),
            ),
            Stop(
                "Marble Mountains",
                Coordinates(45.8, 124.0),
                datetime.timedelta(minutes=10),
            ),
            Stop(
                "World's Best Banh Mi Shop",
                Coordinates(46.3, 123.4),
                datetime.timedelta(minutes=20),
            ),
        ]

    def test_get_next_stops_at_stop(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database1.csv")
        stops_finder = NextStopsFinder(database)
        user = User(200, Direction.NORTH, Coordinates(45.8, 124.0))
        stops = stops_finder.get_next_stops(user)
        assert stops == [
            Stop(
                "Marble Mountains",
                Coordinates(45.8, 124.0),
                datetime.timedelta(minutes=0),
            ),
            Stop(
                "World's Best Banh Mi Shop",
                Coordinates(46.3, 123.4),
                datetime.timedelta(minutes=10),
            ),
        ]

    def test_get_next_stops_between_stops(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database1.csv")
        stops_finder = NextStopsFinder(database)
        user = User(200, Direction.NORTH, Coordinates(45.7, 123.4))
        stops = stops_finder.get_next_stops(user)
        assert stops == [
            Stop(
                "Marble Mountains",
                Coordinates(45.8, 124.0),
                # half-way between the first and second stops
                # so take away 10/2 = 5 minutes
                datetime.timedelta(minutes=5),
            ),
            Stop(
                "World's Best Banh Mi Shop",
                Coordinates(46.3, 123.4),
                datetime.timedelta(minutes=15),
            ),
        ]

    def test_get_next_stops_past_end(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database1.csv")
        stops_finder = NextStopsFinder(database)
        user = User(200, Direction.NORTH, Coordinates(46.4, 123.4))
        stops = stops_finder.get_next_stops(user)
        assert stops == []

    def test_get_next_stops_direction_north(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database_direction.csv")
        stops_finder = NextStopsFinder(database)
        user = User(100, Direction.NORTH, Coordinates(45.6, 123.4))
        stops = stops_finder.get_next_stops(user)
        assert stops == [
            Stop(
                "Stop A",
                Coordinates(45.6, 123.4),
                datetime.timedelta(minutes=0),
            ),
            Stop(
                "Stop B",
                Coordinates(45.8, 123.5),
                datetime.timedelta(minutes=5),
            ),
        ]

    def test_get_next_stops_direction_south(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database_direction.csv")
        stops_finder = NextStopsFinder(database)
        user = User(100, Direction.SOUTH, Coordinates(45.8, 123.5))
        stops = stops_finder.get_next_stops(user)
        assert stops == [
            Stop(
                "Stop B",
                Coordinates(45.8, 123.5),
                datetime.timedelta(minutes=0),
            ),
            Stop(
                "Stop A",
                Coordinates(45.6, 123.4),
                datetime.timedelta(minutes=5),
            ),
        ]

    def test_get_next_stops_direction_east(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database_direction.csv")
        stops_finder = NextStopsFinder(database)
        user = User(200, Direction.EAST, Coordinates(45.6, 123.4))
        stops = stops_finder.get_next_stops(user)
        assert stops == [
            Stop(
                "Stop A",
                Coordinates(45.6, 123.4),
                datetime.timedelta(minutes=0),
            ),
            Stop(
                "Stop C",
                Coordinates(45.5, 124.0),
                datetime.timedelta(minutes=5),
            ),
        ]

    def test_get_next_stops_direction_west(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database_direction.csv")
        stops_finder = NextStopsFinder(database)
        user = User(200, Direction.WEST, Coordinates(45.5, 124.0))
        stops = stops_finder.get_next_stops(user)
        assert stops == [
            Stop(
                "Stop C",
                Coordinates(45.5, 124.0),
                datetime.timedelta(minutes=0),
            ),
            Stop(
                "Stop A",
                Coordinates(45.6, 123.4),
                datetime.timedelta(minutes=5),
            ),
        ]


