from database import LocalDatabase
from models import Stop, Route
from utils import Direction, Coordinates
import datetime


class TestLocalDatabase:
    def test_empty_database(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database_empty.csv")
        route = database.get_route(100, Direction.NORTH)
        assert route == Route(100, Direction.NORTH, [])

    def test_normal_database(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database1.csv")
        route = database.get_route(100, Direction.NORTH)
        assert route == Route(
            100,
            Direction.NORTH,
            [
                Stop(
                    "Brisbane Street",
                    Coordinates(45.6, 123.4),
                    datetime.timedelta(minutes=0),
                ),
                Stop(
                    "Gold Coast Avenue",
                    Coordinates(45.7, 123.5),
                    datetime.timedelta(minutes=2),
                ),
                Stop(
                    "Da Nang Centre",
                    Coordinates(45.8, 123.5),
                    datetime.timedelta(minutes=5),
                ),
                Stop(
                    "Hoi An Mall",
                    Coordinates(45.9, 123.5),
                    datetime.timedelta(minutes=15),
                ),
                Stop(
                    "University of Queensland",
                    Coordinates(46.0, 123.5),
                    datetime.timedelta(minutes=20),
                ),
                Stop(
                    "CMC Global Office",
                    Coordinates(46.2, 123.4),
                    datetime.timedelta(minutes=25),
                ),
                Stop(
                    "World's Best Banh Mi Shop",
                    Coordinates(46.3, 123.4),
                    datetime.timedelta(minutes=35),
                ),
            ],
        )

    def test_database_route_not_exist(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database1.csv")
        route = database.get_route(12345, Direction.NORTH)
        assert route == Route(
            12345,
            Direction.NORTH,
            [],
        )

    def test_database_direction_not_exist(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database1.csv")
        route = database.get_route(100, Direction.EAST)
        assert route == Route(
            100,
            Direction.EAST,
            [],
        )

    def test_database_wrong_order(self):
        database = LocalDatabase()
        database.set_database_file("../data/test_database_bad_order.csv")
        route = database.get_route(200, Direction.EAST)
        assert route == Route(
            200,
            Direction.EAST,
            [
                Stop(
                    "A street",
                    Coordinates(45.4, 123.2),
                    datetime.timedelta(minutes=0),
                ),
                Stop(
                    "B street",
                    Coordinates(45.4, 123.4),
                    datetime.timedelta(minutes=5),
                ),
                Stop(
                    "C street",
                    Coordinates(45.3, 123.6),
                    datetime.timedelta(minutes=10),
                ),
            ],
        )
