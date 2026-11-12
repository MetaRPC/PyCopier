# Position sizing and copy settings

Pass decimal sizing values as strings (`"0.01"`, `"1.5"`) wherever the model accepts them. Avoid introducing floating-point rounding into the request.

## Sizing policies

| `risk_type` | Base calculation before broker constraints |
|---|---|
| `FixedLot` | Follower lots = `risk_value` |
| `LotMultiplier` | Master lots × `risk_value`; contract-size alignment applies when enabled |
| `BalanceMultiplier` | Master lots × follower balance / master balance × `risk_value` × contract-size ratio |
| `EquityMultiplier` | Master lots × follower equity / master equity × `risk_value` × contract-size ratio |
| `FixedBalanceMultiplier` | Master lots × follower balance / `fixed_master_balance` × `risk_value` × contract-size ratio |

`fixed_master_balance` must be positive for FixedBalanceMultiplier. Contract-size ratio means master contract size / follower contract size. Final lots may be refined, rounded, limited or rejected by broker limits and copier settings.

A 0.10-lot source with LotMultiplier `"0.5"` has a base 0.05 lots before contract alignment or broker constraints. FixedLot `"0.01"` requests a base 0.01 lots regardless of source size.

## Run a worksheet without connecting accounts

The [standalone example](https://github.com/MetaRPC/PyCopier/blob/main/examples/sizing_preview.py) uses Python's standard library. No API key, SDK installation, terminals or orders are involved.

```bash
python examples/sizing_preview.py --mode LotMultiplier --master-lots 0.10 --risk-value 0.5
python examples/sizing_preview.py --mode BalanceMultiplier --master-lots 0.10 --risk-value 1 --master-funds 10000 --follower-funds 5000
python examples/sizing_preview.py --mode FixedLot --risk-value 0.005 --minimum 0.01 --step 0.01
```

The first two examples request 0.05 lots. The third keeps the requested 0.005 lots visible and flags the minimum and step violations; it does not increase exposure to make a trade pass. For EquityMultiplier, supply equity values. For FixedBalanceMultiplier, `--master-funds` is the configured fixed master balance. `--no-contract-alignment` affects LotMultiplier only. The defaults are illustrative, not broker specifications.

The worksheet checks positive finite inputs and basic volume constraints. It does not reproduce every server setting, perform currency conversion, check margin or guarantee execution. Confirm actual follower lots and logs after a demo trade. Run its offline checks with `python -m unittest discover -s tests -p test_sizing_preview.py`.

!!! warning "Different deposit currencies"
    The audited server compares raw balance/equity numbers; these ratios do not perform currency conversion. Do not describe them as equal monetary risk across currencies. Use matching deposit currencies for a simple verification and inspect actual lots.

## Copy switches

| Field | Meaning |
|---|---|
| `copy_sl` | Copy stop-loss changes, subject to broker constraints |
| `copy_tp` | Copy take-profit changes |
| `copy_pending_orders` | Include pending orders |
| `reverse_copy` | Reverse direction |

These switches do not guarantee broker acceptance. Symbols, digits, minimum stop distances, margin and sessions can affect execution. Compare the follower position with its log.

## Advanced settings and wrapper scope

The handwritten wrapper exposes Start, List, Pause and Remove. The current server also offers advanced settings and an Update RPC; this wrapper does not claim coverage of every service option. The bundled core proto is not an exhaustive copy of the latest server schema.

Review symbol mappings, limits, trading filters and equity protection in the control panel. Do not enable force-minimum-lot just to make a test pass: that can increase exposure.
