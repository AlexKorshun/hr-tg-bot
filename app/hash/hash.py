import hashlib
import hmac
import os

SALT = os.getenv("HASH_SALT", "static_salt_for_demo").encode() # TODO: убрать хеш в env

def hash_string(value: str) -> str:
    return hmac.new(SALT, value.encode(), hashlib.sha256).hexdigest()

def verify_string(value: str, hashed: str) -> bool:
    expected = hash_string(value)
    return hmac.compare_digest(expected, hashed)
