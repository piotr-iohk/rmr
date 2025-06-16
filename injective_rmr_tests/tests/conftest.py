import os
import subprocess
import shutil
import signal
import time
import pytest
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def local_chain():
    """Start Injective local chain before any tests run."""
    root_dir = Path(__file__).resolve().parent.parent.parent  # goes up to the repo root

    setup_script = root_dir / "setup.sh"
    node_script = root_dir / "injectived.sh"

    if not setup_script.exists() or not node_script.exists():
        pytest.exit("❌ Could not find setup.sh or injectived.sh in project root.")

    if shutil.which("injectived") is None:
        pytest.exit("❌ injectived binary not found in PATH.")

    print("\n⚙️  Starting local Injective chain...")

    subprocess.run(["rm", "-rf", ".injectived"], cwd=root_dir)

    setup = subprocess.run(
        [str(setup_script)], cwd=root_dir, capture_output=True, text=True
    )
    if setup.returncode != 0:
        pytest.exit(f"❌ setup.sh failed:\n{setup.stderr}")

    node_proc = subprocess.Popen([str(node_script)], cwd=root_dir)
    time.sleep(5)  # wait a bit before test execution begins

    yield  # tests will now run

    print("\n🛑  Tearing down local Injective chain...")

    # Try graceful shutdown first (SIGTERM to the whole group)
    try:
        os.killpg(os.getpgid(node_proc.pid), signal.SIGTERM)
        node_proc.wait(timeout=10)
    except Exception:
        # Force-kill if still alive
        os.killpg(os.getpgid(node_proc.pid), signal.SIGKILL)
