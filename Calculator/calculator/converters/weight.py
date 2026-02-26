"""
Weight converter.

Features:
- Metric and imperial/US units (13 total).
- Single conversion path via kilograms as the base unit.
- Shared BaseConverter UI and history handling.
"""

from decimal import Decimal
from enum import IntEnum

from calculator.converters.base import BaseConverter
from calculator.converters.converter_utils import to_decimal
from calculator.config import WEIGHT_HISTORY_FILE
from calculator.exceptions import CalculatorError

class WeightUnit(IntEnum):
    """Weight unit types - 13 units total."""
    KILOGRAM = 1
    GRAM = 2
    MILLIGRAM = 3
    CENTIGRAM = 4
    DECIGRAM = 5
    DECAGRAM = 6
    HECTOGRAM = 7
    METRIC_TONNE = 8
    OUNCE = 9
    POUND = 10
    STONE = 11
    SHORT_TON_US = 12
    LONG_TON_UK = 13
    QUIT = 14


# ============================================================================
# Menu Display Functions
# ============================================================================

def weight_conv_menuMsg() -> None:
    """Display weight conversion menu with all 13 units."""
    print("\n" + "="*50)
    print("WEIGHT CONVERSION")
    print("="*50)
    print("\nMETRIC UNITS:")
    print("  1.  Kilogram (kg)")
    print("  2.  Gram (g)")
    print("  3.  Milligram (mg)")
    print("  4.  Centigram (cg)")
    print("  5.  Decigram (dg)")
    print("  6.  Decagram (dag)")
    print("  7.  Hectogram (hg)")
    print("  8.  Metric Tonne (t)")
    print("\nIMPERIAL/US UNITS:")
    print("  9.  Ounce (oz)")
    print("  10. Pound (lb)")
    print("  11. Stone (st)")
    print("  12. Short Ton - US (ton)")
    print("  13. Long Ton - UK (ton)")
    print("\n  14. Quit Weight Converter")
    print("="*50)


# ============================================================================
# Universal Weight Conversion Function
# ============================================================================

def convert_weight(value: Decimal, from_unit: int, to_unit: int) -> Decimal:
    """
    Universal weight converter - converts any weight unit to any other unit.

    Strategy:
    1. Convert input value to kilograms (base unit)
    2. Convert kilograms to target unit

    Args:
        value: Weight value to convert
        from_unit: Source unit (WeightUnit enum value)
        to_unit: Target unit (WeightUnit enum value)

    Returns:
        Converted weight value as Decimal.
    """
    to_kg_factors = {
        WeightUnit.KILOGRAM: Decimal("1"),
        WeightUnit.GRAM: Decimal("0.001"),
        WeightUnit.MILLIGRAM: Decimal("0.000001"),
        WeightUnit.CENTIGRAM: Decimal("0.00001"),
        WeightUnit.DECIGRAM: Decimal("0.0001"),
        WeightUnit.DECAGRAM: Decimal("0.01"),
        WeightUnit.HECTOGRAM: Decimal("0.1"),
        WeightUnit.METRIC_TONNE: Decimal("1000"),
        WeightUnit.OUNCE: Decimal("0.0283495"),
        WeightUnit.POUND: Decimal("0.453592"),
        WeightUnit.STONE: Decimal("6.35029"),
        WeightUnit.SHORT_TON_US: Decimal("907.185"),
        WeightUnit.LONG_TON_UK: Decimal("1016.05"),
    }

    weight_in_kg = to_decimal(value, "Weight") * to_kg_factors[from_unit]
    return weight_in_kg / to_kg_factors[to_unit]


# ============================================================================
# Weight Unit Names and Abbreviations
# ============================================================================

WEIGHT_UNIT_NAMES = {
    WeightUnit.KILOGRAM: "Kilogram",
    WeightUnit.GRAM: "Gram",
    WeightUnit.MILLIGRAM: "Milligram",
    WeightUnit.CENTIGRAM: "Centigram",
    WeightUnit.DECIGRAM: "Decigram",
    WeightUnit.DECAGRAM: "Decagram",
    WeightUnit.HECTOGRAM: "Hectogram",
    WeightUnit.METRIC_TONNE: "Metric Tonne",
    WeightUnit.OUNCE: "Ounce",
    WeightUnit.POUND: "Pound",
    WeightUnit.STONE: "Stone",
    WeightUnit.SHORT_TON_US: "Short Ton (US)",
    WeightUnit.LONG_TON_UK: "Long Ton (UK)",
}

WEIGHT_UNIT_ABBREV = {
    WeightUnit.KILOGRAM: "kg",
    WeightUnit.GRAM: "g",
    WeightUnit.MILLIGRAM: "mg",
    WeightUnit.CENTIGRAM: "cg",
    WeightUnit.DECIGRAM: "dg",
    WeightUnit.DECAGRAM: "dag",
    WeightUnit.HECTOGRAM: "hg",
    WeightUnit.METRIC_TONNE: "t",
    WeightUnit.OUNCE: "oz",
    WeightUnit.POUND: "lb",
    WeightUnit.STONE: "st",
    WeightUnit.SHORT_TON_US: "ton (US)",
    WeightUnit.LONG_TON_UK: "ton (UK)",
}

HISTORY_FILE = WEIGHT_HISTORY_FILE


# ============================================================================
# Main Weight Converter Function
# ============================================================================

class WeightConverter(BaseConverter):
    """Weight converter implementation."""

    name = "WEIGHT"
    emoji = ""
    history_file = HISTORY_FILE
    units = {unit: (WEIGHT_UNIT_NAMES[unit], WEIGHT_UNIT_ABBREV[unit]) for unit in WEIGHT_UNIT_NAMES}

    def convert(self, value: Decimal, from_unit: int, to_unit: int) -> Decimal:
        return convert_weight(value, from_unit, to_unit)

    def display_menu(self) -> None:
        weight_conv_menuMsg()

    def get_value_prompt(self, unit_name: str) -> str:
        return f"\nEnter weight in {unit_name}: "


def display_hist_weight_conv() -> None:
    """Display weight conversion history."""
    WeightConverter().display_history()


def clear_hist_weight_conv() -> None:
    """Clear weight conversion history."""
    WeightConverter().clear_history()

def weight_converter() -> None:
    """Main weight conversion interface."""
    try:
        WeightConverter().run()
    except (CalculatorError):
        raise
