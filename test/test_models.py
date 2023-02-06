from models import *
import datetime
from utils import Coordinates


class TestUser:
    def test_eq_different_class(self):
        user = User()
        stop = Stop("hi", Coordinates(-1, 0), datetime.timedelta(minutes=1))
        assert user != stop

    def test_eq_true(self):
        user1 = User(100, Direction.EAST, Coordinates(1, 2))
        user2 = User(100, Direction.EAST, Coordinates(1, 2))
        assert user1 == user2

    def test_eq_false_route(self):
        user1 = User(100, Direction.EAST, Coordinates(1, 2))
        user2 = User(200, Direction.EAST, Coordinates(1, 2))
        assert user1 != user2

    def test_eq_false_direction(self):
        user1 = User(100, Direction.EAST, Coordinates(1, 2))
        user2 = User(100, Direction.WEST, Coordinates(1, 2))
        assert user1 != user2

    def test_eq_false_coordinates(self):
        user1 = User(100, Direction.EAST, Coordinates(1, 2))
        user2 = User(100, Direction.EAST, Coordinates(1, 3))
        assert user1 != user2


class TestStop:
    def test_is_after_same(self):
        assert Stop("name", Coordinates(1, 3), datetime.timedelta()).is_after(
            User(100, Direction.NORTH, Coordinates(1, 2))
        )
        assert Stop("name", Coordinates(1, 3), datetime.timedelta()).is_after(
            User(100, Direction.SOUTH, Coordinates(1, 2))
        )
        assert Stop("name", Coordinates(3, 2), datetime.timedelta()).is_after(
            User(100, Direction.EAST, Coordinates(1, 2))
        )
        assert Stop("name", Coordinates(3, 2), datetime.timedelta()).is_after(
            User(100, Direction.WEST, Coordinates(1, 2))
        )

    def test_is_after_true(self):
        assert Stop("name", Coordinates(2, 3), datetime.timedelta()).is_after(
            User(100, Direction.NORTH, Coordinates(1, 2))
        )
        assert Stop("name", Coordinates(0, 3), datetime.timedelta()).is_after(
            User(100, Direction.SOUTH, Coordinates(1, 2))
        )
        assert Stop("name", Coordinates(3, 3), datetime.timedelta()).is_after(
            User(100, Direction.EAST, Coordinates(1, 2))
        )
        assert Stop("name", Coordinates(3, 1), datetime.timedelta()).is_after(
            User(100, Direction.WEST, Coordinates(1, 2))
        )

    def test_is_after_false(self):
        assert not (
            Stop("name", Coordinates(0, 3), datetime.timedelta()).is_after(
                User(100, Direction.NORTH, Coordinates(1, 2))
            )
        )
        assert not (
            Stop("name", Coordinates(2, 3), datetime.timedelta()).is_after(
                User(100, Direction.SOUTH, Coordinates(1, 2))
            )
        )
        assert not (
            Stop("name", Coordinates(3, 1), datetime.timedelta()).is_after(
                User(100, Direction.EAST, Coordinates(1, 2))
            )
        )
        assert not (
            Stop("name", Coordinates(3, 3), datetime.timedelta()).is_after(
                User(100, Direction.WEST, Coordinates(1, 2))
            )
        )

    def test_eq_same(self):
        assert Stop(
            "name", Coordinates(0, 0), datetime.timedelta(minutes=1)
        ) == Stop("name", Coordinates(0, 0), datetime.timedelta(minutes=1))

    def test_eq_name(self):
        assert not (
            Stop("name", Coordinates(0, 0), datetime.timedelta(minutes=1))
            == Stop("other", Coordinates(0, 0), datetime.timedelta(minutes=1))
        )

    def test_eq_coordinates(self):
        assert not (
            Stop("name", Coordinates(0, 0), datetime.timedelta(minutes=1))
            == Stop("name", Coordinates(1, 0), datetime.timedelta(minutes=1))
        )

    def test_eq_time_until_stop(self):
        assert not (
            Stop("name", Coordinates(0, 0), datetime.timedelta(minutes=1))
            == Stop("name", Coordinates(0, 0), datetime.timedelta(minutes=2))
        )


class TestRoute:
    def test_eq_same(self):
        assert Route(
            100,
            Direction.NORTH,
            [Stop("name", Coordinates(0, 0), datetime.timedelta())],
        ) == Route(
            100,
            Direction.NORTH,
            [Stop("name", Coordinates(0, 0), datetime.timedelta())],
        )

    def test_eq_number(self):
        assert Route(100, Direction.NORTH, []) != Route(
            200, Direction.NORTH, []
        )

    def test_eq_coordinates(self):
        assert Route(100, Direction.SOUTH, []) != Route(
            100, Direction.EAST, []
        )

    def test_eq_stops(self):
        assert Route(
            100,
            Direction.NORTH,
            [Stop("name", Coordinates(0, 0), datetime.timedelta(minutes=2))],
        ) != Route(
            100,
            Direction.NORTH,
            [Stop("name2", Coordinates(1, 1), datetime.timedelta(minutes=1))],
        )
