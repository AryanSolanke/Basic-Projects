"""
Data unit converter.

Features:
- 35 units and 1,190 bidirectional conversions.
- SI (decimal) and IEC (binary) prefixes supported.
- Converts via bits as the base unit for consistency.

Unit groups:
- Base: Bit, Nibble, Byte
- SI bits/bytes: K/M/G/T/P/E/Z/Y (base 1000)
- IEC bits/bytes: Ki/Mi/Gi/Ti/Pi/Ei/Zi/Yi (base 1024)
"""

from decimal import Decimal
from enum import IntEnum

from calculator.converters.base import BaseConverter
from calculator.converters.converter_utils import to_decimal
from calculator.config import DATA_HISTORY_FILE
from calculator.exceptions import CalculatorError

class DataUnit(IntEnum):
    """Data unit types - 35 units total."""
    # Base units
    BIT = 1
    NIBBLE = 2
    BYTE = 3
    
    # Decimal (SI) bits - base 1000
    KILOBIT = 4
    KIBIBIT = 5
    MEGABIT = 6
    MEBIBIT = 7
    GIGABIT = 8
    GIBIBIT = 9
    TERABIT = 10
    TEBIBIT = 11
    PETABIT = 12
    PEBIBIT = 13
    EXABIT = 14
    EXBIBIT = 15
    ZETTABIT = 16
    ZEBIBIT = 17
    YOTTABIT = 18
    YOBIBIT = 19
    
    # Decimal (SI) bytes - base 1000
    KILOBYTE = 20
    KIBIBYTE = 21
    MEGABYTE = 22
    MEBIBYTE = 23
    GIGABYTE = 24
    GIBIBYTE = 25
    TERABYTE = 26
    TEBIBYTE = 27
    PETABYTE = 28
    PEBIBYTE = 29
    EXABYTE = 30
    EXBIBYTE = 31
    ZETTABYTE = 32
    ZEBIBYTE = 33
    YOTTABYTE = 34
    YOBIBYTE = 35
    
    QUIT = 36


HISTORY_FILE = DATA_HISTORY_FILE


# ============================================================================
# Menu Display Functions
# ============================================================================

def data_converter_menuMsg() -> None:
    """Display comprehensive data unit conversion menu."""
    print("\n" + "="*60)
    print("           DATA UNIT CONVERSION MENU")
    print("="*60)
    print("\nBASE UNITS:")
    print("  1.  Bit (b)")
    print("  2.  Nibble (4 bits)")
    print("  3.  Byte (B)")
    
    print("\nDECIMAL BITS (SI - Base 1000):")
    print("  4.  Kilobit (kb)")
    print("  6.  Megabit (Mb)")
    print("  8.  Gigabit (Gb)")
    print("  10. Terabit (Tb)")
    print("  12. Petabit (Pb)")
    print("  14. Exabit (Eb)")
    print("  16. Zettabit (Zb)")
    print("  18. Yottabit (Yb)")
    
    print("\nBINARY BITS (IEC - Base 1024):")
    print("  5.  Kibibit (Kib)")
    print("  7.  Mebibit (Mib)")
    print("  9.  Gibibit (Gib)")
    print("  11. Tebibit (Tib)")
    print("  13. Pebibit (Pib)")
    print("  15. Exbibit (Eib)")
    print("  17. Zebibit (Zib)")
    print("  19. Yobibit (Yib)")
    
    print("\nDECIMAL BYTES (SI - Base 1000):")
    print("  20. Kilobyte (KB)")
    print("  22. Megabyte (MB)")
    print("  24. Gigabyte (GB)")
    print("  26. Terabyte (TB)")
    print("  28. Petabyte (PB)")
    print("  30. Exabyte (EB)")
    print("  32. Zettabyte (ZB)")
    print("  34. Yottabyte (YB)")
    
    print("\nBINARY BYTES (IEC - Base 1024):")
    print("  21. Kibibyte (KiB)")
    print("  23. Mebibyte (MiB)")
    print("  25. Gibibyte (GiB)")
    print("  27. Tebibyte (TiB)")
    print("  29. Pebibyte (PiB)")
    print("  31. Exbibyte (EiB)")
    print("  33. Zebibyte (ZiB)")
    print("  35. Yobibyte (YiB)")
    
    print("\n  36. Quit Data Converter")
    print("="*60)


