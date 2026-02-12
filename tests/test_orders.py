import unittest
import importlib

try:
    orders = importlib.import_module('orders')
    order = orders.order
    multi_orders = orders.multi_orders
    import_error = None
except ModuleNotFoundError as exc:
    orders = None
    import_error = exc

class TestOrder(unittest.TestCase):
    def setUp(self):
        if orders is None:
            self.skipTest(f'orders module not available: {import_error}')

    def test_create_order(self):
        o = order('2023-01-01T12:00:00+0000', 'buy', 10.0, 2.0)
        self.assertEqual(o.type_string, 'buy')
        self.assertAlmostEqual(o.price_float, 10.0)
        self.assertAlmostEqual(o.amount_float, 2.0)
        self.assertAlmostEqual(o.value_float, 20.0)
        self.assertEqual(o.date_dt.year, 2023)

    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            order('2023-01-01T12:00:00+0000', 'hold', 10.0, 2.0)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            order('2023-01-01T12:00:00+0000', 'buy', -1.0, 2.0)

    def test_negative_amount(self):
        with self.assertRaises(ValueError):
            order('2023-01-01T12:00:00+0000', 'buy', 10.0, -1.0)

class TestMultiOrders(unittest.TestCase):
    def setUp(self):
        if orders is None:
            self.skipTest(f'orders module not available: {import_error}')
        self.mo = multi_orders('ABC')
        self.mo.add_order(order('2023-01-01T12:00:00+0000', 'buy', 5.0, 1))
        self.mo.add_order(order('2023-01-02T12:00:00+0000', 'sell', 10.0, 1))

    def test_latest_value(self):
        self.mo.sort_by_time_increasing()
        self.assertAlmostEqual(self.mo.latest_value(), 5.0)

    def test_latest_profit(self):
        self.mo.sort_by_time_increasing()
        self.mo.update_current(0, 0)
        self.assertAlmostEqual(self.mo.latest_profit(), 5.0)

if __name__ == '__main__':
    unittest.main()
