"""Load project environment for tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import securepayload

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
securepayload.load_env(_PROJECT_ROOT / ".env")


def _require_aes_key() -> str:
    key = os.environ.get("SECURITY_AES_KEY")
    if not key:
        pytest.fail("SECURITY_AES_KEY is not set. Copy .env.example to .env and set your key.")
    return key


@pytest.fixture(scope="session")
def aes_key() -> str:
    return _require_aes_key()


@pytest.fixture(scope="session", autouse=True)
def configure_securepayload(aes_key: str) -> None:
    securepayload.configure(key=aes_key)
