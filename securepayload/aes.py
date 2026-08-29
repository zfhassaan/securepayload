from __future__ import annotations

import base64
import binascii
import copy
import json
from typing import Any, Callable, Iterable, Mapping, Sequence

from Crypto.Cipher import AES

from .exceptions import DecryptionError, EncryptionError, InvalidKeyError, SecurityEncryptionError

_JSON_SEPARATORS = (",", ":")


def prepare_key(key: str, key_size: int = 128) -> bytes:
    if not key:
        raise InvalidKeyError("AES key must be a non-empty string.")

    byte_len = key_size // 8
    raw = key.encode("utf-8")

    if len(raw) < byte_len:
        return raw.ljust(byte_len, b"\0")
    if len(raw) > byte_len:
        return raw[:byte_len]
    return raw


def _pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def _pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
    if not data:
        raise DecryptionError("Cannot unpad empty ciphertext.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise DecryptionError("Invalid PKCS#7 padding.")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise DecryptionError("Invalid PKCS#7 padding bytes.")
    return data[:-pad_len]


def _to_json(data: Any) -> str:
    return json.dumps(data, separators=_JSON_SEPARATORS, ensure_ascii=False)


class Aes:
    def __init__(
        self,
        key: str,
        *,
        key_size: int = 128,
        iteration_count: int = 8,
        iv: str = "",
    ) -> None:
        # iteration_count and iv are accepted for API compatibility; ECB ignores IV.
        self.key_size = key_size
        self.iteration_count = iteration_count
        self.iv = iv
        self.key = key
        self._key_bytes = prepare_key(key, key_size)

    def set_new_key(self, iv: str, key: str) -> tuple[str, str]:
        """Update IV and key. Empty IV is allowed (ECB mode does not use IV)."""
        if not key:
            raise InvalidKeyError("Invalid key")
        self.iv = iv
        self.key = key
        self._key_bytes = prepare_key(key, self.key_size)
        return self.iv, self.key

    def obj_copy(self, obj: Any) -> Any:
        """Deep copy helper used by ``obj_pipe``."""
        return copy.deepcopy(obj)

    def obj_pipe(
        self,
        obj: Mapping[str, Any],
        mode: int,
        props: Iterable[str],
    ) -> dict[str, Any]:
        """Encrypt (mode > 0) or decrypt (mode <= 0) selected object properties."""
        result = dict(self.obj_copy(obj))
        for prop in props:
            if prop not in obj:
                continue
            result[prop] = self.encrypt(obj[prop]) if mode > 0 else self.decrypt(obj[prop])
        return result

    def _transform(
        self,
        data: Any,
        *,
        props: Sequence[str] | None,
        pipe_mode: int,
        on_scalar: Callable[[str], str],
        error_cls: type[SecurityEncryptionError],
        action: str,
    ) -> Any:
        if isinstance(data, Mapping):
            if props:
                return self.obj_pipe(data, pipe_mode, props)
            return on_scalar(_to_json(data))
        if isinstance(data, (list, tuple)):
            if props:
                return [self.obj_pipe(item, pipe_mode, props) for item in data]
            return on_scalar(_to_json(data))
        if isinstance(data, str):
            return on_scalar(data)
        if isinstance(data, int):
            return on_scalar(str(data))
        raise error_cls(f"Unsupported {action} input type: {type(data).__name__}")

    def encrypt(self, data: Any, props: Sequence[str] | None = None) -> Any:
        """Encrypt strings, numbers, dicts, or lists."""
        return self._transform(
            data,
            props=props,
            pipe_mode=1,
            on_scalar=self.do_encrypt,
            error_cls=EncryptionError,
            action="encrypt",
        )

    def decrypt(self, data: Any, props: Sequence[str] | None = None) -> Any:
        """Decrypt strings, numbers, dicts, or lists."""
        return self._transform(
            data,
            props=props,
            pipe_mode=0,
            on_scalar=self.do_decrypt,
            error_cls=DecryptionError,
            action="decrypt",
        )

    def do_encrypt(self, plain_text: str) -> str:
        """Encrypt plaintext and return Base64 ciphertext."""
        try:
            cipher = AES.new(self._key_bytes, AES.MODE_ECB)
            padded = _pkcs7_pad(plain_text.encode("utf-8"))
            encrypted = cipher.encrypt(padded)
            return base64.b64encode(encrypted).decode("ascii")
        except SecurityEncryptionError:
            raise
        except (TypeError, ValueError, UnicodeError) as exc:
            raise EncryptionError("Encryption failed.") from exc

    def do_decrypt(self, cipher_text: str, key: str | None = None, iv: str | None = None) -> str:
        """
        Decrypt Base64 ciphertext.

        ``key`` and ``iv`` are optional overrides; only ``key`` is applied when
        provided. ECB mode ignores IV.
        """
        _ = iv  # ECB mode does not use IV.
        try:
            key_bytes = self._key_bytes if key is None else prepare_key(key, self.key_size)
            raw = base64.b64decode(cipher_text, validate=True)
            if len(raw) % 16 != 0:
                raise DecryptionError("Ciphertext length must be a multiple of the AES block size.")
            cipher = AES.new(key_bytes, AES.MODE_ECB)
            decrypted = cipher.decrypt(raw)
            return _pkcs7_unpad(decrypted).decode("utf-8")
        except SecurityEncryptionError:
            raise
        except (binascii.Error, TypeError, ValueError, UnicodeError) as exc:
            raise DecryptionError("Decryption failed.") from exc
