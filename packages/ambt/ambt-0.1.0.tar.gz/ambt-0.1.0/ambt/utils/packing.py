from ambt.utils.typing import anyType, any_to_str, any_to_bytes
import struct

packingTypeStr: bool = True 
packingWidth: int = 64
_packingTransform = lambda x: any_to_str(x) if packingTypeStr else any_to_bytes(x)

def flat(payload: list[anyType]) -> str|bytes:
    data = _packingTransform(b"")

    for p in payload:
        if type(p) == int or type(p) == float:
            data += pack(int(p), word_size=packingWidth) 
        elif type(p) == str or type(p) == bytes:
            data += _packingTransform(p)
        else:
            raise Exception(f"[AmbtPacking] Unknown element type {type(p)}")

    return data


def _formatHelper(endianness: str, sign: bool, fchar: str) -> str:
    format = ''
    if endianness == 'little':
        format += '<'
    elif endianness == 'big':
        format += '>'
    else:
        raise Exception(f"[AmbtPacking] Unknown endianness {endianness}")

    format += fchar if sign else fchar.upper()
    return format

def _packingHelper(number: int, endianness: str, sign: bool, fchar: str) -> str|bytes:
    format = _formatHelper(endianness, sign, fchar) 
    return _packingTransform(struct.pack(format, number))

def pack(number: int, word_size: int = 64, endianness: str = 'little', sign: bool = False) -> str|bytes:
    data = _packingTransform(b"")

    if word_size % 8 != 0:
        raise Exception(f"[AmbtPacking] Invalid word size {word_size}")
   
    if sign or number < 0:
        number = (2**word_size + number) & (2**word_size-1)

    while word_size > 0:
        data += p8(number % 0x100)   
        number //= 0x100
        word_size -= 8

    if endianness == 'little':
        return data
    elif endianness == 'big':
        return data[::-1]
    else:
        raise Exception(f"[AmbtPacking] Unknown endianness {endianness}")

def p8(number: int, endianness: str = 'little', sign: bool = False) -> str|bytes:
    return _packingHelper(number, endianness, sign, "b")

def p16(number: int, endianness: str = 'little', sign: bool = False) -> str|bytes:
    return _packingHelper(number, endianness, sign, "h")

def p32(number: int, endianness: str = 'little', sign: bool = False) -> str|bytes:
    return _packingHelper(number, endianness, sign, "i")

def p64(number: int, endianness: str = 'little', sign: bool = False) -> str|bytes:
    return _packingHelper(number, endianness, sign, "q")


def _unpackingHelper(data: str|bytes, endianness: str, sign: bool, fchar: str) -> int:
    format = _formatHelper(endianness, sign, fchar) 
    return struct.unpack(format, any_to_bytes(data))[0]

def unpack(data: str|bytes, word_size: int = 64, endianness: str = 'little', sign: bool = False) -> int:
    number: int = 0

    if word_size % 8 != 0:
        raise Exception(f"[AmbtPacking] Invalid word size {word_size}")

    if endianness == 'little':
        data = any_to_bytes(data)[::-1] 
    elif endianness == 'big':
        data = any_to_bytes(data)
    else:
        raise Exception(f"[AmbtPacking] Unknown endianness {endianness}")

    for n in data:
        number *= 0x100
        number += u8(bytes([n]))

    if sign:
        number = -(2**word_size - number) if number >= 2**(word_size-1) else number

    return number

def u8(data: str|bytes, endianness: str = 'little', sign: bool = False) -> int:
    return _unpackingHelper(data, endianness, sign, "b")

def u16(data: str|bytes, endianness: str = 'little', sign: bool = False) -> int:
    return _unpackingHelper(data, endianness, sign, "h")

def u32(data: str|bytes, endianness: str = 'little', sign: bool = False) -> int:
    return _unpackingHelper(data, endianness, sign, "i")

def u64(data: str|bytes, endianness: str = 'little', sign: bool = False) -> int:
    return _unpackingHelper(data, endianness, sign, "q")

