"""Offline copier sizing worksheet. No API key, network calls or trades.

This calculates requested lots, not the server's final broker-adjusted volume.
Use matching deposit currencies: raw fund ratios do not convert currencies.
"""
import argparse
from decimal import Decimal, InvalidOperation, localcontext
import json

MODES = ("FixedLot", "LotMultiplier", "BalanceMultiplier", "EquityMultiplier", "FixedBalanceMultiplier")


def positive(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Use positive finite decimal values") from exc
    if not result.is_finite() or not Decimal("0.00000001") <= result <= Decimal("100000000"):
        raise ValueError("Use finite values between 0.00000001 and 100000000")
    return result


def preview(mode, master_lots, risk_value, master_funds="10000", follower_funds="5000",
            master_contract="100000", follower_contract="100000", align_contracts=True,
            minimum="0.01", maximum="100", step="0.01"):
    if mode not in MODES:
        raise ValueError("Unknown sizing mode")
    lots, value, master, follower, source_contract, target_contract, low, high, increment = map(
        positive, (master_lots, risk_value, master_funds, follower_funds,
                   master_contract, follower_contract, minimum, maximum, step))
    if low > high:
        raise ValueError("Minimum volume cannot exceed maximum")
    with localcontext() as context:
        # Bound precision without changing the caller's decimal context.
        context.prec = 80
        ratio = source_contract / target_contract
        if mode == "FixedLot":
            requested = value
        elif mode == "LotMultiplier":
            requested = lots * value * (ratio if align_contracts else Decimal(1))
        else:
            # master_funds is balance, equity, or the fixed master balance.
            requested = lots * follower / master * value * ratio
        problems = []
        if requested < low: problems.append("below minimum")
        if requested > high: problems.append("above maximum")
        if requested % increment != 0: problems.append("not an exact volume-step multiple")
    return {"risk_type": mode, "risk_value": str(value), "requested_lots": format(requested, "f"),
            "volume_issues": problems,
            "note": "No broker rounding applied. Check actual logs, margin, contract and broker rules."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="LotMultiplier")
    parser.add_argument("--master-lots", default="0.10")
    parser.add_argument("--risk-value", default="0.5")
    parser.add_argument("--master-funds", default="10000",
                        help="Master balance/equity, or fixed master balance, for the selected mode")
    parser.add_argument("--follower-funds", default="5000")
    parser.add_argument("--master-contract", default="100000")
    parser.add_argument("--follower-contract", default="100000")
    parser.add_argument("--no-contract-alignment", action="store_true",
                        help="Disable optional contract alignment for LotMultiplier only")
    parser.add_argument("--minimum", default="0.01")
    parser.add_argument("--maximum", default="100")
    parser.add_argument("--step", default="0.01")
    args = vars(parser.parse_args())
    args["align_contracts"] = not args.pop("no_contract_alignment")
    try:
        print(json.dumps(preview(**args), indent=2))
    except ValueError as exc:
        parser.error(str(exc))
