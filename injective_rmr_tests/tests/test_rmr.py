from cli.injectived_cli import InjectivedCLI
from cli.utils import extract_txhash_from_stdout, wait_for_tx_success


def test_mu_4_update_rmr_eq_imr(perpetual_market_setup):
    cli = InjectivedCLI()

    market_id = perpetual_market_setup
    market = cli.query.get_market_by_id(market_id)
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

    updated_market_info = cli.query.get_market_by_id(market_id)

    assert updated_market_info is not None
    assert float(updated_market_info["market"]["reduce_margin_ratio"]) == float(
        updated_market_info["market"]["initial_margin_ratio"]
    )
