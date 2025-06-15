# **Test Plan: Reduce Margin Ratio (RMR)**

## Objective

Verify that:

- A new perpetual market can be created with a `reduce-margin-ratio` (RMR) value.
- An existing perpetual market’s `reduce-margin-ratio` value can be updated.
- The values are correctly stored and retrievable via CLI query commands.
- Constraints on RMR (`RMR ≥ IMR > MMR`) are respected and validated.
- What are the possible min and max values of RMR and test boundary values around them. Hint: https://github.com/Kishan-Dhakan/calculator-app/blob/master/injective-chain/modules/exchange/types/params.go#L429-L446 (It seems that all margin ratios values are valid when between 0.005 and 1.0)
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
1. Create new perpetual market using modified `setup_tst_usdt_perp.sh` from this repo, like `setup_tst_usdt_perp.sh rmr_value imr_value mmr_value` e.g. `setup_tst_usdt_perp.sh 0.06 0.05 0.01`
2. Verify market is created and the RMR / IMR / MMR values are set as expected, e.g.

```
injectived q exchange derivative-markets --chain-id injective-1 -o json \
| jq '.markets[] | select(.market.ticker == "TST/USDT PERP")
| {reduce_margin_ratio: .market.reduce_margin_ratio,
   initial_margin_ratio: .market.initial_margin_ratio,
   maintenance_margin_ratio: .market.maintenance_margin_ratio}'
```

3. In case market is not created (for some cases it is expected), look up transaction for `Submitting proposal to launch TST/USDT PERP market` by its `txhash`. Look at transaction code and raw_log for potential failure reason e.g.

```
injectived q tx AD665B0B09FE8E523DDE820E831978D6167637E7DFFA0976D613A501E43CBD13 --chain-id injective-1 -o json | jq
```

| TC ID | Description                              | RMR / IMR / MMR       | Expected | Actual   | Result | Notes                                                                                                                                                                                                                            |
| ----- | ---------------------------------------- | --------------------- | -------- | -------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MC-01 | Create market with valid RMR > IMR > MMR | 0.06 / 0.05 / 0.01    | Created  | Created  | ✅     |                                                                                                                                                                                                                                  |
| MC-02 | Create market with RMR = IMR             | 0.05 / 0.05 / 0.01    | Created  | Created  | ✅     |                                                                                                                                                                                                                                  |
| MC-03 | RMR == IMR == MMR                        | 0.05 / 0.05 / 0.05    | Rejected | Created  | :x:    | Constraint violated `RMR ≥ IMR > MMR`                                                                                                                                                                                            |
| MC-04 | RMR == IMR < MMR                         | 0.05 / 0.05 / 0.06    | Rejected | Rejected | ✅     | Proposal rejected, tx failed: `failed to execute message; message index: 0: Ensure that MaintenanceMarginRatio < InitialMarginRatio <= ReduceMarginRatio: invalid proposal message`                                              |
| MC-05 | RMR < IMR > MMR                          | 0.02 / 0.05 / 0.01    | Rejected | Rejected | ✅     | Proposal rejected, tx failed: `failed to execute message; message index: 0: Ensure that MaintenanceMarginRatio < InitialMarginRatio <= ReduceMarginRatio: invalid proposal message`                                              |
| MC-06 | RMR = 0 < IMR                            | 0.0 / 0.05 / 0.01     | Rejected | Rejected | ✅     | Proposal rejected, tx failed: `failed to execute message; message index: 0: margin ratio cannot be less than minimum: 0.000000000000000000: invalid proposal message`, Minimum is not specified in the error msg, nor documented |
| MC-07 | max RMR = 1.0                            | 1.0 / 0.1 / 0.05      | Created  | Rejected | :x:    | Proposal rejected, tx failed: `failed to execute message; message index: 0: margin ratio cannot be greater than or equal to 1: 1.000000000000000000: invalid proposal message`                                                   |
| MC-08 | over limits RMR = 100                    | 100 / 0.1 / 0.05      | Rejected | Rejected | ✅     | Proposal rejected, tx failed: `failed to execute message; message index: 0: margin ratio cannot be greater than or equal to 1: 100.000000000000000000: invalid proposal message`                                                 |
| MC-09 | min possible RMR                         | 0.006 / 0.006 / 0.005 | Created  | Created  | ✅     |                                                                                                                                                                                                                                  |
| MC-10 | min RMR, but RMR == IMR == MMR           | 0.005 / 0.005 / 0.005 | Rejected | Created  | :x:    | Constraint violated `RMR ≥ IMR > MMR`                                                                                                                                                                                            |
| MC-11 | RMR non-decimal (e.g. "abc")             | "abc" / 0.1 / 0.05    | Rejected | Rejected | ✅     | `could not parse abc as math.LegacyDec for field ReduceMarginRatio: failed to set decimal string with base 10: abc000000000000000000` , rejected before sending                                                                  |
| MC-12 | Missing RMR field                        | – / 0.1 / 0.05        | Rejected | Rejected | ✅     | Proposal rejected, tx failed: `"failed to execute message; message index: 0: margin ratio cannot be less than minimum: 0.000000000000000000: invalid proposal message`                                                           |
| MC-13 | MRs below 0                              | -0.06 / -0.05 / -0.01 | Rejected | Rejected | ✅     | Proposal rejected, tx failed: `"failed to execute message; message index: 0: margin ratio cannot be less than minimum: -0.050000000000000000: invalid proposal message`                                                          |

---

### Market Update

---

## Out of Scope

---

## Notes
