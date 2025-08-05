import unittest
from minipot import booster  # ajusta si el import es distinto

class TestBooster(unittest.TestCase):
    def test_basic_addition(self):
        self.assertEqual(booster.add(2, 2), 4)

    def test_negative_numbers(self):
        self.assertEqual(booster.add(-2, -3), -5)

    def test_boost_value(self):
        result = booster.boost(10, 2)
        self.assertEqual(result, 20)

    def test_boost_zero(self):
        self.assertEqual(booster.boost(0, 100), 0)

    def test_division_ok(self):
        self.assertAlmostEqual(booster.divide(10, 2), 5.0)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            booster.divide(10, 0)

    def test_booster_init(self):
        obj = booster.Booster()
        self.assertTrue(hasattr(obj, "power"))

    def test_booster_set_power(self):
        obj = booster.Booster()
        obj.set_power(99)
        self.assertEqual(obj.power, 99)

    def test_str(self):
        obj = booster.Booster()
        self.assertIn("Booster", str(obj))

    def test_repr(self):
        obj = booster.Booster()
        self.assertIn("Booster", repr(obj))

    def test_increase_power(self):
        obj = booster.Booster()
        current = obj.power
        obj.increase()
        self.assertEqual(obj.power, current + 1)

    def test_decrease_power(self):
        obj = booster.Booster()
        current = obj.power
        obj.decrease()
        self.assertEqual(obj.power, current - 1)

    def test_reset_power(self):
        obj = booster.Booster()
        obj.set_power(10)
        obj.reset()
        self.assertEqual(obj.power, 0)

    def test_custom_boost_formula(self):
        self.assertEqual(booster.custom_boost(5, 3), 8)  # ajusta según lógica real
