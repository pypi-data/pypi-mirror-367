from ..utils import partition_text_to_blocks, xor_bytes
from ..cipher import encrypt_block


# for Counter mode, it is the same operation for encryption and decryption
def ctr_iterate(text: bytes, key: bytes, iv: bytes) -> bytes:
    assert len(key) == 64, "Key length must be 512 bits."
    assert len(iv)  == 64, "IV length must be 512 bits."
    
    out = b""
    
    counter = int.from_bytes(iv)
    for block in partition_text_to_blocks(text, assert_blocks=False):
        counter_block = encrypt_block(counter.to_bytes(64), key)
        out += xor_bytes(block, counter_block[:len(block)])
        counter += 1
            
    return out


def ctr_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    return ctr_iterate(plaintext, key, iv)


def ctr_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    return ctr_iterate(ciphertext, key, iv)
