from typing import Callable

anyToStrBytesType = Callable[[object], str] | Callable[[object], bytes]
anyType = str|bytes|int|float

def any_to_bytes(a: object) -> bytes:
    if type(a) == bytes:
        return a
    elif type(a) == str:
        return str_to_bytes(a)
    elif type(a) == int or type(a) == float:
        return num_to_bytes(a)
    else:
        raise Exception(f"[AmbtTyping] Unsupported type {type(a)} while converting to bytes")

def str_to_bytes(s: str) -> bytes:
    return bytes(map(ord, s))

def num_to_bytes(n: int|float) -> bytes:
    return bytes(map(ord, str(n)))


def any_to_str(a: object) -> str:
    if type(a) == str:
        return a
    elif type(a) == bytes:
        return bytes_to_str(a)
    elif type(a) == int or type(a) == float:
        return num_to_str(a)
    else:
        raise Exception(f"[AmbtTyping] Unsupported type {type(a)} while converting to str")

def bytes_to_str(b: bytes) -> str:
    return "".join(map(chr, b))

def num_to_str(n: int|float) -> str:
    return str(n)


def any_to_int(a: object) -> int:
    if type(a) == bytes:
        a = bytes_to_str(a)
    if type(a) == str:
        if a.lower().startswith("0b"):
            return int(a, 2)
        elif a.lower().startswith("0o"):
            return int(a,8)
        elif a.lower().startswith("0x"):
            return int(a, 16)
        else:
            return int(a)
    if type(a) == int:
        return a
    if type(a) == float:
        return int(a)
    else:
        raise Exception(f"[AmbtTyping] Unsupported type {type(a)} while converting to int")
