# RMR Testing

This repository contains a **comprehensive functional test plan**, **bug reports**, and **automated tests** for validating the behavior of the **Reduce Margin Ratio (RMR)** field in Injective's perpetual markets.

## Test Plan

The full test plan is available in [TestPlan.md](TestPlan.md).

## Bug Report

All discovered bugs during testing have been filed as GitHub [Issues](https://github.com/piotr-iohk/rmr/issues) in this repository, and are cross-referenced in `TestPlan.md`.

## Test Automation

This repository also includes automated tests using `pytest`. The test runner will:

- Start a local Injective chain using bundled scripts
- Launch a test perpetual market (`TST/USDT PERP`)
- Execute test scenarios that assert correct RMR behavior

### Prerequisites

- ✅ [`poetry`](https://python-poetry.org/docs/#installation) installed
- ✅ [`allure` CLI](https://docs.qameta.io/allure/#_installing_a_commandline) installed and available in `$PATH`
- ✅ [`injectived`](https://github.com/InjectiveFoundation/injective-core) installed and available in `$PATH`

### 🔧 Installation

```bash
git clone https://github.com/piotr-iohk/rmr.git
cd rmr/injective_rmr_tests

poetry install
```

### 🧪 Running Tests

```bash
poetry run pytest -v --alluredir=allure-results
allure serve allure-results
```
