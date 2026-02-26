"""
Converter Module - Main Router

Provides angle, temperature, weight, pressure, and data conversion functionality.
Routes to specific converter modules.
"""

from enum import IntEnum

from calculator.utils import errmsg
from calculator.converters.angle import angle_converter
from calculator.converters.temperature import temperature_converter
from calculator.converters.weight import weight_converter
from calculator.converters.pressure import pressure_converter
from calculator.converters.data import data_converter
from calculator.exceptions import CalculatorError

class MenuOptions(IntEnum):
    """Conversion unit types."""
    ANGLE_CONVERSION = 1
    TEMPERATURE_CONVERSION = 2
    WEIGHT_CONVERSION = 3
    PRESSURE_CONVERSION = 4
    DATA_CONVERSION = 5
    QUIT = 6


# ============================================================================
# Menu Display Functions
# ============================================================================

def converter_menuMsg() -> None:
    """Display main converter menu."""
    print("\n" + "="*50)
    print("UNIT CONVERTER")
    print("="*50)
    print("1. Angle Conversion")
    print("2. Temperature Conversion")
    print("3. Weight Conversion")
    print("4. Pressure Conversion")
    print("5. Data Conversion")
    print("6. Quit Converter")
    print("="*50)


# ============================================================================
# Main Converter Function
# ============================================================================

def converter_menu() -> None:
    """Main converter interface. Routes to specific converter modules."""
    while True:
        
        converter_menuMsg()
        try:
            op_num = int(input("\nEnter your choice: "))
        
            if op_num == MenuOptions.QUIT:
                print("\n   Converter menu closed\n")
                break

            if op_num == MenuOptions.ANGLE_CONVERSION:
                angle_converter()
            elif op_num == MenuOptions.TEMPERATURE_CONVERSION:
                temperature_converter()
            elif op_num == MenuOptions.WEIGHT_CONVERSION:
                weight_converter()
            elif op_num == MenuOptions.PRESSURE_CONVERSION:
                pressure_converter()
            elif op_num == MenuOptions.DATA_CONVERSION:
                data_converter()
            else:
                print("Invalid choice: Please select 1-6\n")

        except ValueError:
            print("Invalid value: Please select 1-6\n")
            continue
        except (TypeError, CalculatorError) as e:
            print(f"{e}")
            continue
