from .hash_settings import password_hasher


def hash_password(password: str)-> str:
    result_hash = password_hasher.hash(password)
    return result_hash

