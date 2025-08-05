import random
from hashlib import sha512


def generate_suffix(length: int, key: bytes) -> bytes:
    # use the hash of the key so that even if the padding is found the key will not
    random.seed(sha512(key).hexdigest())  
    suffix = b"".join([random.randint(1, 255).to_bytes(1) for _ in range(length-1)])
    return b"\x00" + suffix


def pad(plaintext_bytes: bytes, key: bytes) -> bytes:
    suffix_len = 64 - (len(plaintext_bytes) % 64) if len(plaintext_bytes)%64 != 0 else 64
    padded = plaintext_bytes + generate_suffix(suffix_len, key)
    return padded


def unpad(plaintext_bytes: bytes) -> bytes:
    pad_start_index = plaintext_bytes.rfind(b"\x00", len(plaintext_bytes)-64)
    return plaintext_bytes[:pad_start_index]
