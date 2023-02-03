import pytest
import math
from utils import *

class TestCoordinates:

    def test_init_coordinates(self):
        coordinates = Coordinates(30, 122.3)
        assert coordinates.latitude == 30
        assert coordinates.longitude == 122.3

    def test_distance_between_zero(self):
        assert (Coordinates.distance_between(Coordinates(30, 122),
                                             Coordinates(30, 122))
                == 0)

    def test_distance_between_normal(self):
        assert (Coordinates.distance_between(Coordinates(1, 2),
                                             Coordinates(4, 6))
                == 5)

    def test_distance_between_float(self):
        assert math.isclose(
            Coordinates.distance_between(Coordinates(1.1, 2.2),
                                         Coordinates(3.6, 4.16)),
            3.176727876290319
        )