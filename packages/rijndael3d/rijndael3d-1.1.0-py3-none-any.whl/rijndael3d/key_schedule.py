from .constants import R_CON, S_BOX
import numpy as np


def key_to_word_group(key: bytes) -> np.ndarray:
    if not len(key) == 64:
        raise ValueError(f"Keys are of length 64 bytes (512 bits) only, supplied length of {len(key)}")
                
    return np.frombuffer(key, dtype=np.uint8).reshape((16, 4))


def g_function(word: np.ndarray, round: int) -> np.ndarray:
    # circular shift by one byte to left
    first = word[0]
    word = np.delete(word, 0)
    word = np.append(word, first)
    
    # s box
    for loc, byte in np.ndenumerate(word):
        word[loc] = S_BOX[byte]
    
    # r consts
    word = word ^ (R_CON[round-1], 0, 0, 0)
    
    return word


def get_next_word_group(curr_word_group: np.ndarray, round: int) -> np.ndarray:
    if not len(curr_word_group) == 16:
        raise ValueError(f"Word groups are of length 16 words, supplied length of {len(curr_word_group)} words.")
    
    next_word_group = np.ndarray(dtype=np.uint8, shape=(16, 4))
    
    g_word = g_function(curr_word_group[-1], round)
    
    next_word_group[0] = g_word ^ curr_word_group[0]
    
    for i in range(1, 16):
        next_word_group[i] = next_word_group[i-1] ^ curr_word_group[i]
    
    return next_word_group


def generate_round_keys(initial_key: bytes):
    word_groups = np.ndarray(dtype=np.uint8, shape=(16, 16, 4))
    word_groups[0] = key_to_word_group(initial_key)
    for i in range(1, 16):
        word_groups[i] = get_next_word_group(word_groups[i-1], i)

    keys = np.ndarray(dtype=np.uint8, shape=(16, 4, 4, 4))
    for i in range(16):
        keys[i] = word_groups[i].reshape((4, 4, 4))
    
    return keys
