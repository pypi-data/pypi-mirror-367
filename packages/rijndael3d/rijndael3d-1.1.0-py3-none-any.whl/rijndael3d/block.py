import numpy as np
from .constants import S_BOX, INVERSE_S_BOX, XY_MULT_MATRIX, INVERSE_XY_MULT_MATRIX, XZ_MULT_MATRIX, \
    INVERSE_XZ_MULT_MATRIX, YZ_MULT_MATRIX, INVERSE_YZ_MULT_MATRIX
from .gf_arithmetic import multiply_mats
from numba import jit


EMPTY_BLOCK = np.ndarray(dtype=np.uint8, shape=(64, 1, 1))


@jit(nopython=True, nogil=True, cache=True)
def block_from_bytes(source_bytes: bytes) -> np.ndarray:
    assert len(source_bytes) == 64, "Source bytes must be of length 64."
    byte_block = EMPTY_BLOCK.copy()

    for i in range(64):
        byte_block[i] = source_bytes[i]
    
    return byte_block.reshape((4, 4, 4))


def export_to_bytes(block: np.ndarray) -> bytes:
    return b"".join(block.reshape((64, 1, 1)))
    

@jit(nopython=True, nogil=True, cache=True)
def shift_rows(block: np.ndarray) -> None:  # XY layer permutation
    for z in range(0, 4):
        block[1][0][z], block[1][1][z], block[1][2][z], block[1][3][z] = \
            block[1][1][z], block[1][2][z], block[1][3][z], block[1][0][z]  # row 2
        block[2][0][z], block[2][1][z], block[2][2][z], block[2][3][z] = \
            block[2][2][z], block[2][3][z], block[2][0][z], block[2][1][z]  # row 3
        block[3][0][z], block[3][1][z], block[3][2][z], block[3][3][z] = \
            block[3][3][z], block[3][0][z], block[3][1][z], block[3][2][z]  # row 4


@jit(nopython=True, nogil=True, cache=True)
def inverse_shift_rows(block: np.ndarray) -> None:  # XY layer permutation
    for z in range(0, 4):
        block[1][0][z], block[1][1][z], block[1][2][z], block[1][3][z] = \
            block[1][3][z], block[1][0][z], block[1][1][z], block[1][2][z]  # row 2
        block[2][0][z], block[2][1][z], block[2][2][z], block[2][3][z] = \
            block[2][2][z], block[2][3][z], block[2][0][z], block[2][1][z]  # row 3
        block[3][0][z], block[3][1][z], block[3][2][z], block[3][3][z] = \
            block[3][1][z], block[3][2][z], block[3][3][z], block[3][0][z]  # row 4


@jit(nopython=True, nogil=True, cache=True)
def rotate_elements(block: np.ndarray) -> None:  # XZ layer permutation
    for y in range(0, 4):
        block[0][y][1], block[0][y][3], block[2][y][3], block[2][y][1] = \
            block[2][y][1], block[0][y][1], block[0][y][3], block[2][y][3]  # group 2
        block[1][y][1], block[1][y][3], block[3][y][3], block[3][y][1] = \
            block[3][y][3], block[3][y][1], block[1][y][1], block[1][y][3]  # group 3
        block[1][y][0], block[1][y][2], block[3][y][2], block[3][y][0] = \
            block[1][y][2], block[3][y][2], block[3][y][0], block[1][y][0]  # group 4


@jit(nopython=True, nogil=True, cache=True)
def inverse_rotate_elements(block: np.ndarray) -> None:  # XZ layer permutation
    for y in range(0, 4):
        block[0][y][1], block[0][y][3], block[2][y][3], block[2][y][1] = \
            block[0][y][3], block[2][y][3], block[2][y][1], block[0][y][1]  # group 2
        block[1][y][1], block[1][y][3], block[3][y][3], block[3][y][1] = \
            block[3][y][3], block[3][y][1], block[1][y][1], block[1][y][3]  # group 3
        block[1][y][0], block[1][y][2], block[3][y][2], block[3][y][0] = \
            block[3][y][0], block[1][y][0], block[1][y][2], block[3][y][2]  # group 4


