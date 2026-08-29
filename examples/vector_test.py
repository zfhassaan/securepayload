#!/usr/bin/env python3
"""Verify SecurePayload against known ciphertext test vectors."""

import sys
from pathlib import Path

import securepayload
from securepayload.vectors import (
    KNOWN_ORDER_CIPHER,
    KNOWN_ORDER_PLAIN,
    KNOWN_STRING_CIPHER,
    KNOWN_STRING_PLAIN,
)


def main() -> None:
    try:
        securepayload.bootstrap(Path(__file__).resolve().parents[1] / ".env")
    except securepayload.InvalidKeyError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    assert securepayload.decrypt(KNOWN_ORDER_CIPHER) == KNOWN_ORDER_PLAIN
    assert securepayload.decrypt(KNOWN_STRING_CIPHER) == KNOWN_STRING_PLAIN
    assert securepayload.decrypt(securepayload.encrypt(KNOWN_ORDER_PLAIN)) == KNOWN_ORDER_PLAIN

    print("Known vector checks passed.")


if __name__ == "__main__":
    main()
