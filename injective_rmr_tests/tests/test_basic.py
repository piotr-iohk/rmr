def test_chain_status():
    from subprocess import run

    result = run(["injectived", "status"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "latest_block_height" in result.stdout
