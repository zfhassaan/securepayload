#!/usr/bin/env python3
"""
Thin wrapper that runs the pytest suite.

Usage:
    python examples/run_tests.py

Requires SECURITY_AES_KEY in .env (copy from .env.example).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    raise SystemExit(pytest.main(["-v", str(ROOT / "tests")]))


if __name__ == "__main__":
    main()
