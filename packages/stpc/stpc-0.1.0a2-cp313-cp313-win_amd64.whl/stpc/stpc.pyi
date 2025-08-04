from typing import Tuple

import warnings
import functools

def deprecated(reason: str):
    def decorator(func_or_class):
        @functools.wraps(func_or_class)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func_or_class.__name__} is deprecated: {reason}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func_or_class(*args, **kwargs)
        return wrapper
    return decorator



__version__: str

@deprecated("RSA is vulnerable to timing attacks. Use Ed25519 or Falcon instead.")
class Rsa:
    """
    ⚠️ Deprecated: RSA is vulnerable to timing attacks. Use Ed25519 or Falcon instead.
    """
    @staticmethod
    def generate_keypair(pk_size: int) -> Tuple[bytes, bytes, bytes]: ...
    @staticmethod
    def sign(data: bytes, signing_key_pem: bytes) -> bytes: ...
    @staticmethod
    def verify(data: bytes, signature: bytes, verifying_key_pem: bytes) -> bool: ...


class Ed25519:
    @staticmethod
    def generate_keypair() -> Tuple[bytes, bytes]: ...
    @staticmethod
    def sign(message: bytes, signing_key_bytes: bytes) -> bytes: ...
    @staticmethod
    def verify(message: bytes, signature_bytes: bytes, verifying_key_bytes: bytes) -> bool: ...


class Falcon512:
    @staticmethod
    def generate_keypair() -> Tuple[bytes, bytes]: ...
    @staticmethod
    def sign(message: bytes, signing_key_bytes: bytes) -> bytes: ...
    @staticmethod
    def verify(message: bytes, signature_bytes: bytes, public_key_bytes: bytes) -> bool: ...


class Falcon1024:
    @staticmethod
    def generate_keypair() -> Tuple[bytes, bytes]: ...
    @staticmethod
    def sign(message: bytes, signing_key_bytes: bytes) -> bytes: ...
    @staticmethod
    def verify(message: bytes, signature_bytes: bytes, public_key_bytes: bytes) -> bool: ...