@jit(nopython=True, nogil=True, cache=True)
def spin_rings(block: np.ndarray) -> None:  # YZ layer permutation
    for x in range(0, 4):
        block[x][1][2], block[x][2][1] = block[x][2][1], block[x][1][2]  # ring 2
        block[x][1][1], block[x][2][2] = block[x][2][2], block[x][1][1]  # ring 3
        block[x][0][0], block[x][0][3], block[x][3][0], block[x][3][3] = \
            block[x][0][3], block[x][3][3], block[x][0][0], block[x][3][0]  # ring 1
        block[x][0][2], block[x][2][3], block[x][3][1], block[x][1][0] = \
            block[x][1][0], block[x][0][2], block[x][2][3], block[x][3][1]  # ring 4
        block[x][0][1], block[x][1][3], block[x][3][2], block[x][2][0] = \
            block[x][2][0], block[x][0][1], block[x][1][3], block[x][3][2]  # ring 5
        

@jit(nopython=True, nogil=True, cache=True)
def inverse_spin_rings(block: np.ndarray) -> None:
    for x in range(0, 4):
        block[x][1][2], block[x][2][1] = block[x][2][1], block[x][1][2]  # ring 2
        block[x][1][1], block[x][2][2] = block[x][2][2], block[x][1][1]  # ring 3
        block[x][0][0], block[x][0][3], block[x][3][0], block[x][3][3] = \
            block[x][3][0], block[x][0][0], block[x][3][3], block[x][0][3]  # ring 1
        block[x][0][2], block[x][2][3], block[x][3][1], block[x][1][0] = \
            block[x][2][3], block[x][3][1], block[x][1][0], block[x][0][2]  # ring 4
        block[x][0][1], block[x][1][3], block[x][3][2], block[x][2][0] = \
            block[x][1][3], block[x][3][2], block[x][2][0], block[x][0][1]  # ring 5


@jit(nopython=True, nogil=True, cache=True)
def sub_bytes(block: np.ndarray) -> None:
    for loc, byte in np.ndenumerate(block):
        block[loc] = S_BOX[byte]


@jit(nopython=True, nogil=True, cache=True)
def inverse_sub_bytes(block: np.ndarray) -> None:
    for loc, byte in np.ndenumerate(block):
        block[loc] = INVERSE_S_BOX[byte]


@jit(nopython=True, nogil=True, cache=True)
def mix_xy_columns(block: np.ndarray) -> None:
    for z in range(0, 4):
        block[slice(0, 4)][slice(0, 4)][z] = \
            multiply_mats(XY_MULT_MATRIX, block[slice(0, 4)][slice(0, 4)][z])


@jit(nopython=True, nogil=True, cache=True)
def inverse_mix_xy_columns(block: np.ndarray) -> None:
    for z in range(0, 4):
        block[slice(0, 4)][slice(0, 4)][z] = \
            multiply_mats(INVERSE_XY_MULT_MATRIX , block[slice(0, 4)][slice(0, 4)][z])


@jit(nopython=True, nogil=True, cache=True)
def mix_xz_columns(block: np.ndarray) -> None:
    for y in range(0, 4):
        block[slice(0, 4)][y][slice(0, 4)] = \
            multiply_mats(XZ_MULT_MATRIX, block[slice(0, 4)][y][slice(0, 4)])


@jit(nopython=True, nogil=True, cache=True)
def inverse_mix_xz_columns(block: np.ndarray) -> None:
    for y in range(0, 4):
        block[slice(0, 4)][y][slice(0, 4)] = \
            multiply_mats(INVERSE_XZ_MULT_MATRIX, block[slice(0, 4)][y][slice(0, 4)])


@jit(nopython=True, nogil=True, cache=True)
def mix_yz_columns(block: np.ndarray) -> None:
    for x in range(0, 4):
        block[x][slice(0, 4)][slice(0, 4)] = \
            multiply_mats(YZ_MULT_MATRIX, block[x][slice(0, 4)][slice(0, 4)])


@jit(nopython=True, nogil=True, cache=True)
def inverse_mix_yz_columns(block: np.ndarray) -> None:
    for x in range(0, 4):
        block[x][slice(0, 4)][slice(0, 4)] = \
            multiply_mats(INVERSE_YZ_MULT_MATRIX, block[x][slice(0, 4)][slice(0, 4)])
    
    
@jit(nopython=True, nogil=True, cache=True)
def add_round_key(block, round_key: np.ndarray) -> None:
    block ^= round_key
