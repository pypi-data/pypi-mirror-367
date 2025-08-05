from hashlib import sha512
from .ctr import ctr_iterate
from ..cipher import encrypt_block
from ..gf_arithmetic import gf_2_512_multiply_bytes
from ..utils import partition_text_to_blocks, xor_bytes


def calculate_tag(ciphertext: bytes, key: bytes, iv: bytes, aad: bytes) -> bytes:
    h = encrypt_block(b"\x00"*64, key)
    
    # use the hash of the aad so it could be of arbitrary length
    prev_g = gf_2_512_multiply_bytes(sha512(aad).digest(), h)
    
    for block in partition_text_to_blocks(ciphertext):
        prev_g = gf_2_512_multiply_bytes(xor_bytes(prev_g, block), h)
    
    tag = xor_bytes(gf_2_512_multiply_bytes(prev_g, h), encrypt_block(iv, key))
    
    return tag


def gcm_encrypt(plaintext: bytes, key: bytes, iv: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
    ciphertext = ctr_iterate(plaintext, key, (int.from_bytes(iv)+1).to_bytes(64))
    
    return ciphertext, calculate_tag(ciphertext, key, iv, aad)


def gcm_decrypt(ciphertext: bytes, key: bytes, iv: bytes, tag: bytes, aad: bytes = b"") -> bytes:
    plaintext = ctr_iterate(ciphertext, key, (int.from_bytes(iv)+1).to_bytes(64))
    
    calculated_tag = calculate_tag(ciphertext, key, iv, aad)
    
    if tag != calculated_tag:
        raise ValueError("The tag that was received and the tag that was calculated are not the same."
                         "This points to an alteration of the data inputted between encryption and decryption.")
    
    return plaintext
    