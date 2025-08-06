import ctypes
import os

# Load grain128a shared lib
_lib_path = os.path.join(os.path.dirname(__file__), "native", "grain128a.dll")
grain128a = ctypes.CDLL(_lib_path)

# Define function prototypes according to grain128a API
# (You need to adjust according to the actual C API)

def grain128a_encrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    out = (ctypes.c_ubyte * len(data))()
    grain128a.grain128a_encrypt(
        ctypes.c_char_p(key),
        ctypes.c_char_p(iv),
        ctypes.c_char_p(data),
        ctypes.c_int(len(data)),
        out
    )
    return bytes(out)

def grain128a_decrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    # Grain128a is a stream cipher, encryption = decryption
    return grain128a_encrypt(key, iv, data)