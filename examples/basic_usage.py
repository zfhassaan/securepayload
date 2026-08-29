#!/usr/bin/env python3
"""Basic SecurePayload encryption example."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import securepayload
from securepayload.vectors import KNOWN_STRING_CIPHER


def main() -> None:
    try:
        securepayload.bootstrap(Path(__file__).resolve().parents[1] / ".env")
    except securepayload.InvalidKeyError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    payload = {
        "order_no": "26168785012837",
        "channel": "CARD",
        "consignee": "zfhassaan",
    }

    print("=== securepayload.encrypt / securepayload.decrypt ===")
    encrypted = securepayload.encrypt(payload)
    print("Encrypted:", encrypted)

    decrypted = securepayload.decrypt(encrypted)
    print("Decrypted:", json.dumps(decrypted, indent=2))

    print("\n=== Known test vector ===")
    print("Ciphertext:", KNOWN_STRING_CIPHER)
    print("Decrypted :", securepayload.decrypt(KNOWN_STRING_CIPHER))


if __name__ == "__main__":
    main()
