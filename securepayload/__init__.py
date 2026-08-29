"""
SecurePayload — Python AES API payload encryption.

Primary usage::

    import securepayload

    securepayload.bootstrap()
    ciphertext = securepayload.encrypt({"order_no": "m123"})
    payload = securepayload.decrypt(ciphertext)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .aes import Aes
from .encryption_service import EncryptionService
from .env import find_env_file, load_env
from .exceptions import (
    DecryptionError,
    EncryptionError,
    InvalidKeyError,
    SecurityEncryptionError,
)

__version__ = "1.0.0"

_service: EncryptionService | None = None


def configure(
    key: str | None = None,
    *,
    key_size: int = 128,
    iteration_count: int = 8,
    iv: str = "",
    env_file: Path | str | None = None,
) -> None:
    """
    Set the AES key used by ``encrypt`` and ``decrypt``.

    If ``key`` is omitted, loads ``SECURITY_AES_KEY`` from the environment
    (searching for ``.env`` when needed).
    """
    global _service

    resolved = key
    if not resolved:
        load_env(env_file)
        resolved = os.environ.get("SECURITY_AES_KEY")

    if not resolved:
        raise InvalidKeyError(
            "AES key is not configured. Set SECURITY_AES_KEY in .env or call configure(key=...)."
        )

    _service = EncryptionService(
        resolved,
        key_size=key_size,
        iteration_count=iteration_count,
        iv=iv,
    )


def bootstrap(
    env_file: Path | str | None = None,
    *,
    key: str | None = None,
    key_size: int = 128,
    iteration_count: int = 8,
    iv: str = "",
) -> str:
    """
    Load ``.env`` and configure the module in one step.

    If ``env_file`` is omitted, searches upward from the current working directory
    for a ``.env`` file. Returns the configured key.
    """
    if key is None:
        load_env(env_file)
        key = os.environ.get("SECURITY_AES_KEY")
    if not key:
        raise InvalidKeyError(
            "AES key is not configured. Set SECURITY_AES_KEY in .env or call bootstrap(key=...)."
        )
    configure(key=key, key_size=key_size, iteration_count=iteration_count, iv=iv)
    return key


def _get_service() -> EncryptionService:
    if _service is None:
        configure()
    assert _service is not None
    return _service


def encrypt(data: dict | list | str) -> str:
    """Encrypt a payload to a Base64 AES ciphertext string."""
    return _get_service().encrypt(data)


def decrypt(encrypted_data: Any) -> Any:
    """Decrypt a Base64 ciphertext string or pass through dict/list payloads."""
    return _get_service().decrypt(encrypted_data)


__all__ = [
    "Aes",
    "EncryptionService",
    "SecurityEncryptionError",
    "EncryptionError",
    "DecryptionError",
    "InvalidKeyError",
    "configure",
    "bootstrap",
    "encrypt",
    "decrypt",
    "load_env",
    "find_env_file",
    "__version__",
]
