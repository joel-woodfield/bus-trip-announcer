import math

from bus_trip_announcer.utils import Coordinates


class TestCoordinates:
    def test_init_coordinates(self):
        coordinates = Coordinates(30, 122.3)
        assert coordinates.latitude == 30
        assert coordinates.longitude == 122.3

    def test_distance_between_identical_coordinates(self):
        """
        Test that Coordinates.distance_between returns 0 for identical
        coordinates
        """
        coordinates1 = Coordinates(30, 122)
        coordinates2 = Coordinates(30, 122)
        distance = Coordinates.distance_between(coordinates1, coordinates2)
        assert distance == 0

    def test_distance_between_where_distance_is_positive(self):
        assert (
            Coordinates.distance_between(Coordinates(1, 2), Coordinates(4, 6))
            == 5
        )

    def test_distance_between_coordinates_when_values_are_floats(self):
        coordinates1 = Coordinates(1.1, 2.2)
        coordinates2 = Coordinates(3.6, 4.16)
        distance = Coordinates.distance_between(coordinates1, coordinates2)
        assert math.isclose(distance, 3.176727876290319)

    def test_latitude_displacement_between_where_result_is_zero(self):
        assert (
            Coordinates.latitude_displacement_between(
                Coordinates(30, 122), Coordinates(30, 555)
            )
            == 0
        )

    def test_latitude_displacement_between_where_result_is_positive(self):
        assert (
            Coordinates.latitude_displacement_between(
                Coordinates(1, 2), Coordinates(4, 6)
            )
            == 3
        )

    def test_latitude_displacement_between_where_result_is_negative(self):
        assert (
            Coordinates.latitude_displacement_between(
                Coordinates(4, 6), Coordinates(1, 2)
            )
            == -3
        )

    def test_latitude_displacement_between_where_coordinates_are_floats(self):
        assert math.isclose(
            Coordinates.latitude_displacement_between(
                Coordinates(1.1, 2.2), Coordinates(3.6, 4.16)
            ),
            2.5,
        )

    def test_longitude_displacement_between_where_result_is_zero(self):
        assert (
            Coordinates.longitude_displacement_between(
                Coordinates(30, 122), Coordinates(45, 122)
            )
            == 0
        )

    def test_longitude_displacement_between_where_result_is_positive(self):
        assert (
            Coordinates.longitude_displacement_between(
                Coordinates(1, 2), Coordinates(4, 6)
            )
            == 4
        )

    def test_longitude_displacement_between_where_coordinates_are_floats(self):
        assert math.isclose(
            Coordinates.longitude_displacement_between(
                Coordinates(1.1, 2.2), Coordinates(3.6, 4.16)
            ),
            1.96,
        )

    def test_longitude_displacement_between_where_result_is_negative(self):
        assert (
            Coordinates.longitude_displacement_between(
                Coordinates(4, 6), Coordinates(1, 2)
            )
        ) == -4
