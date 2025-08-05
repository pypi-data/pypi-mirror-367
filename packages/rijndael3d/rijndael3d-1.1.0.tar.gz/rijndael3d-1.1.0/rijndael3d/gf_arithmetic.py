import numpy as np
from numba import jit, int32


empty_layer = np.ndarray(dtype=np.uint8, shape=(4, 4))


@jit(int32(int32, int32))
def gf_multiply(a: int, b: int) -> int:
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        a <<= 1
        if a >= 0x100:  # Check if overflow occurred
            a ^= 0x11d  # XOR with the irreducible polynomial
        b >>= 1
    return p


@jit()
def get_single_element_in_matrix_mult(mat1: np.ndarray, mat2: np.ndarray, i: int, j: int) -> int:
    return gf_multiply(mat1[i][0], mat2[0][j]) ^ \
           gf_multiply(mat1[i][1], mat2[1][j]) ^ \
           gf_multiply(mat1[i][2], mat2[2][j]) ^ \
           gf_multiply(mat1[i][3], mat2[3][j])
    

@jit()
def multiply_mats(mat1: np.ndarray, mat2: np.ndarray) -> np.ndarray:
    assert mat1.shape == mat2.shape == (4, 4)
    mat_out = empty_layer.copy()  # we can't use jit with np.ndarray(..) directly because it has problems with Numba
    
    for (i, j), _ in np.ndenumerate(mat_out):
        mat_out[i][j] = get_single_element_in_matrix_mult(mat1, mat2, i, j)
    
    return mat_out


# here we don't use jit because numba doesn't support the features used in this function
def gf_2_512_multiply_bytes(b1: bytes, b2: bytes) -> bytes:
    a = int.from_bytes(b1)
    b = int.from_bytes(b2)

    # Irreducible Polynomial: x^512 + x^8 + x^5 + x^2 + 1
    irreducible_poly = (1 << 512) | (1 << 8) | (1 << 5) | (1 << 2) | 1

    p = 0
    for _ in range(512):
        if b & 1:
            p ^= a
        a <<= 1
        if a & (1 << 512):
            a ^= irreducible_poly
        b >>= 1
    return p.to_bytes(64)
