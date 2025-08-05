import numpy as np
import random
from rijndael3d.block import block_from_bytes


def get_random_block():
    """Gets a randomized block using the `random` module. Used for testing.

    Returns:
        np.ndarray: A block that contains random elements.
    """
    return block_from_bytes(b"".join([random.randint(0, 255).to_bytes(1) for _ in range(64)]))


def xy_layered_repr(block: np.ndarray) -> str:
    int_block = np.ndarray(dtype=np.uint8, shape=(4, 4, 4))
    for loc, byte in np.ndenumerate(block):
        # loc for location, in format x,y,z
        int_block[loc[2]][loc[0]][loc[1]] = byte  # convert to to view layers in the wanted plane 
    return int_block.__str__()


def xz_layered_repr(block: np.ndarray) -> str:
    int_block = np.ndarray(dtype=np.uint8, shape=(4, 4, 4))
    for loc, byte in np.ndenumerate(block):
        # loc for location, in format x,y,z
        int_block[loc[1]][loc[0]][loc[2]] = byte  # convert to to view layers in the wanted plane
    return int_block.__str__()


def yz_layered_repr(block: np.ndarray) -> str:
    int_block = np.ndarray(dtype=np.uint8, shape=(4, 4, 4))
    for loc, byte in np.ndenumerate(block):
        # loc for location, in format x,y,z
        int_block[loc] = byte  # convert to to view layers in the wanted plane 
    return int_block.__str__()