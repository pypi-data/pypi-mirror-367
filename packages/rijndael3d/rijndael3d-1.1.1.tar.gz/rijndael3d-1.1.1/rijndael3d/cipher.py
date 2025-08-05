import numpy as np
from numba import jit
from .block import sub_bytes, shift_rows, mix_xy_columns, rotate_elements, mix_xz_columns, spin_rings, \
    mix_yz_columns, add_round_key, inverse_mix_xy_columns, inverse_mix_xz_columns, inverse_mix_yz_columns, \
    inverse_rotate_elements, inverse_shift_rows, inverse_spin_rings, inverse_sub_bytes, block_from_bytes, export_to_bytes
from .key_schedule import generate_round_keys


@jit(nopython=True, nogil=True, cache=True)
def perform_round(block: np.ndarray, round_key: np.ndarray) -> None:
    sub_bytes(block)
    
    shift_rows(block)
    mix_xy_columns(block)
    
    rotate_elements(block)
    mix_xz_columns(block)
    
    spin_rings(block)
    mix_yz_columns(block)
    
    add_round_key(block, round_key)


@jit(nopython=True, nogil=True, cache=True)
def perform_inverse_round(block: np.ndarray, round_key: np.ndarray) -> None:
    add_round_key(block, round_key)

    inverse_mix_yz_columns(block)
    inverse_spin_rings(block)
    
    inverse_mix_xz_columns(block)
    inverse_rotate_elements(block)
    
    inverse_mix_xy_columns(block)
    inverse_shift_rows(block)
    
    inverse_sub_bytes(block)


def encrypt_block(plaintext: bytes, key: bytes) -> bytes:
    block = block_from_bytes(plaintext)
    round_keys = generate_round_keys(key)
    for round_key in round_keys:
        perform_round(block, round_key)
    return export_to_bytes(block)


def decrypt_block(ciphertext: bytes, key: bytes) -> bytes:
    block = block_from_bytes(ciphertext)
    round_keys = generate_round_keys(key)
    for round_key in reversed(round_keys):
        perform_inverse_round(block, round_key)
    return export_to_bytes(block)
