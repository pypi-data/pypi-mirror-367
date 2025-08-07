

def is_gzipped(data: bytes) -> bool:
    return data[:2] == b'\x1f\x8b'