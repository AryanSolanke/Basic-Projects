"""Programmer calculator public module with stable API."""

from __future__ import annotations

from textwrap import dedent

from calculator.exceptions import (
    CalculatorError,
    InvalidInputError,
    InvalidBitShiftError,
    NullInputError,
)
from calculator.programmer_parts.operations import (
    WORD_SIZE_CYCLE,
    WORD_SIZE_LABELS,
    WordSize,
    bitwise_and as _bitwise_and_impl,
    bitwise_not as _bitwise_not_impl,
    bitwise_or as _bitwise_or_impl,
    bitwise_xor as _bitwise_xor_impl,
    bin_to_dec as _bin_to_dec_impl,
    dec_to_bin as _dec_to_bin_impl,
    dec_to_hex as _dec_to_hex_impl,
    dec_to_oct as _dec_to_oct_impl,
    hex_to_dec as _hex_to_dec_impl,
    mask as _mask_impl,
    oct_to_dec as _oct_to_dec_impl,
    parse_int as _parse_int_impl,
    rotate_left as _rotate_left_impl,
    rotate_left_carry as _rotate_left_carry_impl,
    rotate_right as _rotate_right_impl,
    rotate_right_carry as _rotate_right_carry_impl,
    shift_arithmetic_left as _shift_arithmetic_left_impl,
    shift_arithmetic_right as _shift_arithmetic_right_impl,
    shift_logical_left as _shift_logical_left_impl,
    shift_logical_right as _shift_logical_right_impl,
    unsigned_mask as _unsigned_mask_impl,
)

_word_size: WordSize = WordSize.QWORD


def get_word_size() -> WordSize:
    return _word_size


def set_word_size(word_size: WordSize | int) -> WordSize:
    global _word_size
    _word_size = WordSize(word_size)
    return _word_size


def toggle_word_size() -> WordSize:
    global _word_size
    idx = WORD_SIZE_CYCLE.index(_word_size)
    _word_size = WORD_SIZE_CYCLE[(idx + 1) % len(WORD_SIZE_CYCLE)]
    return _word_size


def _mask(value: int) -> int:
    return _mask_impl(value, _word_size)


def _unsigned_mask(value: int) -> int:
    return _unsigned_mask_impl(value, _word_size)


def _parse_int(raw: str) -> int:
    return _parse_int_impl(raw)


def dec_to_hex(n: int) -> str:
    return _dec_to_hex_impl(n, _word_size)


def dec_to_bin(n: int) -> str:
    return _dec_to_bin_impl(n, _word_size)


def dec_to_oct(n: int) -> str:
    return _dec_to_oct_impl(n, _word_size)


def hex_to_dec(s: str) -> int:
    return _hex_to_dec_impl(s, _word_size)


def hex_to_bin(s: str) -> str:
    return dec_to_bin(int(s.strip(), 16))


def hex_to_oct(s: str) -> str:
    return dec_to_oct(int(s.strip(), 16))


def bin_to_dec(s: str) -> int:
    return _bin_to_dec_impl(s, _word_size)


def bin_to_hex(s: str) -> str:
    return dec_to_hex(int(s.replace(" ", ""), 2))


def bin_to_oct(s: str) -> str:
    return dec_to_oct(int(s.replace(" ", ""), 2))


def oct_to_dec(s: str) -> int:
    return _oct_to_dec_impl(s, _word_size)


def oct_to_hex(s: str) -> str:
    return dec_to_hex(int(s.strip(), 8))


def oct_to_bin(s: str) -> str:
    return dec_to_bin(int(s.strip(), 8))


def show_all_bases(n: int) -> str:
    bases = show_all_bases_map(n)
    return (
        f"  DEC : {bases['DEC']}\n"
        f"  HEX : {bases['HEX']}\n"
        f"  BIN : {bases['BIN']}\n"
        f"  OCT : {bases['OCT']}"
    )


def show_all_bases_map(n: int) -> dict[str, str]:
    u = _unsigned_mask(n)
    return {
        "DEC": str(n),
        "HEX": dec_to_hex(u),
        "BIN": dec_to_bin(u),
        "OCT": dec_to_oct(u),
    }


def bitwise_and(a: int, b: int) -> int:
    return _bitwise_and_impl(a, b, _word_size)


def bitwise_or(a: int, b: int) -> int:
    return _bitwise_or_impl(a, b, _word_size)


def bitwise_xor(a: int, b: int) -> int:
    return _bitwise_xor_impl(a, b, _word_size)


def bitwise_not(a: int) -> int:
    return _bitwise_not_impl(a, _word_size)


def bitwise_nand(a: int, b: int) -> int:
    return bitwise_not(a & b)


def bitwise_nor(a: int, b: int) -> int:
    return bitwise_not(a | b)


