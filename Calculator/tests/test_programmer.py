"""
Tests for the Programmer Calculator Module.

Covers:
- Word size toggling
- Bitwise operations (AND, OR, XOR, NOT, NAND, NOR, XNOR)
- Bit shifts (ASL, ASR, LSL, LSR, ROL, ROR, RCL, RCR)
- Base conversions (DEC ↔ HEX ↔ BIN ↔ OCT)

Run with:  python tests/test_programmer.py
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import calculator.programmer as prog

# ============================================================================
# Helpers
# ============================================================================

_PASS = 0
_FAIL = 0

def _check(name: str, got, expected) -> None:
    global _PASS, _FAIL
    if got == expected:
        _PASS += 1
    else:
        _FAIL += 1
        print(f"  FAIL  {name}")
        print(f"        got      = {got!r}")
        print(f"        expected = {expected!r}")


def _reset_word_size(ws: prog.WordSize) -> None:
    """Force the module word size to a specific value."""
    prog._word_size = ws


# ============================================================================
# Word Size Tests
# ============================================================================

def test_word_size_toggle() -> None:
    _reset_word_size(prog.WordSize.QWORD)
    _check("toggle QWORD->DWORD", prog.toggle_word_size(), prog.WordSize.DWORD)
    _check("toggle DWORD->WORD",  prog.toggle_word_size(), prog.WordSize.WORD)
    _check("toggle WORD->BYTE",   prog.toggle_word_size(), prog.WordSize.BYTE)
    _check("toggle BYTE->QWORD",  prog.toggle_word_size(), prog.WordSize.QWORD)
    _reset_word_size(prog.WordSize.QWORD)


def test_word_size_setter() -> None:
    _check("set word size to BYTE", prog.set_word_size(prog.WordSize.BYTE), prog.WordSize.BYTE)
    _check("getter returns BYTE", prog.get_word_size(), prog.WordSize.BYTE)
    _reset_word_size(prog.WordSize.QWORD)


# ============================================================================
# Mask / Signed Wrapping Tests
# ============================================================================

def test_mask_byte() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    _check("BYTE mask 255 => -1 signed",  prog._mask(255), -1)
    _check("BYTE mask 128 => -128 signed", prog._mask(128), -128)
    _check("BYTE mask 127 => 127 signed",  prog._mask(127), 127)
    _reset_word_size(prog.WordSize.QWORD)


def test_unsigned_mask_byte() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    _check("BYTE unsigned mask 256 => 0",   prog._unsigned_mask(256), 0)
    _check("BYTE unsigned mask -1 => 255",  prog._unsigned_mask(-1), 255)
    _reset_word_size(prog.WordSize.QWORD)


# ============================================================================
# Base Conversion Tests
# ============================================================================

def test_dec_to_hex() -> None:
    _reset_word_size(prog.WordSize.QWORD)
    _check("255 -> FF",       prog.dec_to_hex(255), "FF")
    _check("0 -> 0",          prog.dec_to_hex(0),   "0")
    _check("16 -> 10",        prog.dec_to_hex(16),  "10")
    _check("4096 -> 1000",    prog.dec_to_hex(4096), "1000")


def test_dec_to_oct() -> None:
    _reset_word_size(prog.WordSize.QWORD)
    _check("8 -> 10",   prog.dec_to_oct(8),  "10")
    _check("255 -> 377", prog.dec_to_oct(255), "377")
    _check("0 -> 0",    prog.dec_to_oct(0),  "0")


def test_dec_to_bin() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    result = prog.dec_to_bin(255)
    _check("BYTE 255 -> 1111 1111", result, "1111 1111")
    result_zero = prog.dec_to_bin(0)
    _check("BYTE 0 -> 0000 0000", result_zero, "0000 0000")
    _reset_word_size(prog.WordSize.QWORD)


def test_show_all_bases_map() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    bases = prog.show_all_bases_map(255)
    _check("bases map DEC", bases["DEC"], "255")
    _check("bases map HEX", bases["HEX"], "FF")
    _check("bases map BIN", bases["BIN"], "1111 1111")
    _check("bases map OCT", bases["OCT"], "377")
    _reset_word_size(prog.WordSize.QWORD)


def test_hex_to_dec() -> None:
    _reset_word_size(prog.WordSize.QWORD)
    _check("FF -> 255", prog.hex_to_dec("FF"),  255)
    _check("10 -> 16",  prog.hex_to_dec("10"),  16)
    _check("0 -> 0",    prog.hex_to_dec("0"),   0)


def test_bin_to_dec() -> None:
    _reset_word_size(prog.WordSize.QWORD)
    _check("11111111 -> 255", prog.bin_to_dec("11111111"), 255)
    _check("1010 -> 10",      prog.bin_to_dec("1010"),     10)
    _check("0 -> 0",          prog.bin_to_dec("0"),        0)


def test_oct_to_dec() -> None:
    _reset_word_size(prog.WordSize.QWORD)
    _check("10 -> 8",   prog.oct_to_dec("10"),  8)
    _check("377 -> 255", prog.oct_to_dec("377"), 255)
    _check("0 -> 0",    prog.oct_to_dec("0"),   0)


def test_bidirectional_conversions() -> None:
    """Round-trip: DEC→HEX→DEC, DEC→OCT→DEC, DEC→BIN→DEC."""
    _reset_word_size(prog.WordSize.QWORD)
    for n in [0, 1, 10, 127, 255, 1000, 65535]:
        h = prog.dec_to_hex(n)
        _check(f"round-trip HEX {n}", prog.hex_to_dec(h), n)

        o = prog.dec_to_oct(n)
        _check(f"round-trip OCT {n}", prog.oct_to_dec(o), n)

    _reset_word_size(prog.WordSize.BYTE)
    for n in [0, 1, 10, 100, 127]:
        b = prog.dec_to_bin(n).replace(" ", "")
        _check(f"round-trip BIN BYTE {n}", prog.bin_to_dec(b), n)
    _reset_word_size(prog.WordSize.QWORD)


def test_cross_base_conversions() -> None:
    """HEX→BIN, HEX→OCT, BIN→HEX, BIN→OCT, OCT→HEX, OCT→BIN."""
    _reset_word_size(prog.WordSize.QWORD)
    _check("FF hex->oct",  prog.hex_to_oct("FF"),  "377")
    _check("377 oct->hex", prog.oct_to_hex("377"), "FF")
    _check("11111111 bin->hex", prog.bin_to_hex("11111111"), "FF")
    _check("FF hex->bin includes 1s", "1" in prog.hex_to_bin("FF"), True)


# ============================================================================
# Bitwise Operation Tests
# ============================================================================

def test_bitwise_and() -> None:
    _reset_word_size(prog.WordSize.QWORD)
    _check("12 AND 10 = 8",  prog.bitwise_and(12, 10), 8)
    _check("0 AND 255 = 0",  prog.bitwise_and(0, 255), 0)
    _check("255 AND 255 = 255", prog.bitwise_and(255, 255), 255)


def test_bitwise_or() -> None:
    _reset_word_size(prog.WordSize.QWORD)
    _check("12 OR 10 = 14", prog.bitwise_or(12, 10), 14)
    _check("0 OR 0 = 0",    prog.bitwise_or(0, 0),   0)


def test_bitwise_xor() -> None:
    _reset_word_size(prog.WordSize.QWORD)
    _check("12 XOR 10 = 6",    prog.bitwise_xor(12, 10), 6)
    _check("255 XOR 255 = 0",  prog.bitwise_xor(255, 255), 0)
    _check("0 XOR 255 = 255",  prog.bitwise_xor(0, 255), 255)


def test_bitwise_not() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    _check("BYTE NOT 0 = -1",    prog.bitwise_not(0),   -1)
    _check("BYTE NOT 255 = 0",   prog.bitwise_not(255),  0)  # 255 unsigned = -1 signed; ~(-1) = 0
    _check("BYTE NOT 127 = -128", prog.bitwise_not(127), -128)
    _reset_word_size(prog.WordSize.QWORD)


def test_bitwise_nand() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    # NAND(255, 255) = NOT(255 AND 255) = NOT(255) = NOT(-1 signed) = 0
    _check("BYTE NAND(255,255) = 0", prog.bitwise_nand(255, 255), 0)
    _reset_word_size(prog.WordSize.QWORD)


def test_bitwise_nor() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    # NOR(0, 0) = NOT(0) = -1 (signed BYTE)
    _check("BYTE NOR(0,0) = -1", prog.bitwise_nor(0, 0), -1)
    _reset_word_size(prog.WordSize.QWORD)


def test_bitwise_xnor() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    # XNOR(255, 255) = NOT(255 XOR 255) = NOT(0) = -1
    _check("BYTE XNOR(255,255) = -1", prog.bitwise_xnor(255, 255), -1)
    _reset_word_size(prog.WordSize.QWORD)


# ============================================================================
# Shift Operation Tests
# ============================================================================

def test_logical_shift_left() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    _check("BYTE LSL 1<<1 = 2",   prog.shift_logical_left(1, 1), 2)
    _check("BYTE LSL 64<<1 = -128", prog.shift_logical_left(64, 1), -128)  # 128 signed as BYTE
    _check("BYTE LSL 128<<1 = 0",  prog.shift_logical_left(128, 1), 0)
    _reset_word_size(prog.WordSize.QWORD)


def test_logical_shift_right() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    _check("BYTE LSR 128>>1 = 64", prog.shift_logical_right(128, 1), 64)
    _check("BYTE LSR 255>>1 = 127", prog.shift_logical_right(255, 1), 127)  # logical: no sign ext
    _reset_word_size(prog.WordSize.QWORD)


def test_arithmetic_shift_right_sign_extension() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    # -128 in BYTE is 0x80; ASR 1 should give -64 (sign extended)
    _check("BYTE ASR -128>>1 = -64", prog.shift_arithmetic_right(-128, 1), -64)
    _reset_word_size(prog.WordSize.QWORD)


def test_rotate_left() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    # 0b10110101 ROL 1 = 0b01101011 = 107 unsigned = 107 signed (< 128)
    _check("BYTE ROL 0b10110101 by 1 = 107", prog.rotate_left(0b10110101, 1), 107)
    # ROL by 8 = identity for BYTE
    _check("BYTE ROL 42 by 8 = 42", prog.rotate_left(42, 8), 42)
    _reset_word_size(prog.WordSize.QWORD)


def test_rotate_right() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    # 0b00000001 ROR 1 = 0b10000000 = 128 unsigned = -128 signed BYTE
    _check("BYTE ROR 1 by 1 = -128", prog.rotate_right(1, 1), -128)
    _reset_word_size(prog.WordSize.QWORD)


def test_rotate_left_carry() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    # 0b10000000 RCL 1, carry_in=0 -> value=0, carry_out=1
    result, carry_out = prog.rotate_left_carry(0b10000000, 1, 0)
    _check("BYTE RCL 0x80 by 1 carry_in=0: result=0", result, 0)
    _check("BYTE RCL 0x80 by 1 carry_in=0: carry_out=1", carry_out, 1)
    _reset_word_size(prog.WordSize.QWORD)


def test_rotate_right_carry() -> None:
    _reset_word_size(prog.WordSize.BYTE)
    # 0b00000001 RCR 1, carry_in=0 -> value=0, carry_out=1
    result, carry_out = prog.rotate_right_carry(0b00000001, 1, 0)
    _check("BYTE RCR 0x01 by 1 carry_in=0: result=0", result, 0)
    _check("BYTE RCR 0x01 by 1 carry_in=0: carry_out=1", carry_out, 1)
    _reset_word_size(prog.WordSize.QWORD)


def test_shift_by_zero() -> None:
    """Shifting by 0 must return the original value."""
    _reset_word_size(prog.WordSize.QWORD)
    for v in [0, 1, 42, -1]:
        _check(f"LSL {v} by 0 = {v}", prog.shift_logical_left(v, 0), prog._mask(v))
        _check(f"LSR {v} by 0 = {v}", prog.shift_logical_right(v, 0), prog._mask(v))
        _check(f"ASL {v} by 0 = {v}", prog.shift_arithmetic_left(v, 0), prog._mask(v))
        _check(f"ASR {v} by 0 = {v}", prog.shift_arithmetic_right(v, 0), prog._mask(v))


# ============================================================================
# Test Runner
# ============================================================================

def run_all() -> None:
    suites = [
        test_word_size_toggle,
        test_word_size_setter,
        test_mask_byte,
        test_unsigned_mask_byte,
        test_dec_to_hex,
        test_dec_to_oct,
        test_dec_to_bin,
        test_show_all_bases_map,
        test_hex_to_dec,
        test_bin_to_dec,
        test_oct_to_dec,
        test_bidirectional_conversions,
        test_cross_base_conversions,
        test_bitwise_and,
        test_bitwise_or,
        test_bitwise_xor,
        test_bitwise_not,
        test_bitwise_nand,
        test_bitwise_nor,
        test_bitwise_xnor,
        test_logical_shift_left,
        test_logical_shift_right,
        test_arithmetic_shift_right_sign_extension,
        test_rotate_left,
        test_rotate_right,
        test_rotate_left_carry,
        test_rotate_right_carry,
        test_shift_by_zero,
    ]

    print("=" * 55)
    print("  PROGRAMMER CALCULATOR TESTS")
    print("=" * 55)
    for suite in suites:
        suite()

    total = _PASS + _FAIL
    print("=" * 55)
    print(f"  Results: {_PASS}/{total} passed,  {_FAIL} failed")
    print("=" * 55)
    sys.exit(0 if _FAIL == 0 else 1)


if __name__ == "__main__":
    run_all()
