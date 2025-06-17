import allure
import pytest
from cli.injectived_cli import InjectiveCLIError, InjectivedCLI
from cli.utils import extract_txhash_from_stdout, wait_for_tx_success


@allure.title(
    "Invalid RMR values raise proper CLI errors (MU-03, MU-11, MU-15, MU-16, MU-18)"
)
@pytest.mark.parametrize(
    "new_rmr, expected_error",
    [
        ("1.0", "margin ratio cannot be greater than or equal to 1"),
        ("100", "margin ratio cannot be greater than or equal to 1"),
        ("-0.1", "margin ratio cannot be less than minimum"),
        ("abc", "failed to set decimal string with base 10"),
        ("0.1234567890123456789", "exceeds max precision by -1 decimal places"),
    ],
)
def test_update_rmr_invalid_inputs(perpetual_market_setup, new_rmr, expected_error):
    """MU-03, MU-11, MU-15, MU-16, MU-18 - Test updating RMR with invalid inputs"""

    cli = InjectivedCLI()

    with allure.step("Look up current market"):
        market_id = perpetual_market_setup
        market = cli.query.derivative_market(market_id)
        assert market is not None

    with allure.step(f"Attempt update RMR to invalid value {new_rmr}"):
        with pytest.raises(InjectiveCLIError) as exc_info:
            cli.tx.update_derivative_market_rmr(
                market_id=market_id, new_rmr=new_rmr, from_acct="testcandidate"
            )

    with allure.step("Verify CLI stderr contains expected error message"):
        resp = exc_info.value.result
        assert expected_error in resp.stderr


@allure.title("Update RMR to equal IMR (MU-04)")
def test_mu_4_update_rmr_to_eq_imr(perpetual_market_setup):
    """MU-04 - Update RMR to equal IMR"""

    with allure.step("Query market and assert initial RMR != IMR"):
        cli = InjectivedCLI()
        market_id = perpetual_market_setup
        market = cli.query.derivative_market(market_id)
        assert market is not None
        assert float(market["market"]["reduce_margin_ratio"]) != float(
            market["market"]["initial_margin_ratio"]
        ), "RMR should initially not be equal IMR"

    with allure.step("Update RMR to equal IMR"):
        new_rmr = market["market"]["initial_margin_ratio"]
        resp = cli.tx.update_derivative_market_rmr(
            market_id=market_id, new_rmr=new_rmr, from_acct="testcandidate"
        )
        tx_hash = extract_txhash_from_stdout(resp.stdout)
        wait_for_tx_success(tx_hash=tx_hash, cli=cli)

    with allure.step("Verify RMR was updated to equal IMR"):
        updated_market_info = cli.query.derivative_market(market_id)
        assert updated_market_info is not None
        assert float(updated_market_info["market"]["reduce_margin_ratio"]) == float(
            updated_market_info["market"]["initial_margin_ratio"]
        )


@allure.title("Minimal test")
def test_dummy_allure():
    with allure.step("step 1"):
        assert True
