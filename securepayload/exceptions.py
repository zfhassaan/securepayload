class SecurityEncryptionError(Exception):
    """Base exception for encryption package errors."""


class InvalidKeyError(SecurityEncryptionError):
    """Raised when the AES key is missing or invalid."""


class EncryptionError(SecurityEncryptionError):
    """Raised when encryption fails."""


class DecryptionError(SecurityEncryptionError):
    """Raised when decryption fails."""
