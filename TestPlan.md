# **Test Plan: Reduce Margin Ratio (RMR)**

## Objective

Verify that:

- A new perpetual market can be created with a `reduce-margin-ratio` (RMR) value.
- An existing perpetual market’s `reduce-margin-ratio` value can be updated.
- The values are correctly stored and retrievable via CLI query commands.
- Constraints on RMR (`RMR ≥ IMR > MMR`) are respected and validated.
- What are the possible min and max values of RMR and test boundary values around them. Hint: https://github.com/Kishan-Dhakan/calculator-app/blob/master/injective-chain/modules/exchange/types/params.go#L429-L446 Valid range: [0.005, 1.0)
- RMR input values are validated correctly (as high precision decimal values) within their lower and upper bounds

---

## Test Setup

### Pre-requisites

- `injectived` binary available in `$PATH`
- Local Injective chain running (`rm -rf .injectived && ./setup.sh && ./injectived.sh`)
- Wallets:
  - `testcandidate` (user)
  - `val` (validator)
- Chain ID: `injective-1`
- Passphrase for wallets: `12345678`

---

## Test Cases

### Market Creation

New market can be created using provided script `setup_tst_usdt_perp.sh` which should be executed on the top of the locally running injective chain.
All tests in this group may basically follow steps as below:

0. Start injective local chain: `rm -rf .injectived && ./setup.sh && ./injectived.sh`
1. Create new perpetual market using modified `setup_tst_usdt_perp.sh` from this repo, like `./setup_tst_usdt_perp.sh rmr_value imr_value mmr_value` e.g. `./setup_tst_usdt_perp.sh 0.06 0.05 0.01`
2. Verify market is created and the RMR / IMR / MMR values are set as expected, e.g.

```
$ injectived q exchange derivative-markets --chain-id injective-1 -o json \
| jq '.markets[] | select(.market.ticker == "TST/USDT PERP")
| {reduce_margin_ratio: .market.reduce_margin_ratio,
   initial_margin_ratio: .market.initial_margin_ratio,
   maintenance_margin_ratio: .market.maintenance_margin_ratio}'
```

3. In case market is not created (for some cases it is expected), look up transaction for `Submitting proposal to launch TST/USDT PERP market` by its `txhash`. Look at transaction code and raw_log for potential failure reason e.g.

```
$ injectived q tx AD665B0B09FE8E523DDE820E831978D6167637E7DFFA0976D613A501E43CBD13 \
--chain-id injective-1 -o json | jq
```

