import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("sizing", Path(__file__).parents[1] / "examples/sizing_preview.py")
sizing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sizing)


class SizingPreviewTests(unittest.TestCase):
    def test_five_policies_with_hand_calculated_values(self):
        expected = {"FixedLot": ".5", "LotMultiplier": ".05", "BalanceMultiplier": ".025",
                    "EquityMultiplier": ".025", "FixedBalanceMultiplier": ".025"}
        for mode, lots in expected.items():
            result = sizing.preview(mode, ".1", ".5")
            self.assertEqual(sizing.Decimal(result["requested_lots"]), sizing.Decimal(lots))

    def test_contract_ratio_is_optional_only_for_lot_multiplier(self):
        options = dict(master_contract="100000", follower_contract="10000", align_contracts=False)
        self.assertEqual(sizing.Decimal(sizing.preview("LotMultiplier", ".1", ".5", **options)["requested_lots"]), sizing.Decimal(".05"))
        self.assertEqual(sizing.Decimal(sizing.preview("BalanceMultiplier", ".1", ".5", **options)["requested_lots"]), sizing.Decimal(".25"))

    def test_reports_constraints_without_changing_requested_lots(self):
        result = sizing.preview("FixedLot", ".1", ".005")
        self.assertEqual(result["requested_lots"], "0.005")
        self.assertEqual(result["volume_issues"], ["below minimum", "not an exact volume-step multiple"])
        self.assertIn("above maximum", sizing.preview("FixedLot", ".1", "101")["volume_issues"])

    def test_decimal_step_does_not_use_binary_float(self):
        self.assertEqual(sizing.preview("LotMultiplier", ".1", ".3")["volume_issues"], [])

    def test_invalid_values_and_limits_are_rejected(self):
        for invalid in ("0", "-1", "NaN", "Infinity", "abc", "100000001"):
            with self.assertRaises(ValueError): sizing.preview("BalanceMultiplier", ".1", "1", master_funds=invalid)
        with self.assertRaises(ValueError): sizing.preview("FixedLot", ".1", "1", minimum="2", maximum="1")
        with self.assertRaises(ValueError): sizing.preview("Unknown", ".1", "1")
