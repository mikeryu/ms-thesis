import unittest
from funcs import *


class TestCases(unittest.TestCase):

    def test_updateAcceleration_1(self):
        # constant velocity on the moon
        self.assertAlmostEqual(updateAcceleration(1.62, 5), 0.0)

    def test_updateAcceleration_2(self):
        # free fall on the moon
        self.assertAlmostEqual(updateAcceleration(1.62, 0), -1.62)

    def test_updateAcceleration_3(self):
        # max thrust on the moon
        self.assertAlmostEqual(updateAcceleration(1.62, 9), 1.296)

    def test_updateAcceleration_4(self):
        # strong thrust on the Earth
        self.assertAlmostEqual(updateAcceleration(9.82, 7), 3.928)


    def test_updateAltitude_1(self):
        self.assertAlmostEqual(updateAltitude(500.0, -30.3, 1.62), 470.51)

    def test_updateAltitude_2(self):
        self.assertAlmostEqual(updateAltitude(123.5, -11.3, 5.2), 114.8)

    def test_updateAltitude_3(self):
        # altitude must not be negative
        self.assertAlmostEqual(updateAltitude(0.0, -11.3, 5.2), 0.0)


    def test_updateVelocity_1(self):
        self.assertAlmostEqual(updateVelocity(11.0, -1.62), 9.38)

    def test_updateVelocity_2(self):
        self.assertAlmostEqual(updateVelocity(0.32, -3.24), -2.92)

    def test_updateVelocity_3(self):
        self.assertAlmostEqual(updateVelocity(-9.82, 9.82), 0.0)


    def test_updateFuel_1(self):
        self.assertEqual(updateFuel(500, 9), 491)

    def test_updateFuel_2(self):
        self.assertEqual(updateFuel(12, 10), 2)

    def test_updateFuel_3(self):
        self.assertEqual(updateFuel(3, 3), 0)


if __name__ == '__main__':
    unittest.main()
