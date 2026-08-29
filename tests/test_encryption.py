"""Tests for SecurePayload."""

import pytest
import securepayload
from securepayload import Aes
from securepayload.aes import prepare_key
from securepayload.exceptions import DecryptionError, InvalidKeyError
from securepayload.vectors import (
    KNOWN_ORDER_CIPHER,
    KNOWN_ORDER_PLAIN,
    KNOWN_STRING_CIPHER,
    KNOWN_STRING_PLAIN,
    SAMPLE_KEY,
)


def test_prepare_key_exact_length():
    assert prepare_key(SAMPLE_KEY) == SAMPLE_KEY.encode("utf-8")


def test_prepare_key_rejects_empty():
    with pytest.raises(InvalidKeyError):
        prepare_key("")


def test_aes_string_roundtrip(aes_key):
    aes = Aes(aes_key)
    plain = '{"test":"hello"}'
    assert aes.decrypt(aes.encrypt(plain)) == plain


def test_aes_matches_known_string_vector():
    assert securepayload.decrypt(KNOWN_STRING_CIPHER) == KNOWN_STRING_PLAIN
    assert securepayload.encrypt(KNOWN_STRING_PLAIN) == KNOWN_STRING_CIPHER


def test_encryption_service_dict_roundtrip():
    payload = dict(KNOWN_ORDER_PLAIN)
    encrypted = securepayload.encrypt(payload)
    assert securepayload.decrypt(encrypted) == payload


def test_encryption_service_matches_known_order_vector():
    assert securepayload.decrypt(KNOWN_ORDER_CIPHER) == KNOWN_ORDER_PLAIN


def test_encryption_service_passthrough_for_dict():
    payload = {"already": "decoded"}
    assert securepayload.decrypt(payload) is payload


def test_obj_pipe_selective_encrypt(aes_key):
    aes = Aes(aes_key)
    obj = {"public": "visible", "secret": "hidden"}
    encrypted = aes.obj_pipe(obj, 1, ["secret"])
    assert encrypted["public"] == "visible"
    assert encrypted["secret"] != "hidden"
    restored = aes.obj_pipe(encrypted, 0, ["secret"])
    assert restored == obj


def test_set_new_key_allows_empty_iv(aes_key):
    aes = Aes(aes_key)
    iv, key = aes.set_new_key(iv="", key=aes_key)
    assert iv == ""
    assert key == aes_key
    assert aes.decrypt(aes.encrypt("ping")) == "ping"


def test_decrypt_rejects_invalid_base64(aes_key):
    aes = Aes(aes_key)
    with pytest.raises(DecryptionError):
        aes.do_decrypt("not-valid-base64!!!")
