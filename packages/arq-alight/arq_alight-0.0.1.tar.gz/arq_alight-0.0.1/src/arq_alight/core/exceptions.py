"""Custom exceptions for Arq Alight."""


class ArqAlightError(Exception):
    """Base exception for all Arq Alight errors."""

    pass


class BackupNotFoundError(ArqAlightError):
    """Raised when a backup cannot be found."""

    pass


class BackupCorruptedError(ArqAlightError):
    """Raised when backup data is corrupted or invalid."""

    pass


class EncryptionError(ArqAlightError):
    """Raised when encryption/decryption fails."""

    pass


class DecryptionError(EncryptionError):
    """Raised specifically when decryption fails."""

    pass


class InvalidPasswordError(EncryptionError):
    """Raised when the provided password is incorrect."""

    pass


class CompressionError(ArqAlightError):
    """Raised when compression/decompression fails."""

    pass


class StorageError(ArqAlightError):
    """Raised when storage operations fail."""

    pass


class S3Error(StorageError):
    """Raised when S3 operations fail."""

    pass


class AuthenticationError(ArqAlightError):
    """Raised when authentication fails."""

    pass


class AWSCredentialsError(AuthenticationError):
    """Raised when AWS credentials are missing or invalid."""

    pass


class CacheError(ArqAlightError):
    """Raised when cache operations fail."""

    pass


class CacheNotFoundError(CacheError):
    """Raised when cache data is not found."""

    pass


class CacheCorruptedError(CacheError):
    """Raised when cache data is corrupted."""

    pass


class RestoreError(ArqAlightError):
    """Raised when restore operations fail."""

    pass


class RestorePermissionError(RestoreError):
    """Raised when lacking permissions for restore operations."""

    pass


class ChecksumError(RestoreError):
    """Raised when checksum verification fails."""

    pass


class ConfigError(ArqAlightError):
    """Raised when configuration operations fail."""

    pass


class UnsupportedVersionError(ArqAlightError):
    """Raised when encountering unsupported Arq format versions."""

    def __init__(self, version: int, supported_versions: list[int]):
        self.version = version
        self.supported_versions = supported_versions
        super().__init__(f"Unsupported version {version}. Supported versions: {supported_versions}")