def bitwise_xnor(a: int, b: int) -> int:
    return bitwise_not(a ^ b)


def shift_arithmetic_left(value: int, n: int) -> int:
    return _shift_arithmetic_left_impl(value, n, _word_size)


def shift_arithmetic_right(value: int, n: int) -> int:
    return _shift_arithmetic_right_impl(value, n, _word_size)


def shift_logical_left(value: int, n: int) -> int:
    return _shift_logical_left_impl(value, n, _word_size)


def shift_logical_right(value: int, n: int) -> int:
    return _shift_logical_right_impl(value, n, _word_size)


def rotate_left(value: int, n: int) -> int:
    return _rotate_left_impl(value, n, _word_size)


def rotate_right(value: int, n: int) -> int:
    return _rotate_right_impl(value, n, _word_size)


def rotate_left_carry(value: int, n: int, carry: int) -> tuple[int, int]:
    return _rotate_left_carry_impl(value, n, carry, _word_size)


def rotate_right_carry(value: int, n: int, carry: int) -> tuple[int, int]:
    return _rotate_right_carry_impl(value, n, carry, _word_size)


def _get_int(prompt: str) -> int | None:
    try:
        raw = input(prompt).strip()
        return _parse_int(raw)
    except CalculatorError as e:
        print(e)
        return None
    except (ValueError, TypeError):
        print(InvalidInputError())
        return None


def _get_shift_amount() -> int | None:
    try:
        raw = input("Enter shift amount: ").strip()
        if not raw:
            raise NullInputError()
        n = int(raw)
        if n < 0:
            raise InvalidBitShiftError()
        return n
    except CalculatorError as e:
        print(e)
        return None
    except (ValueError, TypeError):
        print(InvalidInputError())
        return None


def prog_main_menu() -> None:
    ws_label = WORD_SIZE_LABELS[_word_size]
    print(
        dedent(
            f"""
        {'='*55}
        PROGRAMMER CALCULATOR          [{ws_label}]
        {'='*55}
        1. Base Conversion     (DEC / HEX / BIN / OCT)
        2. Bitwise Operations  (AND, OR, XOR, NOT, NAND, NOR, XNOR)
        3. Bit Shift           (Arithmetic, Logical, Rotate, Carry)
        4. Toggle Word Size    (QWORD → DWORD → WORD → BYTE)
        5. Quit Programmer Calculator
        {'='*55}"""
        )
    )


def base_conv_menu() -> None:
    print(
        dedent(
            """
        ──────────────────────────────────────────
        BASE CONVERSION  (enter any prefix or none)
          Decimal : plain digits, e.g. 255
          Hex     : 0xFF  or  FF
          Binary  : 0b11111111
          Octal   : 0o377
        ──────────────────────────────────────────
        1.  DEC → HEX / BIN / OCT  (show all)
        2.  HEX → DEC / BIN / OCT  (show all)
        3.  BIN → DEC / HEX / OCT  (show all)
        4.  OCT → DEC / HEX / BIN  (show all)
        5.  Back
        ──────────────────────────────────────────"""
        )
    )


def bitwise_menu() -> None:
    print(
        dedent(
            """
        ──────────────────────────────────────────
        BITWISE OPERATIONS
        ──────────────────────────────────────────
        1.  AND   (A & B)
        2.  OR    (A | B)
        3.  XOR   (A ^ B)
        4.  NOT   (~A)
        5.  NAND  (~(A & B))
        6.  NOR   (~(A | B))
        7.  XNOR  (~(A ^ B))
        8.  Back
        ──────────────────────────────────────────"""
        )
    )


def shift_menu() -> None:
    print(
        dedent(
            """
        ──────────────────────────────────────────
        BIT SHIFT
        ──────────────────────────────────────────
        1.  Arithmetic Shift Left  (ASL)
        2.  Arithmetic Shift Right (ASR)
        3.  Logical Shift Left     (LSL)
        4.  Logical Shift Right    (LSR)
        5.  Rotate Left            (ROL)
        6.  Rotate Right           (ROR)
        7.  Rotate Left  + Carry   (RCL)
        8.  Rotate Right + Carry   (RCR)
        9.  Back
        ──────────────────────────────────────────"""
        )
    )


def _print_result(label: str, value: int) -> None:
    print(f"\n  ┌─ {label}")
    print(show_all_bases(value))
    print()


