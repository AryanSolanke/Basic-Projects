"""Core pure operations for the programmer calculator."""

from __future__ import annotations

from enum import IntEnum

from calculator.exceptions import ConversionError, InvalidBaseError, InvalidBitShiftError, InvalidInputError, NullInputError


class WordSize(IntEnum):
    """Supported word sizes (bit widths)."""

    BYTE = 8
    WORD = 16
    DWORD = 32
    QWORD = 64


WORD_SIZE_CYCLE = [WordSize.QWORD, WordSize.DWORD, WordSize.WORD, WordSize.BYTE]
WORD_SIZE_LABELS = {
    WordSize.QWORD: "QWORD (64-bit)",
    WordSize.DWORD: "DWORD (32-bit)",
    WordSize.WORD: "WORD  (16-bit)",
    WordSize.BYTE: "BYTE  ( 8-bit)",
}


def unsigned_mask(value: int, word_size: WordSize) -> int:
    bits = int(word_size)
    return value & ((1 << bits) - 1)


def mask(value: int, word_size: WordSize) -> int:
    bits = int(word_size)
    unsigned = unsigned_mask(value, word_size)
    if unsigned >= (1 << (bits - 1)):
        return unsigned - (1 << bits)
    return unsigned


def parse_int(raw: str) -> int:
    raw = raw.strip()
    if not raw:
        raise NullInputError()
    try:
        return int(raw, 0)
    except ValueError:
        try:
            return int(raw, 16)
        except ValueError:
            raise InvalidBaseError(f"\nBase Error: Cannot parse '{raw}' as a valid number.\n")


def dec_to_hex(n: int, word_size: WordSize) -> str:
    if n < 0:
        n = unsigned_mask(n, word_size)
    return hex(n)[2:].upper()


def dec_to_bin(n: int, word_size: WordSize) -> str:
    bits = int(word_size)
    n = unsigned_mask(n, word_size)
    raw = bin(n)[2:]
    padded = raw.zfill(bits)
    groups = [padded[i : i + 4] for i in range(0, len(padded), 4)]
    return " ".join(groups)


def dec_to_oct(n: int, word_size: WordSize) -> str:
    n = unsigned_mask(n, word_size)
    return oct(n)[2:]


def hex_to_dec(s: str, word_size: WordSize) -> int:
    s = s.strip()
    if not s:
        raise NullInputError()
    try:
        return mask(int(s, 16), word_size)
    except ValueError:
        raise ConversionError(f"\nConversion Error: '{s}' is not a valid hexadecimal number.\n")


def bin_to_dec(s: str, word_size: WordSize) -> int:
    s = s.replace(" ", "").strip()
    if not s:
        raise NullInputError()
    try:
        return mask(int(s, 2), word_size)
    except ValueError:
        raise ConversionError(f"\nConversion Error: '{s}' is not a valid binary number.\n")


def oct_to_dec(s: str, word_size: WordSize) -> int:
    s = s.strip()
    if not s:
        raise NullInputError()
    try:
        return mask(int(s, 8), word_size)
    except ValueError:
        raise ConversionError(f"\nConversion Error: '{s}' is not a valid octal number.\n")


def bitwise_and(a: int, b: int, word_size: WordSize) -> int:
    return mask(a & b, word_size)


def bitwise_or(a: int, b: int, word_size: WordSize) -> int:
    return mask(a | b, word_size)


def bitwise_xor(a: int, b: int, word_size: WordSize) -> int:
    return mask(a ^ b, word_size)


def bitwise_not(a: int, word_size: WordSize) -> int:
    return mask(~a, word_size)


def shift_arithmetic_left(value: int, n: int, word_size: WordSize) -> int:
    if n < 0:
        raise InvalidBitShiftError("\nShift Error: Shift amount cannot be negative.\n")
    return mask(value << n, word_size)


def shift_arithmetic_right(value: int, n: int, word_size: WordSize) -> int:
    if n < 0:
        raise InvalidBitShiftError("\nShift Error: Shift amount cannot be negative.\n")
    return mask(mask(value, word_size) >> n, word_size)


def shift_logical_left(value: int, n: int, word_size: WordSize) -> int:
    if n < 0:
        raise InvalidBitShiftError("\nShift Error: Shift amount cannot be negative.\n")
    return mask(unsigned_mask(value, word_size) << n, word_size)


def shift_logical_right(value: int, n: int, word_size: WordSize) -> int:
    if n < 0:
        raise InvalidBitShiftError("\nShift Error: Shift amount cannot be negative.\n")
    return mask(unsigned_mask(value, word_size) >> n, word_size)


def rotate_left(value: int, n: int, word_size: WordSize) -> int:
    if n < 0:
        raise InvalidBitShiftError("\nShift Error: Rotation amount cannot be negative.\n")
    bits = int(word_size)
    n %= bits
    u = unsigned_mask(value, word_size)
    rotated = ((u << n) | (u >> (bits - n))) & ((1 << bits) - 1)
    return mask(rotated, word_size)


def rotate_right(value: int, n: int, word_size: WordSize) -> int:
    if n < 0:
        raise InvalidBitShiftError("\nShift Error: Rotation amount cannot be negative.\n")
    bits = int(word_size)
    n %= bits
    u = unsigned_mask(value, word_size)
    rotated = ((u >> n) | (u << (bits - n))) & ((1 << bits) - 1)
    return mask(rotated, word_size)


def rotate_left_carry(value: int, n: int, carry: int, word_size: WordSize) -> tuple[int, int]:
    if n < 0:
        raise InvalidBitShiftError("\nShift Error: Rotation amount cannot be negative.\n")
    if carry not in (0, 1):
        raise InvalidInputError("\nInput Error: Carry flag must be 0 or 1.\n")
    bits = int(word_size)
    n %= bits + 1
    extended = (unsigned_mask(value, word_size) << 1) | carry
    for _ in range(n):
        msb = (extended >> bits) & 1
        extended = ((extended << 1) & ((1 << (bits + 1)) - 1)) | msb
    result = (extended >> 1) & ((1 << bits) - 1)
    return mask(result, word_size), extended & 1


def rotate_right_carry(value: int, n: int, carry: int, word_size: WordSize) -> tuple[int, int]:
    if n < 0:
        raise InvalidBitShiftError("\nShift Error: Rotation amount cannot be negative.\n")
    if carry not in (0, 1):
        raise InvalidInputError("\nInput Error: Carry flag must be 0 or 1.\n")
    bits = int(word_size)
    n %= bits + 1
    extended = (unsigned_mask(value, word_size) << 1) | carry
    for _ in range(n):
        lsb = extended & 1
        extended = (extended >> 1) | (lsb << bits)
    result = (extended >> 1) & ((1 << bits) - 1)
    return mask(result, word_size), extended & 1

