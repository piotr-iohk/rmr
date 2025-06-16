import time
from typing import Any
from cli.injectived_cli import InjectivedCLI


def extract_txhash_from_stdout(stdout: str) -> str:
    for line in stdout.splitlines():
        if line.startswith("txhash:"):
            return line.split(":", 1)[1].strip()
    raise ValueError("txhash not found in stdout")


def wait_for_tx_success(
    cli: InjectivedCLI, tx_hash: str, timeout: int = 20, interval: float = 1.0
) -> dict[str, Any]:
    """
    Waits until the transaction is confirmed and successful (`code == 0`).
    """
    start_time = time.time()
    while True:
        try:
            tx_data = cli.query.tx(tx_hash, json_output=True)
            code = int(tx_data.get("code", 0))

            if code == 0:
                return tx_data
            else:
                raise RuntimeError(
                    f"❌ TX failed: code={code}, log={tx_data.get('raw_log')}"
                )
        except Exception as e:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"⏰ Timed out waiting for tx {tx_hash}: {e}")
            time.sleep(interval)
