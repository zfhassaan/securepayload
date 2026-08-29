"""High-level encryption service for API payloads."""

from __future__ import annotations

import json
from typing import Any

from .aes import Aes


class EncryptionService:
    """
    Encrypt and decrypt API payloads using AES-128-ECB.

    Provide your own AES key (16 characters for AES-128) to encrypt/decrypt
    payloads exchanged with APIs.
    """

    def __init__(
        self,
        key: str,
        *,
        key_size: int = 128,
        iteration_count: int = 8,
        iv: str = "",
    ) -> None:
        self._aes = Aes(
            key,
            key_size=key_size,
            iteration_count=iteration_count,
            iv=iv,
        )

    def decrypt(self, encrypted_data: Any) -> Any:
        """
        Decrypt AES payload.

        - dict/list: returned unchanged (already decoded)
        - str: decrypted and JSON-decoded when possible; raw string otherwise
        - other: ``None``
        """
        if isinstance(encrypted_data, (dict, list)):
            return encrypted_data

        if isinstance(encrypted_data, str):
            plaintext = self._aes.decrypt(encrypted_data)
            try:
                return json.loads(plaintext)
            except json.JSONDecodeError:
                return plaintext

        return None

    def encrypt(self, data: dict | list | str) -> str:
        """Encrypt data to a Base64 AES string."""
        return self._aes.encrypt(data)

    Decrypt = decrypt
    Encrypt = encrypt