# ============================================================================
# Universal Data Conversion Function
# ============================================================================

def convert_data(value, from_unit: int, to_unit: int) -> Decimal:
    """
    Universal data converter - converts any data unit to any other unit.
    
    This single function handles all 1,190 possible conversions (35x34 pairs).
    
    Strategy:
    1. Convert input value to bits (base unit)
    2. Convert bits to target unit
    
    Conversion factors (to bits):
    -----------------------------
    Base Units:
    - 1 Bit         = 1 bit
    - 1 Nibble      = 4 bits
    - 1 Byte        = 8 bits
    
    Decimal Bits (SI - powers of 1000):
    - 1 Kilobit     = 1,000 bits (10^3)
    - 1 Megabit     = 1,000,000 bits (10^6)
    - 1 Gigabit     = 1,000,000,000 bits (10^9)
    - 1 Terabit     = 10^12 bits
    - 1 Petabit     = 10^15 bits
    - 1 Exabit      = 10^18 bits
    - 1 Zettabit    = 10^21 bits
    - 1 Yottabit    = 10^24 bits
    
    Binary Bits (IEC - powers of 1024):
    - 1 Kibibit     = 1,024 bits (2^10)
    - 1 Mebibit     = 1,048,576 bits (2^20)
    - 1 Gibibit     = 1,073,741,824 bits (2^30)
    - 1 Tebibit     = 2^40 bits
    - 1 Pebibit     = 2^50 bits
    - 1 Exbibit     = 2^60 bits
    - 1 Zebibit     = 2^70 bits
    - 1 Yobibit     = 2^80 bits
    
    Decimal Bytes (SI - powers of 1000, then x8):
    - 1 Kilobyte    = 8,000 bits
    - 1 Megabyte    = 8,000,000 bits
    - 1 Gigabyte    = 8,000,000,000 bits
    - And so on... (x8 for bytes)
    
    Binary Bytes (IEC - powers of 1024, then x8):
    - 1 Kibibyte    = 8,192 bits
    - 1 Mebibyte    = 8,388,608 bits
    - 1 Gibibyte    = 8,589,934,592 bits
    - And so on... (x8 for bytes)
    
    Args:
        value: Data value to convert
        from_unit: Source unit (DataUnit enum value)
        to_unit: Target unit (DataUnit enum value)
    
    Returns:
        Converted data value as Decimal.
    
    Examples:
        >>> convert_data(1, DataUnit.BYTE, DataUnit.BIT)
        8.0
        >>> convert_data(1, DataUnit.KILOBYTE, DataUnit.BYTE)
        1000.0
        >>> convert_data(1, DataUnit.KIBIBYTE, DataUnit.BYTE)
        1024.0
    """
    # Conversion factors: Each unit -> bits
    to_bits_factors = {
        # Base units
        DataUnit.BIT: Decimal("1"),
        DataUnit.NIBBLE: Decimal("4"),
        DataUnit.BYTE: Decimal("8"),
        
        # Decimal bits (SI - base 1000)
        DataUnit.KILOBIT: Decimal("1000"),                # 10^3
        DataUnit.MEGABIT: Decimal("1000000"),             # 10^6
        DataUnit.GIGABIT: Decimal("1000000000"),          # 10^9
        DataUnit.TERABIT: Decimal("1000000000000"),       # 10^12
        DataUnit.PETABIT: Decimal("1000000000000000"),    # 10^15
        DataUnit.EXABIT: Decimal("1e18"),                 # 10^18
        DataUnit.ZETTABIT: Decimal("1e21"),               # 10^21
        DataUnit.YOTTABIT: Decimal("1e24"),               # 10^24
        
        # Binary bits (IEC - base 1024)
        DataUnit.KIBIBIT: Decimal(2) ** 10,              # 2^10
        DataUnit.MEBIBIT: Decimal(2) ** 20,              # 2^20
        DataUnit.GIBIBIT: Decimal(2) ** 30,              # 2^30
        DataUnit.TEBIBIT: Decimal(2) ** 40,              # 2^40
        DataUnit.PEBIBIT: Decimal(2) ** 50,              # 2^50
        DataUnit.EXBIBIT: Decimal(2) ** 60,              # 2^60
        DataUnit.ZEBIBIT: Decimal(2) ** 70,              # 2^70
        DataUnit.YOBIBIT: Decimal(2) ** 80,              # 2^80
        
        # Decimal bytes (SI - base 1000, x8 for bytes)
        DataUnit.KILOBYTE: Decimal("8000"),                # 1000 x 8
        DataUnit.MEGABYTE: Decimal("8000000"),             # 10^6 x 8
        DataUnit.GIGABYTE: Decimal("8000000000"),          # 10^9 x 8
        DataUnit.TERABYTE: Decimal("8000000000000"),       # 10^12 x 8
        DataUnit.PETABYTE: Decimal("8000000000000000"),    # 10^15 x 8
        DataUnit.EXABYTE: Decimal("8e18"),                 # 10^18 x 8
        DataUnit.ZETTABYTE: Decimal("8e21"),               # 10^21 x 8
        DataUnit.YOTTABYTE: Decimal("8e24"),               # 10^24 x 8
        
        # Binary bytes (IEC - base 1024, x8 for bytes)
        DataUnit.KIBIBYTE: Decimal(2) ** 10 * Decimal(8),  # 1024 x 8
        DataUnit.MEBIBYTE: Decimal(2) ** 20 * Decimal(8),  # 2^20 x 8
        DataUnit.GIBIBYTE: Decimal(2) ** 30 * Decimal(8),  # 2^30 x 8
        DataUnit.TEBIBYTE: Decimal(2) ** 40 * Decimal(8),  # 2^40 x 8
        DataUnit.PEBIBYTE: Decimal(2) ** 50 * Decimal(8),  # 2^50 x 8
        DataUnit.EXBIBYTE: Decimal(2) ** 60 * Decimal(8),  # 2^60 x 8
        DataUnit.ZEBIBYTE: Decimal(2) ** 70 * Decimal(8),  # 2^70 x 8
        DataUnit.YOBIBYTE: Decimal(2) ** 80 * Decimal(8),  # 2^80 x 8
    }
    
    # Step 1: Convert input value to bits (base unit)
    data_in_bits = to_decimal(value, "Data") * to_bits_factors[from_unit]
    
    # Step 2: Convert bits to target unit
    result = data_in_bits / to_bits_factors[to_unit]
    
    return result


