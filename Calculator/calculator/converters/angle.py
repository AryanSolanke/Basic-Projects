"""
Angle converter.

Features:
- Degree, radian, and gradian conversions.
- High-precision Decimal arithmetic for stable results.
- Local history file recording for conversions.
"""

from decimal import Decimal, localcontext
from typing import Tuple, Callable, Dict
from enum import IntEnum

from calculator.exceptions import CalculatorError, NullInputError, InvalidInputError
from calculator.converters.converter_utils import get_numeric_input, format_numeric_result, to_decimal
from calculator.config import ANGLE_HISTORY_FILE


INTERNAL_PRECISION = 60
HISTORY_FILE = ANGLE_HISTORY_FILE


def _compute_pi() -> Decimal:
    """
    Compute PI using the Gauss-Legendre algorithm.

    Returns:
        PI with INTERNAL_PRECISION decimal digits.
    """
    with localcontext() as ctx:
        ctx.prec = INTERNAL_PRECISION
        a = Decimal(1)
        b = Decimal(1) / Decimal(2).sqrt()
        t = Decimal(1) / Decimal(4)
        p = Decimal(1)
        for _ in range(7):
            an = (a + b) / 2
            b = (a * b).sqrt()
            t = t - p * (a - an) * (a - an)
            a = an
            p = p * 2
        return (a + b) * (a + b) / (Decimal(4) * t)


PI = _compute_pi()


class AngleUnit(IntEnum):
    """Angle unit types."""
    DEGREE = 1
    RADIAN = 2
    GRADIAN = 3
    QUIT = 4


# ============================================================================
# Menu Display Functions
# ============================================================================

def angle_conversion_menuMsg() -> None:
    """Display angle conversion menu."""
    print("\n" + "="*50)
    print("ANGLE CONVERSION")
    print("="*50)
    print("1. Degree (°)")
    print("2. Radian (rad)")
    print("3. Gradian (grad)")
    print("4. Quit Angle Converter")
    print("="*50)


# ============================================================================
# Angle Conversion Functions
# ============================================================================

def to_rads(angle: Decimal) -> Decimal:
    """Convert degrees to radians."""
    return to_decimal(angle, "Angle") * PI / Decimal(180)


def to_deg(angle: Decimal) -> Decimal:
    """Convert radians to degrees."""
    return to_decimal(angle, "Angle") * Decimal(180) / PI


def to_grad(angle: Decimal) -> Decimal:
    """Convert degrees to gradians."""
    return to_decimal(angle, "Angle") * Decimal(200) / Decimal(180)


def convert_angle(
    name1: str,
    func1: Callable[[Decimal], Decimal],
    name2: str,
    func2: Callable[[Decimal], Decimal],
    angle: Decimal,
) -> Tuple[str, str]:
    """
    Convert a single input into two unit representations.

    Returns formatted strings for display and history recording.
    """
    ans1 = f"{name1}({angle}) = {format_numeric_result(func1(angle))}"
    ans2 = f"{name2}({angle}) = {format_numeric_result(func2(angle))}"
    return ans1, ans2


def record_history_angle_conv(unit_name: str, angle: Decimal, ans1: str, ans2: str) -> None:
    """Append angle conversion to history file."""
    try:
        with HISTORY_FILE.open("a", encoding="utf-8") as f:
            f.write(f"{unit_name}({angle}) -> {ans1} | {ans2}\n")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError):
        print("Internal Error: Failed to record angle history")


def display_hist_angle_conv() -> None:
    """Display angle conversion history from file."""
    try:
        if not HISTORY_FILE.exists():
            print("No angle conversion history available.")
            return

        history = HISTORY_FILE.read_text(encoding="utf-8").strip()
        if not history:
            print("Angle conversion history is empty.")
            return

        print("\n--- Angle Conversion History ---")
        print(history)
    except (PermissionError, UnicodeDecodeError, OSError):
        print("Internal Error: Failed reading angle history")


def clear_hist_angle_conv() -> None:
    """Clear angle conversion history by truncating the history file."""
    try:
        HISTORY_FILE.write_text("", encoding="utf-8")
        print("Angle conversion history cleared successfully!")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError):
        print("Internal Error: Failed to clear angle history")


# ============================================================================
# Conversion Lookup Tables
# ============================================================================

angle_conv_choices = ["Degree", "Radians", "Gradians"]

# Angle conversion configurations: (output1_name, func1, output2_name, func2)
angle_conv_funcs: Dict[int, Tuple[str, Callable, str, Callable]] = {
    AngleUnit.DEGREE: ("rad", to_rads, "grad", to_grad),
    AngleUnit.RADIAN: ("deg", to_deg, "grad", to_grad),
    AngleUnit.GRADIAN: ("deg", to_deg, "rad", to_rads),
}


# ============================================================================
# Main Angle Converter Function
# ============================================================================

def angle_converter() -> None:
    """Main angle conversion interface."""
    try:
        angle_conversion_menuMsg()
        choice = int(input("\nEnter your choice: "))

        if choice == AngleUnit.QUIT:
            return

        if choice in angle_conv_funcs:
            name1, func1, name2, func2 = angle_conv_funcs[choice]
            unit_name = angle_conv_choices[choice - 1]
            print(f"\nEnter angle in {unit_name}: ", end="")
            angle = get_numeric_input()

            if angle is not None:
                ans1, ans2 = convert_angle(name1, func1, name2, func2, angle)
                record_history_angle_conv(unit_name, angle, ans1, ans2)
                print(f"\n   {ans1}")
                print(f"   {ans2}\n")
            else:
                raise NullInputError()
    
    except ValueError:
        raise InvalidInputError("Invalid choice: Please select 1-3\n")
    except (TypeError, CalculatorError):
        raise
