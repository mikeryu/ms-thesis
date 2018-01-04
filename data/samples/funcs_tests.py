import unittest
from funcs import *


class TestCases(unittest.TestCase):

    def test_poundsToKG_1(self):
        self.assertAlmostEqual(poundsToKG(0.0), 0.0)

    def test_poundsToKG_2(self):
        self.assertAlmostEqual(poundsToKG(1.0), 0.453592)

    def test_poundsToKG_3(self):
        self.assertAlmostEqual(poundsToKG(5.5), 2.494756)

    def test_poundsToKG_4(self):
        self.assertAlmostEqual(poundsToKG(120.0), 54.43104)

    def test_poundsToKG_5(self):
        self.assertAlmostEqual(poundsToKG(213.0), 96.615096)


    def test_getMassObject_1(self):
        # error case ... defaults to 0.0
        self.assertAlmostEqual(getMassObject('x'), 0.0)

    def test_getMassObject_2(self):
        # tomato
        self.assertAlmostEqual(getMassObject('t'), 0.1)

    def test_getMassObject_3(self):
        # banana cream pie
        self.assertAlmostEqual(getMassObject('p'), 1.0)

    def test_getMassObject_4(self):
        # rock
        self.assertAlmostEqual(getMassObject('r'), 3.0)

    def test_getMassObject_5(self):
        # lawn gnome
        self.assertAlmostEqual(getMassObject('g'), 5.3)

    def test_getMassObject_6(self):
        # light saber
        self.assertAlmostEqual(getMassObject('l'), 9.07)


    def test_getVelocityObject_1(self):
        # we may assume velocity of the skater is greater than or equal to zero
        self.assertAlmostEqual(getVelocityObject(0.0), 0.0)

    def test_getVelocityObject_2(self):
        self.assertAlmostEqual(getVelocityObject(0.5), 1.5652475842)

    def test_getVelocityObject_3(self):
        self.assertAlmostEqual(getVelocityObject(2.72), 3.6507533469)

    def test_getVelocityObject_4(self):
        self.assertAlmostEqual(getVelocityObject(11.11), 7.3782789321)


    def test_getVelocitySkater_1(self):
        self.assertAlmostEqual(getVelocitySkater(1.0, 3.0, 0.0), 0.0)

    def test_getVelocitySkater_2(self):
        self.assertAlmostEqual(getVelocitySkater(54.43104, 5.3, 7.3782789321), 0.7184297478)


    def test_determineMassMessage_1(self):
        self.assertEqual(determineMassMessage(0.05, 11.0), "You're going to get an F!")

    def test_determineMassMessage_2(self):
        self.assertEqual(determineMassMessage(0.1, 7.12), "You're going to get an F!")

    def test_determineMassMessage_3(self):
        self.assertEqual(determineMassMessage(0.11, 100.0), "Make sure your professor is OK.")

    def test_determineMassMessage_4(self):
        self.assertEqual(determineMassMessage(0.99, 20.0), "Make sure your professor is OK.")

    def test_determineMassMessage_5(self):
        self.assertEqual(determineMassMessage(1.0, 0.0), "Make sure your professor is OK.")

    def test_determineMassMessage_6(self):
        self.assertEqual(determineMassMessage(1.01, 19.99), "How far away is the hospital?")

    def test_determineMassMessage_7(self):
        self.assertEqual(determineMassMessage(1.01, 20.0), "RIP Professor.")

    def test_determineMassMessage_8(self):
        self.assertEqual(determineMassMessage(2.0, 30.0), "RIP Professor.")


    def test_determineVelocityMessage_1(self):
        self.assertEqual(determineVelocityMessage(0.05), "My grandmother skates faster than you!")

    def test_determineVelocityMessage_2(self):
        self.assertEqual(determineVelocityMessage(0.19), "My grandmother skates faster than you!")

    def test_determineVelocityMessage_3(self):
        self.assertEqual(determineVelocityMessage(0.2), None)

    def test_determineVelocityMessage_4(self):
        self.assertEqual(determineVelocityMessage(0.99), None)

    def test_determineVelocityMessage_5(self):
        self.assertEqual(determineVelocityMessage(1.0), "Look out for that railing!!!")

    def test_determineVelocityMessage_6(self):
        self.assertEqual(determineVelocityMessage(1.01), "Look out for that railing!!!")

    def test_determineVelocityMessage_7(self):
        self.assertEqual(determineVelocityMessage(2.0), "Look out for that railing!!!")


    def test_getSkaterVelocityValueMessage_1(self):
        self.assertEqual(getSkaterVelocityValueMessage(0.0), "Velocity of skater: 0.000 m/s")

    def test_getSkaterVelocityValueMessage_2(self):
        self.assertEqual(getSkaterVelocityValueMessage(3.019), "Velocity of skater: 3.019 m/s")

    def test_getSkaterVelocityValueMessage_3(self):
        self.assertEqual(getSkaterVelocityValueMessage(123.4567), "Velocity of skater: 123.457 m/s")


if __name__ == '__main__':
    unittest.main()
