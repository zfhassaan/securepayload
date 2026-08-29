# SecurePayload API Reference

## Module API (recommended)

```python
import securepayload

securepayload.bootstrap()  # loads .env + configures key

ciphertext = securepayload.encrypt({"order_no": "m123"})
payload = securepayload.decrypt(ciphertext)
```

### `bootstrap(env_file=None, *, key=None, key_size=128, iteration_count=8, iv="") -> str`

Loads `.env` (when needed) and configures the module in one step. Returns the configured key.

### `configure(key=None, *, key_size=128, iteration_count=8, iv="", env_file=None)`

Initializes the module with an AES key. If `key` is omitted, loads `SECURITY_AES_KEY` from the environment (searching for `.env` when needed).

`iteration_count` and `iv` are accepted for API compatibility; ECB mode ignores IV.

### `encrypt(data) -> str`

Encrypts a `str`, `dict`, or `list` and returns a Base64 ciphertext string.

### `decrypt(encrypted_data) -> Any`

| Input | Behavior |
|-------|----------|
| `str` | Decrypted; JSON-parsed when valid JSON |
| `dict` / `list` | Returned unchanged (already decoded) |
| Other | `None` |

---

## `EncryptionService`

Class-based API for applications that manage their own key lifecycle.

```python
EncryptionService(key: str, *, key_size=128, iteration_count=8, iv="")
```

Methods mirror `securepayload.encrypt()` / `securepayload.decrypt()`.

---

## `Aes`

Low-level AES helper with `encrypt()`, `decrypt()`, `do_encrypt()`, `do_decrypt()`, `obj_pipe()`, and `set_new_key()`.

### `set_new_key(iv, key)`

Updates the key at runtime. Empty `iv` is allowed (ECB does not use IV).

---

## Exceptions

| Exception | When raised |
|-----------|-------------|
| `SecurityEncryptionError` | Base error |
| `InvalidKeyError` | Missing/invalid key |
| `EncryptionError` | Encryption failure |
| `DecryptionError` | Decryption, padding, or Base64 failure |

---

## Integration patterns

```python
import os
import securepayload

securepayload.configure(key=os.environ["SECURITY_AES_KEY"])
body = securepayload.encrypt({"event": "order.updated", "order_no": "m123"})
data = securepayload.decrypt(request_body)
```
