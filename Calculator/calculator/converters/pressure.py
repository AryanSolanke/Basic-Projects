"""
Pressure converter.

Features:
- Atmosphere, bar, kPa, mmHg, Pa, psi conversions.
- Single conversion path via Pascals as the base unit.
- Shared BaseConverter UI and history handling.
"""

from decimal import Decimal
from enum import IntEnum

from calculator.converters.base import BaseConverter
from calculator.converters.converter_utils import to_decimal
from calculator.config import PRESSURE_HISTORY_FILE
from calculator.exceptions import CalculatorError


class PressureUnit(IntEnum):
    """Pressure unit types - 6 units total."""
    ATMOSPHERE = 1
    BAR = 2
    KILOPASCAL = 3
    MM_MERCURY = 4
    PASCAL = 5
    PSI = 6
    QUIT = 7


# ============================================================================
# Menu Display Functions
# ============================================================================

def pressure_conv_menuMsg() -> None:
    """Display pressure conversion menu with all 6 units."""
    print("\n" + "="*50)
    print("PRESSURE CONVERSION")
    print("="*50)
    print("\nPRESSURE UNITS:")
    print("  1. Atmosphere (atm)")
    print("  2. Bar (bar)")
    print("  3. Kilopascal (kPa)")
    print("  4. Millimeter of Mercury (mmHg)")
    print("  5. Pascal (Pa)")
    print("  6. Pounds per Square Inch (psi)")
    print("\n  7. Quit Pressure Converter")
    print("="*50)


# ============================================================================
# Universal Pressure Conversion Function
# ============================================================================

def convert_pressure(value: Decimal, from_unit: int, to_unit: int) -> Decimal:
    """
    Universal pressure converter - converts any pressure unit to any other unit.

    Strategy:
    1. Convert input value to Pascals (base unit)
    2. Convert Pascals to target unit

    Args:
        value: Pressure value to convert
        from_unit: Source unit (PressureUnit enum value)
        to_unit: Target unit (PressureUnit enum value)

    Returns:
        Converted pressure value as Decimal.
    """
    to_pascal_factors = {
        PressureUnit.ATMOSPHERE: Decimal("101325"),
        PressureUnit.BAR: Decimal("100000"),
        PressureUnit.KILOPASCAL: Decimal("1000"),
        PressureUnit.MM_MERCURY: Decimal("133.322"),
        PressureUnit.PASCAL: Decimal("1"),
        PressureUnit.PSI: Decimal("6894.76"),
    }

    pressure_in_pa = to_decimal(value, "Pressure") * to_pascal_factors[from_unit]
    return pressure_in_pa / to_pascal_factors[to_unit]


# ============================================================================
# Pressure Unit Names and Abbreviations
# ============================================================================

PRESSURE_UNIT_NAMES = {
    PressureUnit.ATMOSPHERE: "Atmosphere",
    PressureUnit.BAR: "Bar",
    PressureUnit.KILOPASCAL: "Kilopascal",
    PressureUnit.MM_MERCURY: "Millimeter of Mercury",
    PressureUnit.PASCAL: "Pascal",
    PressureUnit.PSI: "Pounds per Square Inch",
}

PRESSURE_UNIT_ABBREV = {
    PressureUnit.ATMOSPHERE: "atm",
    PressureUnit.BAR: "bar",
    PressureUnit.KILOPASCAL: "kPa",
    PressureUnit.MM_MERCURY: "mmHg",
    PressureUnit.PASCAL: "Pa",
    PressureUnit.PSI: "psi",
}

HISTORY_FILE = PRESSURE_HISTORY_FILE


# ============================================================================
# Main Pressure Converter Function
# ============================================================================

class PressureConverter(BaseConverter):
    """Pressure converter implementation."""

    name = "PRESSURE"
    emoji = ""
    history_file = HISTORY_FILE
    units = {unit: (PRESSURE_UNIT_NAMES[unit], PRESSURE_UNIT_ABBREV[unit]) for unit in PRESSURE_UNIT_NAMES}

    def convert(self, value: Decimal, from_unit: int, to_unit: int) -> Decimal:
        return convert_pressure(value, from_unit, to_unit)

    def display_menu(self) -> None:
        pressure_conv_menuMsg()

    def get_value_prompt(self, unit_name: str) -> str:
        return "\nEnter pressure: "


def display_hist_pressure_conv() -> None:
    """Display pressure conversion history."""
    PressureConverter().display_history()


def clear_hist_pressure_conv() -> None:
    """Clear pressure conversion history."""
    PressureConverter().clear_history()

def pressure_converter() -> None:
    """Main pressure conversion interface."""
    try:
        PressureConverter().run()
    except (CalculatorError):
        raise
