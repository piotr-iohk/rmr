import pytest
from cli.injectived_cli import InjectiveCLIError, InjectivedCLI
from cli.utils import extract_txhash_from_stdout, wait_for_tx_success


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

    market_id = perpetual_market_setup
    market = cli.query.derivative_market(market_id)
    assert market is not None

    with pytest.raises(InjectiveCLIError) as exc_info:
        cli.tx.update_derivative_market_rmr(
            market_id=market_id, new_rmr=new_rmr, from_acct="testcandidate"
        )
    resp = exc_info.value.result
    assert expected_error in resp.stderr


def test_mu_4_update_rmr_eq_imr(perpetual_market_setup):
    """MU-04 - Update RMR to equal IMR"""

    cli = InjectivedCLI()

    market_id = perpetual_market_setup
    market = cli.query.derivative_market(market_id)
    assert market is not None
    assert float(market["market"]["reduce_margin_ratio"]) != float(
        market["market"]["initial_margin_ratio"]
    ), "RMR should initially not be equal IMR"

    # Update RMR to equal IMR
    new_rmr = market["market"]["initial_margin_ratio"]

    resp = cli.tx.update_derivative_market_rmr(
        market_id=market_id, new_rmr=new_rmr, from_acct="testcandidate"
    )

    tx_hash = extract_txhash_from_stdout(resp.stdout)
    wait_for_tx_success(
        tx_hash=tx_hash,
        cli=cli,
    )

    updated_market_info = cli.query.derivative_market(market_id)

    assert updated_market_info is not None
    assert float(updated_market_info["market"]["reduce_margin_ratio"]) == float(
        updated_market_info["market"]["initial_margin_ratio"]
    )
