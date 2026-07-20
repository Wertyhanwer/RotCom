from argon2.exceptions import VerifyMismatchError

from .hash_settings import password_hasher

def verify_hash(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False

