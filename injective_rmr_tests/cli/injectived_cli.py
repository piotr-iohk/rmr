import os
import json
import subprocess
from typing import Any, Optional, Union


class InjectiveCLIError(Exception):
    def __init__(self, message: str, result: subprocess.CompletedProcess):
        super().__init__(message)
        self.result = result


class InjectivedCLI:
    def __init__(
        self,
        chain_id: str = "injective-1",
        passphrase: str = "12345678",
    ):
        self.chain_id = chain_id
        self.passphrase = passphrase
        self.env = os.environ.copy()

        self.tx = TxGroup(self)
        self.query = QueryGroup(self)

    def run(
        self,
        args: list[str],
        passphrase: Optional[str] = None,
        passphrase_repeats: int = 1,
        json_output: bool = False,
    ) -> Union[subprocess.CompletedProcess, dict[str, Any]]:
        # print(f"Running: injectived {' '.join(args)}")
        if passphrase:
            input_text = "\n".join([passphrase] * passphrase_repeats) + "\n"

        cmd = ["injectived"] + args
        if json_output:
            cmd += ["-o", "json"]

        result = subprocess.run(
            cmd,
            input=input_text if passphrase else None,
            capture_output=True,
            text=True,
            env=self.env,
        )
        if result.returncode != 0:
            raise InjectiveCLIError(
                f"Command failed: {' '.join(cmd)}; std_err: {result.stderr}", result
            )
        if json_output:
            return json.loads(result.stdout)

        return result


class TxGroup:
    def __init__(self, cli: InjectivedCLI):
        self.cli = cli

    def update_derivative_market_rmr(
        self,
        market_id: str,
        new_rmr: str,
        from_acct: str,
        passphrase: Optional[str] = None,
    ) -> subprocess.CompletedProcess:
        return self.cli.run(
            [
                "tx",
                "exchange",
                "update-derivative-market",
                market_id,
                "--reduce-margin-ratio",
                new_rmr,
                "--from",
                from_acct,
                "--chain-id",
                self.cli.chain_id,
                "--gas-prices",
                "500000000inj",
                "--gas",
                "10000000",
                "--yes",
            ],
            passphrase=passphrase or self.cli.passphrase,
            passphrase_repeats=1,
        )


class QueryGroup:
    def __init__(self, cli: InjectivedCLI):
        self.cli = cli

    def derivative_markets(
        self, json_output: bool = True
    ) -> subprocess.CompletedProcess:
        return self.cli.run(
            [
                "q",
                "exchange",
                "derivative-markets",
                "--chain-id",
                self.cli.chain_id,
            ],
            json_output=json_output,
        )

    def get_market_by_ticker(self, ticker: str) -> Optional[dict[str, Any]]:
        data = self.derivative_markets(json_output=True)
        for market in data["markets"]:
            if market["market"]["ticker"] == ticker:
                return market
        return None

    def get_market_by_id(self, market_id: str) -> Optional[dict[str, Any]]:
        data = self.derivative_markets(json_output=True)
        for market in data["markets"]:
            if market["market"]["market_id"] == market_id:
                return market
        return None

    def tx(self, tx_hash: str, json_output: bool = True) -> subprocess.CompletedProcess:
        return self.cli.run(
            [
                "q",
                "tx",
                tx_hash,
                "--chain-id",
                self.cli.chain_id,
            ],
            json_output=json_output,
        )

    def proposal(
        self, proposal_id: Union[int, str], json_output: bool = True
    ) -> subprocess.CompletedProcess:
        return self.cli.run(
            [
                "q",
                "gov",
                "proposal",
                str(proposal_id),
                "--chain-id",
                self.cli.chain_id,
            ],
            json_output=json_output,
        )


if __name__ == "__main__":
    # Example usage
    cli = InjectivedCLI()
    resp = cli.query.derivative_markets()
    print(resp)
    market_id = "0x8fde97d09cbdf47ad5ee9d076d0be329c30af3357946e038ef9f6d14a083f692"

    resp = cli.tx.update_derivative_market_rmr(
        market_id=market_id, new_rmr="0.99", from_acct="testcandidate"
    )
    print(resp.stdout)