# ============================================================================
# Data Unit Names and Abbreviations
# ============================================================================

DATA_UNIT_NAMES = {
    # Base units
    DataUnit.BIT: "Bit",
    DataUnit.NIBBLE: "Nibble",
    DataUnit.BYTE: "Byte",
    
    # Decimal bits (SI)
    DataUnit.KILOBIT: "Kilobit",
    DataUnit.MEGABIT: "Megabit",
    DataUnit.GIGABIT: "Gigabit",
    DataUnit.TERABIT: "Terabit",
    DataUnit.PETABIT: "Petabit",
    DataUnit.EXABIT: "Exabit",
    DataUnit.ZETTABIT: "Zettabit",
    DataUnit.YOTTABIT: "Yottabit",
    
    # Binary bits (IEC)
    DataUnit.KIBIBIT: "Kibibit",
    DataUnit.MEBIBIT: "Mebibit",
    DataUnit.GIBIBIT: "Gibibit",
    DataUnit.TEBIBIT: "Tebibit",
    DataUnit.PEBIBIT: "Pebibit",
    DataUnit.EXBIBIT: "Exbibit",
    DataUnit.ZEBIBIT: "Zebibit",
    DataUnit.YOBIBIT: "Yobibit",
    
    # Decimal bytes (SI)
    DataUnit.KILOBYTE: "Kilobyte",
    DataUnit.MEGABYTE: "Megabyte",
    DataUnit.GIGABYTE: "Gigabyte",
    DataUnit.TERABYTE: "Terabyte",
    DataUnit.PETABYTE: "Petabyte",
    DataUnit.EXABYTE: "Exabyte",
    DataUnit.ZETTABYTE: "Zettabyte",
    DataUnit.YOTTABYTE: "Yottabyte",
    
    # Binary bytes (IEC)
    DataUnit.KIBIBYTE: "Kibibyte",
    DataUnit.MEBIBYTE: "Mebibyte",
    DataUnit.GIBIBYTE: "Gibibyte",
    DataUnit.TEBIBYTE: "Tebibyte",
    DataUnit.PEBIBYTE: "Pebibyte",
    DataUnit.EXBIBYTE: "Exbibyte",
    DataUnit.ZEBIBYTE: "Zebibyte",
    DataUnit.YOBIBYTE: "Yobibyte",
}