def handle_base_conversion() -> None:
    while True:
        base_conv_menu()
        try:
            choice = int(input("Enter choice: "))
        except (ValueError, TypeError):
            print(InvalidInputError())
            continue
        if choice == 5:
            break
        if choice == 1:
            raw = input("Enter decimal value: ").strip()
            try:
                if not raw:
                    raise NullInputError()
                n = int(raw)
                _print_result(f"DEC {n}", n)
            except CalculatorError as e:
                print(e)
            except ValueError:
                print(InvalidInputError("\nInput Error: Invalid decimal number.\n"))
        elif choice == 2:
            raw = input("Enter hex value (e.g. FF or 0xFF): ").strip()
            try:
                n = hex_to_dec(raw.replace("0x", "").replace("0X", ""))
                _print_result(f"HEX {raw.upper()}", n)
            except CalculatorError as e:
                print(e)
        elif choice == 3:
            raw = input("Enter binary value (e.g. 1010 or 0b1010): ").strip().replace("0b", "").replace("0B", "").replace(" ", "")
            try:
                n = bin_to_dec(raw)
                _print_result(f"BIN {raw}", n)
            except CalculatorError as e:
                print(e)
        elif choice == 4:
            raw = input("Enter octal value (e.g. 377 or 0o377): ").strip().replace("0o", "").replace("0O", "")
            try:
                n = oct_to_dec(raw)
                _print_result(f"OCT {raw}", n)
            except CalculatorError as e:
                print(e)
        else:
            print(InvalidInputError("\nInput Error: Please select 1-5.\n"))


def handle_bitwise() -> None:
    while True:
        bitwise_menu()
        try:
            choice = int(input("Enter choice: "))
        except (ValueError, TypeError):
            print(InvalidInputError())
            continue
        if choice == 8:
            break
        if choice == 4:
            a = _get_int("Enter value A: ")
            if a is None:
                continue
            try:
                _print_result(f"NOT {a}", bitwise_not(a))
            except CalculatorError as e:
                print(e)
            continue
        if choice not in range(1, 8):
            print(InvalidInputError("\nInput Error: Please select 1-8.\n"))
            continue
        a = _get_int("Enter value A: ")
        if a is None:
            continue
        b = _get_int("Enter value B: ")
        if b is None:
            continue
        try:
            ops = {
                1: ("AND", bitwise_and),
                2: ("OR", bitwise_or),
                3: ("XOR", bitwise_xor),
                5: ("NAND", bitwise_nand),
                6: ("NOR", bitwise_nor),
                7: ("XNOR", bitwise_xnor),
            }
            label_str, op_func = ops[choice]
            _print_result(f"{a} {label_str} {b}", op_func(a, b))
        except CalculatorError as e:
            print(e)


def handle_bit_shift() -> None:
    while True:
        shift_menu()
        try:
            choice = int(input("Enter choice: "))
        except (ValueError, TypeError):
            print(InvalidInputError())
            continue
        if choice == 9:
            break
        if choice not in range(1, 9):
            print(InvalidInputError("\nInput Error: Please select 1-9.\n"))
            continue
        value = _get_int("Enter value: ")
        if value is None:
            continue
        n = _get_shift_amount()
        if n is None:
            continue
        try:
            if choice in (7, 8):
                try:
                    carry_raw = int(input("Enter carry flag (0 or 1): ").strip())
                    carry = carry_raw & 1
                except (ValueError, TypeError):
                    print(InvalidInputError("\nInput Error: Carry must be 0 or 1.\n"))
                    continue
                if choice == 7:
                    result, new_carry = rotate_left_carry(value, n, carry)
                    print(f"\n  ROL carry: value={value}, n={n}, carry_in={carry}")
                else:
                    result, new_carry = rotate_right_carry(value, n, carry)
                    print(f"\n  ROR carry: value={value}, n={n}, carry_in={carry}")
                print(f"  carry_out = {new_carry}")
                _print_result("Result", result)
                continue
            shift_ops = {
                1: ("ASL", shift_arithmetic_left),
                2: ("ASR", shift_arithmetic_right),
                3: ("LSL", shift_logical_left),
                4: ("LSR", shift_logical_right),
                5: ("ROL", rotate_left),
                6: ("ROR", rotate_right),
            }
            label_str, shift_func = shift_ops[choice]
            _print_result(f"{value} {label_str} {n}", shift_func(value, n))
        except CalculatorError as e:
            print(e)


def programmer_calc() -> None:
    while True:
        prog_main_menu()
        try:
            choice = int(input("Enter choice: "))
        except (ValueError, TypeError, KeyboardInterrupt):
            print(InvalidInputError())
            continue
        try:
            if choice == 1:
                handle_base_conversion()
            elif choice == 2:
                handle_bitwise()
            elif choice == 3:
                handle_bit_shift()
            elif choice == 4:
                new_ws = toggle_word_size()
                print(f"\n  Word size set to: {WORD_SIZE_LABELS[new_ws]}\n")
            elif choice == 5:
                print("\n  Programmer calculator closed!\n")
                break
            else:
                print(InvalidInputError("\nInput Error: Please select 1-5.\n"))
        except CalculatorError as e:
            print(e)
            continue
        except Exception as e:
            print(f"\nSystem Error: {type(e).__name__}\n")
            continue



