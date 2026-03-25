"""
Advanced Modular Calculator - Main Entry Point

Desktop-first calculator entry point with a CLI fallback.
"""

import argparse
from enum import IntEnum

from calculator.standard import (
    errmsg,
    std_calc
)
from calculator.scientific import (
    sci_calc,
    sci_calc_menuMsg,
)
from calculator.router import converter_menu
from calculator.programmer import programmer_calc


class MainMode(IntEnum):
    """Main calculator modes."""
    STANDARD   = 1
    SCIENTIFIC = 2
    CONVERTER  = 3
    PROGRAMMER = 4
    QUIT       = 5


# ============================================================================
# Menu Display Functions
# ============================================================================

def mode_choice_menu() -> None:
    """Display main menu options."""
    print("\n" + "="*50)
    print("ADVANCED MODULAR CALCULATOR")
    print("="*50)
    print("1. Standard Calculator")
    print("2. Scientific Calculator")
    print("3. Unit Converter")
    print("4. Programmer Calculator")
    print("5. Quit Calculator")
    print("="*50)


# ============================================================================
# CLI Entry Point
# ============================================================================

def cli_main() -> None:
    """Run the legacy console calculator."""
    print("\n" + "="*50)
    print("   Welcome to Advanced Modular Calculator!")
    print("="*50)
    
    try:
        while True:
            mode_choice_menu()
            try:
                mode_choice = int(input("\nSelect a mode: "))
            except (ValueError, TypeError):
                errmsg()
                continue

            if mode_choice == MainMode.STANDARD:
                std_calc()

            elif mode_choice == MainMode.SCIENTIFIC:
                sci_calc_menuMsg()
                sci_calc()

            elif mode_choice == MainMode.CONVERTER:
                converter_menu()

            elif mode_choice == MainMode.PROGRAMMER:
                programmer_calc()

            elif mode_choice == MainMode.QUIT:
                print("\n" + "="*50)
                print("   Thank you for using Calculator!")
                print("="*50 + "\n")
                break
            else:
                errmsg()

    except (KeyboardInterrupt, EOFError):
        print("\nProgram interrupted by user. Thank you for using Calculator!")


def main(argv: list[str] | None = None) -> None:
    """
    Launch the desktop UI by default.

    Use ``--cli`` to force the legacy console interface.
    """
    parser = argparse.ArgumentParser(
        description="Advanced Modular Calculator",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run the legacy console interface instead of the desktop UI.",
    )
    args = parser.parse_args(argv)

    if args.cli:
        cli_main()
        return

    try:
        from tkinter import TclError
    except ImportError:
        TclError = RuntimeError

    try:
        from calculator.gui import launch_gui
        launch_gui()
    except (ImportError, TclError) as exc:
        print(f"\nGUI unavailable ({exc}). Falling back to CLI mode.\n")
        cli_main()


if __name__ == '__main__':
    main()


