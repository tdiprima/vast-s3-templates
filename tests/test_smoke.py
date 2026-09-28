"""Smoke test against a local moto S3 server (no VAST needed).

    pip install "moto[server]" pytest
    pytest
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PORT = 5555


@pytest.fixture(scope="session")
def env():
    proc = subprocess.Popen(
        [sys.executable, "-m", "moto.server", "-p", str(PORT)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    e = {
        **os.environ,
        "VAST_S3_ENDPOINT": f"http://127.0.0.1:{PORT}",
        "VAST_S3_ACCESS_KEY": "testing",
        "VAST_S3_SECRET_KEY": "testing",
        "VAST_S3_BUCKET": "smoke",
    }
    yield e
    proc.terminate()


def run(env, *args):
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, env=env, capture_output=True, text=True, check=True
    ).stdout


def test_end_to_end(env, tmp_path):
    src = tmp_path / "big.bin"
    src.write_bytes(os.urandom(40 * 1024 * 1024))  # > multipart threshold

    assert "created smoke" in run(env, "scripts/create_bucket.py", "-v")
    assert "smoke: Enabled" in run(env, "scripts/versioning.py", "status")
    run(env, "scripts/upload.py", str(src), "-p", "in/")
    run(env, "scripts/upload.py", str(src), "-p", "in/")  # second version
    assert "big.bin" in run(env, "scripts/list_objects.py", "in/")

    out = run(env, "scripts/download.py", "in/big.bin", str(tmp_path / "dl.bin"))
    assert "40.0 MiB" in out
    assert (tmp_path / "dl.bin").read_bytes() == src.read_bytes()  # no corruption

    assert run(env, "scripts/versioning.py", "list").count("big.bin") == 2
    assert run(env, "scripts/presigned_url.py", "in/big.bin").startswith("http")
    assert "deleted 1 objects" in run(env, "scripts/delete.py", "-y", "-r", "in/")
    assert "Parquet round-trip" in run(env, "examples/pandas_load.py")
