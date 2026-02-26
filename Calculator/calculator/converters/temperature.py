"""
Temperature converter.

Features:
- Celsius, Kelvin, and Fahrenheit conversions.
- Decimal arithmetic to avoid floating-point drift.
- Shared BaseConverter UI and history handling.
"""

from decimal import Decimal
from enum import IntEnum
from typing import Callable, Dict, Tuple

from calculator.converters.base import BaseConverter
from calculator.converters.converter_utils import to_decimal
from calculator.config import TEMP_HISTORY_FILE
from calculator.exceptions import CalculatorError

class TempUnit(IntEnum):
    """Temperature unit types."""
    CELSIUS = 1
    KELVIN = 2
    FAHRENHEIT = 3
    QUIT = 4


# ============================================================================
# Menu Display Functions
# ============================================================================

def temp_conv_menuMsg() -> None:
    """Display temperature conversion menu."""
    print("\n" + "="*50)
    print("TEMPERATURE CONVERSION")
    print("="*50)
    print("1. Celsius (°C)")
    print("2. Kelvin (K)")
    print("3. Fahrenheit (°F)")
    print("4. Quit Temperature Converter")
    print("="*50)


# ============================================================================
# Temperature Conversion Functions (pure Decimal)
# ============================================================================

def C_to_kelvin(tmp: Decimal) -> Decimal:
    """Convert Celsius to Kelvin."""
    return to_decimal(tmp, "Temperature") + Decimal("273.15")


def C_to_Fahrenheit(tmp: Decimal) -> Decimal:
    """Convert Celsius to Fahrenheit."""
    return (to_decimal(tmp, "Temperature") * Decimal(9) / Decimal(5)) + Decimal(32)


def K_to_celsius(tmp: Decimal) -> Decimal:
    """Convert Kelvin to Celsius."""
    return to_decimal(tmp, "Temperature") - Decimal("273.15")


def K_to_Fahrenheit(tmp: Decimal) -> Decimal:
    """Convert Kelvin to Fahrenheit."""
    return C_to_Fahrenheit(K_to_celsius(tmp))


def F_to_celsius(tmp: Decimal) -> Decimal:
    """Convert Fahrenheit to Celsius."""
    return (to_decimal(tmp, "Temperature") - Decimal(32)) * Decimal(5) / Decimal(9)


def F_to_kelvin(tmp: Decimal) -> Decimal:
    """Convert Fahrenheit to Kelvin."""
    return F_to_celsius(tmp) + Decimal("273.15")


# ============================================================================
# Conversion Lookup Tables
# ============================================================================

temp_conv_funcs: Dict[Tuple[int, int], Tuple[str, str, Callable]] = {
    (TempUnit.CELSIUS, TempUnit.KELVIN): ("Celsius", "Kelvin", C_to_kelvin),
    (TempUnit.CELSIUS, TempUnit.FAHRENHEIT): ("Celsius", "Fahrenheit", C_to_Fahrenheit),
    (TempUnit.KELVIN, TempUnit.CELSIUS): ("Kelvin", "Celsius", K_to_celsius),
    (TempUnit.KELVIN, TempUnit.FAHRENHEIT): ("Kelvin", "Fahrenheit", K_to_Fahrenheit),
    (TempUnit.FAHRENHEIT, TempUnit.CELSIUS): ("Fahrenheit", "Celsius", F_to_celsius),
    (TempUnit.FAHRENHEIT, TempUnit.KELVIN): ("Fahrenheit", "Kelvin", F_to_kelvin),
}

HISTORY_FILE = TEMP_HISTORY_FILE


# ============================================================================
# Main Temperature Converter Function
# ============================================================================

class TemperatureConverter(BaseConverter):
    """Temperature converter implementation."""

    name = "TEMPERATURE"
    emoji = ""
    history_file = HISTORY_FILE

    units = {
        TempUnit.CELSIUS: ("Celsius", "°C"),
        TempUnit.KELVIN: ("Kelvin", "K"),
        TempUnit.FAHRENHEIT: ("Fahrenheit", "°F"),
    }

    def convert(self, value: Decimal, from_unit: int, to_unit: int) -> Decimal:
        key = (from_unit, to_unit)
        if key not in temp_conv_funcs:
            raise KeyError("Invalid temperature conversion.")
        _, _, func = temp_conv_funcs[key]
        return func(value)

    def display_menu(self) -> None:
        temp_conv_menuMsg()

    def get_value_prompt(self, unit_name: str) -> str:
        return "\nEnter temperature: "


def display_hist_temp_conv() -> None:
    """Display temperature conversion history."""
    TemperatureConverter().display_history()


def clear_hist_temp_conv() -> None:
    """Clear temperature conversion history."""
    TemperatureConverter().clear_history()

def temperature_converter() -> None:
    """Main temperature conversion interface."""
    try:
        TemperatureConverter().run()
    except (CalculatorError):
        raise
