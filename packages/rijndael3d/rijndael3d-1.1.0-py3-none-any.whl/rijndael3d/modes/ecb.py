from ..cipher import encrypt_block, decrypt_block
from ..utils import partition_text_to_blocks


def ecb_encrypt(plaintext: bytes, key: bytes) -> bytes:
    assert len(key) == 64, "Key length must be 512 bits."
    assert len(plaintext)%64 == 0, "Data must be padded to 64 byte boundary in ECB mode"
    
    ciphertext = b""
    for block in partition_text_to_blocks(plaintext):
        ciphertext += encrypt_block(block, key)
    
    return ciphertext


def ecb_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    assert len(key) == 64, "Key length must be 512 bits."
    assert len(ciphertext)%64 == 0, "Data must be padded to 64 byte boundary in ECB mode"

    plaintext = b""
    for block in partition_text_to_blocks(ciphertext):
        plaintext += decrypt_block(block, key)
         
    return plaintext