DATA_UNIT_ABBREV = {
    # Base units
    DataUnit.BIT: "b",
    DataUnit.NIBBLE: "nibble",
    DataUnit.BYTE: "B",
    
    # Decimal bits (SI)
    DataUnit.KILOBIT: "kb",
    DataUnit.MEGABIT: "Mb",
    DataUnit.GIGABIT: "Gb",
    DataUnit.TERABIT: "Tb",
    DataUnit.PETABIT: "Pb",
    DataUnit.EXABIT: "Eb",
    DataUnit.ZETTABIT: "Zb",
    DataUnit.YOTTABIT: "Yb",
    
    # Binary bits (IEC)
    DataUnit.KIBIBIT: "Kib",
    DataUnit.MEBIBIT: "Mib",
    DataUnit.GIBIBIT: "Gib",
    DataUnit.TEBIBIT: "Tib",
    DataUnit.PEBIBIT: "Pib",
    DataUnit.EXBIBIT: "Eib",
    DataUnit.ZEBIBIT: "Zib",
    DataUnit.YOBIBIT: "Yib",
    
    # Decimal bytes (SI)
    DataUnit.KILOBYTE: "KB",
    DataUnit.MEGABYTE: "MB",
    DataUnit.GIGABYTE: "GB",
    DataUnit.TERABYTE: "TB",
    DataUnit.PETABYTE: "PB",
    DataUnit.EXABYTE: "EB",
    DataUnit.ZETTABYTE: "ZB",
    DataUnit.YOTTABYTE: "YB",
    
    # Binary bytes (IEC)
    DataUnit.KIBIBYTE: "KiB",
    DataUnit.MEBIBYTE: "MiB",
    DataUnit.GIBIBYTE: "GiB",
    DataUnit.TEBIBYTE: "TiB",
    DataUnit.PEBIBYTE: "PiB",
    DataUnit.EXBIBYTE: "EiB",
    DataUnit.ZEBIBYTE: "ZiB",
    DataUnit.YOBIBYTE: "YiB",
}


# ============================================================================
# Helper Functions
# ============================================================================


def format_data_result(result) -> str:
    """
    Format data conversion result with intelligent precision.
    
    Args:
        result: Numerical result to format
    
    Returns:
        String representation with appropriate precision.
    """
    result_dec = to_decimal(result, "Data")
    if not result_dec.is_finite():
        return str(result_dec)

    abs_val = abs(result_dec)
    if abs_val >= Decimal("1e15") or (abs_val != 0 and abs_val < Decimal("1e-6")):
        return format(result_dec, ".6E").lower()
    if abs_val >= Decimal("1000"):
        return format(result_dec, ".2f")
    return format(result_dec, ".9g")


# ============================================================================
# Main Data Converter Function
# ============================================================================

class DataConverter(BaseConverter):
    """Data unit converter implementation."""

    name = "DATA"
    emoji = "📊"
    history_file = HISTORY_FILE
    units = {unit: (DATA_UNIT_NAMES[unit], DATA_UNIT_ABBREV[unit]) for unit in DATA_UNIT_NAMES}

    def convert(self, value: Decimal, from_unit: int, to_unit: int) -> Decimal:
        return convert_data(value, from_unit, to_unit)

    def display_menu(self) -> None:
        data_converter_menuMsg()

    def get_value_prompt(self, unit_name: str) -> str:
        return f"\nEnter data amount in {unit_name}: "

    def format_result(self, result) -> str:
        return format_data_result(result)


def display_hist_data_conv() -> None:
    """Display data conversion history."""
    DataConverter().display_history()


def clear_hist_data_conv() -> None:
    """Clear data conversion history."""
    DataConverter().clear_history()

def data_converter() -> None:
    """
    Main data unit conversion interface.
    Provides interactive menu for data conversions.
    """
    try:
        DataConverter().run()
    except (CalculatorError):
        raise

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("        DATA UNIT CONVERTER")
    print("="*60)
    data_converter()
