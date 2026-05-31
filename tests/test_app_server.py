import importlib.util
import pathlib
import unittest
from decimal import Decimal


ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "app" / "server.py"
SPEC = importlib.util.spec_from_file_location("arb_app_server", SERVER_PATH)
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


class AppEngineTests(unittest.TestCase):
    def test_partial_buy_exact_base_recomputes_spend(self):
        asks = [
            [Decimal("100"), Decimal("0.5")],
            [Decimal("110"), Decimal("1.0")],
        ]

        base, spent, vwap, full = server.walk_buy_base(asks, Decimal("0.75"))

        self.assertTrue(full)
        self.assertEqual(base, Decimal("0.75"))
        self.assertEqual(spent, Decimal("77.50"))
        self.assertEqual(vwap, Decimal("103.333333333333333333333333333"))

    def test_config_rejects_absurd_values_without_mutating(self):
        original = server.CONFIG["latency_bps"]

        errors = server._apply_config({"latency_bps": -1})

        self.assertTrue(errors)
        self.assertEqual(server.CONFIG["latency_bps"], original)

    def test_config_accepts_bounded_rebalance_cost(self):
        original = server.CONFIG["rebalance_bps"]

        errors = server._apply_config({"rebalance_bps": 3})

        self.assertEqual(errors, [])
        self.assertEqual(server.CONFIG["rebalance_bps"], Decimal("3"))
        server.CONFIG["rebalance_bps"] = original


if __name__ == "__main__":
    unittest.main()
