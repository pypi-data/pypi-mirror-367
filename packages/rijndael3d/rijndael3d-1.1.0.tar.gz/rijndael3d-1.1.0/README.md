# Rijndael3D
Rijndael3D is my work-in-progress extension of the Rijndael cipher that works in 512-bit 4x4x4 blocks of bytes. This module uses new layer-based permutation algorithms together with modified versions of regular Rijndael components to utilize the 3 dimensional structure of blocks.
This module is programmed in pure Python, it implements finite-field arithmetic in GF(2<sup>8</sup>) and is boosted by the [`numba`](https://numba.pydata.org/) module internally.

## Cipher Specifications
- Key size: 512 bits
- Block size: 512 bits
- Number of rounds: 16 rounds
- Structure: substitution–permutation network
- Padding method: pseudo-randomized (seeded) padding using the SHA512 of the key.
- Supported modes: the current version of Rijndael3D supports the following modes; `ECB`, `CBC`, and `CTR`. `GCM` is planned to be added.

## Disclaimer
This module was built as a fun project to learn cryptography and cryptanalysis. It is not designed to withstand side channel attacks or other advanced cryptanalysis techniques.

## Installation
This module is available only on PyPI, installation via pip:
```
pip install rijndael3d
```

## Basic Usage
Because the block size is 512 bits, the keys and initialization vectors must all be in the matching size of 512 bits.

The basic usage of this module is as follows (CTR mode for example):

Importing the appropriate functions:
```
from rijndael3d.modes.ctr import ctr_encrypt, ctr_decrypt
```

Encrypting:
```
encrypted = ctr_encrypt(plaintext, key, iv)
```

Decrypting:
```
decrypted = ctr_decrypt(ciphertext, key, iv)
```

## Advanced Usage
If you want to utilize the internal functions of this module or take a closer look at them, this is the section for you. 

The functionality of this module are segmented into the appropriate files and directory:
- `block.py`:            All internal block manipulation functions.
- `cipher.py`:           Round performing and single block encryption/decryption.
- `constants.py`:        Contains all the constants used.
- `debug_operations.py`: Debug-related functions, not used in normal usage of the module.
- `gf_arithmetic.py`:    The implementation for GF(2<sup>8</sup>) arithmetic.
- `key_schedule.py`:     The key scheduling algorithm.
- `padding.py`:          The padding mechanism.
- `utils.py`:            Utility functions.
- The `modes` directory that contains the code for each mode of operation.