| TC ID | Description                              | RMR / IMR / MMR       | Expected | Actual   | Result | Notes                                                                                                                                                                                                                            | Bug ticket                                         |
| ----- | ---------------------------------------- | --------------------- | -------- | -------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| MC-01 | Create market with valid RMR > IMR > MMR | 0.06 / 0.05 / 0.01    | Created  | Created  | ✅     |                                                                                                                                                                                                                                  |                                                    |
| MC-02 | Create market with RMR = IMR             | 0.05 / 0.05 / 0.01    | Created  | Created  | ✅     |                                                                                                                                                                                                                                  |                                                    |
| MC-03 | RMR == IMR == MMR                        | 0.05 / 0.05 / 0.05    | Rejected | Created  | :x:    | Constraint violated `RMR ≥ IMR > MMR`                                                                                                                                                                                            | 🐛[#1](https://github.com/piotr-iohk/rmr/issues/1) |
| MC-04 | RMR == IMR < MMR                         | 0.05 / 0.05 / 0.06    | Rejected | Rejected | 🟡     | Proposal rejected, tx failed: `failed to execute message; message index: 0: Ensure that MaintenanceMarginRatio < InitialMarginRatio <= ReduceMarginRatio: invalid proposal message`                                              | 🐛[#2](https://github.com/piotr-iohk/rmr/issues/2) |
| MC-05 | RMR < IMR > MMR                          | 0.02 / 0.05 / 0.01    | Rejected | Rejected | 🟡     | Proposal rejected, tx failed: `failed to execute message; message index: 0: Ensure that MaintenanceMarginRatio < InitialMarginRatio <= ReduceMarginRatio: invalid proposal message`                                              | 🐛[#2](https://github.com/piotr-iohk/rmr/issues/2) |
| MC-06 | RMR = 0 < IMR                            | 0.0 / 0.05 / 0.01     | Rejected | Rejected | 🟡     | Proposal rejected, tx failed: `failed to execute message; message index: 0: margin ratio cannot be less than minimum: 0.000000000000000000: invalid proposal message`, Minimum is not specified in the error msg, nor documented | 🐛[#2](https://github.com/piotr-iohk/rmr/issues/2) |
| MC-07 | max RMR = 1.0                            | 1.0 / 0.1 / 0.05      | Rejected | Rejected | 🟡     | Proposal rejected, tx failed: `failed to execute message; message index: 0: margin ratio cannot be greater than or equal to 1: 1.000000000000000000: invalid proposal message`                                                   | 🐛[#2](https://github.com/piotr-iohk/rmr/issues/2) |
| MC-08 | over limits RMR = 100                    | 100 / 0.1 / 0.05      | Rejected | Rejected | 🟡     | Proposal rejected, tx failed: `failed to execute message; message index: 0: margin ratio cannot be greater than or equal to 1: 100.000000000000000000: invalid proposal message`                                                 | 🐛[#2](https://github.com/piotr-iohk/rmr/issues/2) |
| MC-09 | min possible RMR                         | 0.006 / 0.006 / 0.005 | Created  | Created  | ✅     |                                                                                                                                                                                                                                  |                                                    |
| MC-10 | min RMR, but RMR == IMR == MMR           | 0.005 / 0.005 / 0.005 | Rejected | Created  | :x:    | Constraint violated `RMR ≥ IMR > MMR`                                                                                                                                                                                            | 🐛[#1](https://github.com/piotr-iohk/rmr/issues/1) |
| MC-11 | RMR non-decimal (e.g. "abc")             | "abc" / 0.1 / 0.05    | Rejected | Rejected | ✅     | `could not parse abc as math.LegacyDec for field ReduceMarginRatio: failed to set decimal string with base 10: abc000000000000000000` , rejected before sending                                                                  |                                                    |
| MC-12 | Missing RMR field                        | – / 0.1 / 0.05        | Rejected | Rejected | 🟡     | Proposal rejected, tx failed: `"failed to execute message; message index: 0: margin ratio cannot be less than minimum: 0.000000000000000000: invalid proposal message`                                                           | 🐛[#2](https://github.com/piotr-iohk/rmr/issues/2) |
| MC-13 | MRs below 0                              | -0.06 / -0.05 / -0.01 | Rejected | Rejected | 🟡     | Proposal rejected, tx failed: `"failed to execute message; message index: 0: margin ratio cannot be less than minimum: -0.050000000000000000: invalid proposal message`                                                          | 🐛[#2](https://github.com/piotr-iohk/rmr/issues/2) |

---

### Market Update

#### Prerequisites

1. Start injective local chain: `rm -rf .injectived && ./setup.sh && ./injectived.sh`
2. Create new perpetual market using modified e.g. `./setup_tst_usdt_perp.sh 0.06 0.05 0.01`
3. Look up newly created market id:

```
$ injectived q exchange derivative-markets --chain-id injective-1 -o json \
| jq '.markets[] | select(.market.ticker == "TST/USDT PERP")
| {market_id: .market.market_id}'

{
  "market_id": "0x8fde97d09cbdf47ad5ee9d076d0be329c30af3357946e038ef9f6d14a083f692"
}
```

All tests in this group may basically follow steps as below: 0. Look up previously created market:

```
$ injectived q exchange derivative-markets --chain-id injective-1 -o json \
| jq '.markets[] | select(.market.ticker == "TST/USDT PERP")
| { market_id: .market.market_id,
   reduce_margin_ratio: .market.reduce_margin_ratio,
   initial_margin_ratio: .market.initial_margin_ratio,
   maintenance_margin_ratio: .market.maintenance_margin_ratio}'
```

1. Update perpetual market RMR:

```
# <market_id> - replace with market_id value
# <account> - replace with testcandidate (in case of admin account) or val (in case of non-admin account)
# <rmr_value> - replace with new rmr value
$ yes 12345678 | injectived tx exchange update-derivative-market <market_id> \
  --reduce-margin-ratio <rmr_value> \
  --from <account> \
  --chain-id injective-1 \
  --gas-prices 500000000inj \
  --gas 10000000 \
  --yes
```

2. Check if market has been updated:

```
$ injectived q exchange derivative-markets --chain-id injective-1 -o json \
| jq '.markets[] | select(.market.ticker == "TST/USDT PERP")
| { market_id: .market.market_id,
   reduce_margin_ratio: .market.reduce_margin_ratio,
   initial_margin_ratio: .market.initial_margin_ratio,
   maintenance_margin_ratio: .market.maintenance_margin_ratio}'
```

3. In case market is not updated (for some cases it is expected), look up update transaction. Look at transaction code and raw_log for potential failure reason e.g.

```
$ injectived q tx AD665B0B09FE8E523DDE820E831978D6167637E7DFFA0976D613A501E43CBD13 \
--chain-id injective-1 -o json | jq
```

| TC ID | Description                                                             | RMR / IMR / MMR (old → new)                              | Expected | Actual   | Result | Notes                                                                                                                                                               | Bug ticket                                         |
| ----- | ----------------------------------------------------------------------- | -------------------------------------------------------- | -------- | -------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| MU-01 | Update RMR to bigger valid value                                        | 0.06 / 0.05 / 0.01 → 0.07 / 0.05 / 0.01                  | Updated  | Rejected | :x:    | Tx failed: `failed to execute message; message index: 0: Invalid margin ratio` new constraint discovered: `RMR >= default_reduce_margin_ratio`                      | 🐛[#3](https://github.com/piotr-iohk/rmr/issues/3) |
| MU-02 | Update RMR to smaller valid value                                       | 0.07 / 0.05 / 0.01 → 0.06 / 0.05 / 0.01                  | Updated  | Rejected | :x:    | Tx failed: `failed to execute message; message index: 0: Invalid margin ratio` new constraint discovered: `RMR >= default_reduce_margin_ratio`                      | 🐛[#3](https://github.com/piotr-iohk/rmr/issues/3) |
| MU-03 | Update RMR to 1.0                                                       | 0.06 / 0.05 / 0.01 → 1.00 / 0.05 / 0.01                  | Rejected | Rejected | ✅     | validation: `margin ratio cannot be greater than or equal to 1: 1.000000000000000000`                                                                               |                                                    |
| MU-04 | Update RMR == IMR                                                       | 0.099 / 0.09 / 0.01 → 0.09 / 0.09 / 0.01                 | Updated  | Updated  | ✅     |                                                                                                                                                                     |                                                    |
| MU-05 | Update RMR > IMR                                                        | 0.09 / 0.09 / 0.01 → 0.5 / 0.09 / 0.01                   | Updated  | Updated  | ✅     |                                                                                                                                                                     |                                                    |
| MU-06 | Update RMR < IMR                                                        | 0.09 / 0.09 / 0.01 → 0.08 / 0.09 / 0.01                  | Rejected | Rejected | ✅     | `failed to execute message; message index: 0: Ensure that MaintenanceMarginRatio < InitialMarginRatio <= ReduceMarginRatio`                                         |                                                    |
| MU-07 | Update RMR to same value (no-op)                                        | 0.09 / 0.09 / 0.01 → 0.09 / 0.09 / 0.01                  | Updated  | Updated  | ✅     |                                                                                                                                                                     |                                                    |
| MU-08 | Update RMR > IMR                                                        | 0.09 / 0.09 / 0.01 → 0.5 / 0.09 / 0.01                   | Updated  | Updated  | ✅     |                                                                                                                                                                     |                                                    |
| MU-09 | Update RMR using non-admin account (val)                                | 0.5 / 0.09 / 0.01 → 0.07 / 0.09 / 0.01                   | Rejected | Rejected | ✅     | `failed to execute message; message index: 0: market belongs to another admin (inj158ucxjzr6ccrlpmz8z05wylu8tr5eueqang232): Invalid access level to perform action` |                                                    |
| MU-10 | Update RMR to 0.0                                                       | 0.5 / 0.09 / 0.01 → 0.00 / 0.09 / 0.01                   | Rejected | Rejected | 🟡     | `no update value present: struct field error [/home/piotr/code/calculator-app/injective-chain/modules/exchange/types/v2/msgs.go:221]`                               | 🐛[#4](https://github.com/piotr-iohk/rmr/issues/4) |
| MU-11 | Update RMR < 0.0                                                        | 0.5 / 0.05 / 0.01 → -0.1 / 0.09 / 0.01                   | Rejected | Rejected | ✅     | `margin ratio cannot be less than minimum: -0.100000000000000000`                                                                                                   |                                                    |
| MU-12 | Update RMR to minimum allowed (max(0.005, default_reduce_margin_ratio)) | 0.06 / 0.05 / 0.01 → 0.08 / 0.05 / 0.01                  | Updated  | Updated  | ✅     |                                                                                                                                                                     |
| MU-13 | Update RMR to below minimum allowed                                     | 0.06 / 0.05 / 0.01 → 0.07 / 0.05 / 0.01                  | Rejected | Rejected | ✅     | Tx failed: `failed to execute message; message index: 0: Invalid margin ratio` new constraint discovered: `RMR >= default_reduce_margin_ratio`                      |                                                    |
| MU-14 | Update RMR to above miminum allowed                                     | 0.06 / 0.05 / 0.01 → 0.081 / 0.05 / 0.01                 | Updated  | Updated  | ✅     |                                                                                                                                                                     |                                                    |
| MU-15 | Update RMR to non-decimal string (“abc”)                                | 0.06 / 0.05 / 0.01 → abc / 0.05 / 0.01                   | Rejected | Rejected | ✅     |                                                                                                                                                                     |                                                    |
| MU-16 | Exceed precision                                                        | 0.06 / 0.05 / 0.01 → 0.1234567890123456789 / 0.05 / 0.01 | Rejected | Rejected | ✅     | `value '0.1234567890123456789' exceeds max precision by -1 decimal places: max precision 18`                                                                        |                                                    |
| MU-17 | Max precision, max allowed                                              | 0.06 / 0.05 / 0.01 → 0.999999999999999999 / 0.05 / 0.01  | Updated  | Updated  | ✅     |                                                                                                                                                                     |                                                    |
| MU-18 | Update RMR to 100                                                       | 0.06 / 0.05 / 0.01 → 1.00 / 0.05 / 0.01                  | Rejected | Rejected | ✅     | validation: `margin ratio cannot be greater than or equal to 1: 100.000000000000000000`                                                                             |                                                    |

---

## Notes

- While analysing "possible min / max values for RMR" we confirmed from source (https://github.com/Kishan-Dhakan/calculator-app/blob/master/injective-chain/modules/exchange/types/params.go#L429-L446 ) that any margin-ratio **should** be valid in the inclusive range **0.005 ≤ value < 1.0**.

- ⚠️ While executing TC MU-01 (update RMR from 0.06 → 0.07), we discovered that the Injective chain enforces a constraint where `RMR >= default_reduce_margin_ratio`. (https://github.com/Kishan-Dhakan/calculator-app/blob/master/injective-chain/modules/exchange/keeper/derivative_msg_server.go#L252-L255) This constraint is not mentioned in the assignment or public documentation and led to a failed update even though the new RMR was higher than IMR and MMR. The current default RMR value can be found in `injectived q exchange params`. As a result boundary-value test cases now include a note that the lower bound is effectively `max(0.005, default_reduce_margin_ratio)`

## Bug tickets

- 🐛[#1](https://github.com/piotr-iohk/rmr/issues/1) - [Constraint `MaintenanceMarginRatio < InitialMarginRatio <= ReduceMarginRatio` can be violated when proposing perpetual market](https://github.com/piotr-iohk/rmr/issues/1)
- 🐛[#2](https://github.com/piotr-iohk/rmr/issues/2) - [RMR constraints validated On-Chain instead of at submission](https://github.com/piotr-iohk/rmr/issues/2)
- 🐛[#3](https://github.com/piotr-iohk/rmr/issues/3) - [RMR value range \[max(0.005, default_reduce_margin_ratio), 1.0) constraint ambiguity](https://github.com/piotr-iohk/rmr/issues/3)
- 🐛[#4](https://github.com/piotr-iohk/rmr/issues/4) - [Unexpected error message when attempting to update perpetual market with RMR = 0 (`no update value present: struct field error`)](https://github.com/piotr-iohk/rmr/issues/4)

---

## Out of Scope

- **Impact of RMR on liquidation behavior** — This test plan focuses solely on functional validation of margin ratio constraints and updates, not on runtime or liquidation mechanics.
- **Interplay with advanced market parameters** — In particular, the `default_reduce_margin_ratio` can be modified via a separate governance proposal. Its update behavior and effect on RMR/IMR/MMR interactions are not tested here.
- **Instant perpetual market creation** — This test plan does not cover perpetual markets launched via instant (non-proposal-based) mechanisms, as described in the [Injective documentation](https://docs.injective.network/developers/modules/injective/exchange/00_derivative_market_concepts#perpetual-market-creation).
