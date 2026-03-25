"""Scientific Calculator Module.

Public API compatibility layer with orchestration logic.
Implementation is split across:
- scientific_parts/core.py
- scientific_parts/functions.py
- scientific_parts/validators.py
- scientific_parts/history.py
"""

from decimal import Decimal, InvalidOperation
from textwrap import dedent
from typing import Callable, Optional, Tuple

from calculator.config import SCI_HISTORY_FILE
from calculator.exceptions import CalculatorError, InvalidInputError
from calculator.scientific_parts.core import (
    ANGLE_TOLERANCE,
    RESULT_PRECISION,
    FunctionCategory,
    NumberLike,
    SciOperation,
    SubOperation,
    _to_decimal,
    format_result,
)
from calculator.scientific_parts.functions import (
    cosec,
    cosec_inv,
    cosech,
    cosech_inv,
    cosine,
    cosine_inv,
    cosineh,
    cosineh_inv,
    cot,
    cot_inv as _cot_inv_impl,
    coth,
    coth_inv,
    sec,
    sec_inv,
    sech,
    sech_inv,
    sine,
    sine_inv,
    sineh,
    sineh_inv,
    tangent,
    tangent_inv as _tangent_inv_impl,
    tangenth,
    tangenth_inv,
)
from calculator.scientific_parts.history import (
    clear_hist_sci_calc as _clear_history_impl,
    display_hist_sci_calc as _display_history_impl,
    record_history_sci_calc as _record_history_impl,
)
from calculator.scientific_parts.validators import (
    validate_hyperbolic_asymptote as _validate_hyperbolic_asymptote,
    validate_inverse_hyperbolic_domain as _validate_inverse_hyperbolic_domain,
    validate_inverse_trig_domain as _validate_inverse_trig_domain,
    validate_trig_asymptote as _validate_trig_asymptote,
)

HISTORY_FILE = SCI_HISTORY_FILE


def tangent_inv(val: NumberLike) -> Decimal:
    """Return arctan in degrees with fast handling for the slow ±1 series case."""
    val_dec = _to_decimal(val)
    if val_dec == 1:
        return Decimal(45)
    if val_dec == -1:
        return Decimal(-45)
    return _tangent_inv_impl(val_dec)


def cot_inv(val: NumberLike) -> Decimal:
    """Return arccot in degrees with fast handling for the slow ±1 reciprocal case."""
    val_dec = _to_decimal(val)
    if val_dec == 1:
        return Decimal(45)
    if val_dec == -1:
        return Decimal(-45)
    return _cot_inv_impl(val_dec)


def sci_calc_menuMsg() -> None:
    """Display scientific calculator menu with all functions."""
    print(
        dedent(
            """
                |============================>Operations<============================|\n

                1. Basic trigo functions
                    │──1.1 sin(x)
                    │──1.2 cos(x)
                    │──1.3 tan(x)
                    │──1.4 cot(x)
                    │──1.5 sec(x)
                    │──1.6 cosec(x)

                2. Inverse trigo functions
                    │──2.1 sin⁻¹(x)
                    │──2.2 cos⁻¹(x)
                    │──2.3 tan⁻¹(x)
                    │──2.4 cot⁻¹(x)
                    │──2.5 sec⁻¹(x)
                    │──2.6 cosec⁻¹(x)

                3. Hyperbolic trigo functions
                    │──3.1 sinh(x)
                    │──3.2 cosh(x)
                    │──3.3 tanh(x)
                    │──3.4 coth(x)
                    │──3.5 sech(x)
                    │──3.6 cosech(x)

                4. Inverse Hyperbolic trigo functions
                    │──4.1 sinh⁻¹(x)
                    │──4.2 cosh⁻¹(x)
                    │──4.3 tanh⁻¹(x)
                    │──4.4 coth⁻¹(x)
                    │──4.5 sech⁻¹(x)
                    │──4.6 cosech⁻¹(x)

                5. Show operations.
                6. Show history.
                7. Clear history.
                8. Quit scientific calculator.
                |====================================================================|
"""
        )
    )


def get_val() -> Optional[Decimal]:
    """Prompt user for numeric input with error handling."""
    try:
        val = Decimal(input().strip())
        return val
    except (InvalidOperation, ValueError, TypeError):
        raise InvalidInputError("Invalid Value: Please use numbers only.")


def display_hist_sci_calc() -> None:
    """Display calculation history from file."""
    _display_history_impl(HISTORY_FILE)


def record_history_sci_calc(name: str, val: NumberLike, answer: str) -> None:
    """Append calculation to history file."""
    _record_history_impl(name, val, answer, HISTORY_FILE)


def clear_hist_sci_calc() -> None:
    """Clear all history by truncating the history file."""
    _clear_history_impl(HISTORY_FILE)


def validate_subOpNum(sub_op_num: int) -> int:
    """Validate sub-operation number."""
    if 1 <= sub_op_num <= 6:
        return 1
    print("Invalid Choice: Please select 1-6")
    return 0


trigo_funcs: dict[Tuple[int, int], Tuple[str, Callable[[NumberLike], Decimal]]] = {
    (FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_1): ("sin", sine),
    (FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_2): ("cos", cosine),
    (FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_3): ("tan", tangent),
    (FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_4): ("cot", cot),
    (FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_5): ("sec", sec),
    (FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_6): ("cosec", cosec),
    (FunctionCategory.HYPERBOLIC, SubOperation.FUNC_1): ("sinh", sineh),
    (FunctionCategory.HYPERBOLIC, SubOperation.FUNC_2): ("cosh", cosineh),
    (FunctionCategory.HYPERBOLIC, SubOperation.FUNC_3): ("tanh", tangenth),
    (FunctionCategory.HYPERBOLIC, SubOperation.FUNC_4): ("coth", coth),
    (FunctionCategory.HYPERBOLIC, SubOperation.FUNC_5): ("sech", sech),
    (FunctionCategory.HYPERBOLIC, SubOperation.FUNC_6): ("cosech", cosech),
    (FunctionCategory.INVERSE_TRIGONOMETRIC, SubOperation.FUNC_1): ("sin⁻¹", sine_inv),
    (FunctionCategory.INVERSE_TRIGONOMETRIC, SubOperation.FUNC_2): ("cos⁻¹", cosine_inv),
    (FunctionCategory.INVERSE_TRIGONOMETRIC, SubOperation.FUNC_3): ("tan⁻¹", tangent_inv),
    (FunctionCategory.INVERSE_TRIGONOMETRIC, SubOperation.FUNC_4): ("cot⁻¹", cot_inv),
    (FunctionCategory.INVERSE_TRIGONOMETRIC, SubOperation.FUNC_5): ("sec⁻¹", sec_inv),
    (FunctionCategory.INVERSE_TRIGONOMETRIC, SubOperation.FUNC_6): ("cosec⁻¹", cosec_inv),
    (FunctionCategory.INVERSE_HYPERBOLIC, SubOperation.FUNC_1): ("sinh⁻¹", sineh_inv),
    (FunctionCategory.INVERSE_HYPERBOLIC, SubOperation.FUNC_2): ("cosh⁻¹", cosineh_inv),
    (FunctionCategory.INVERSE_HYPERBOLIC, SubOperation.FUNC_3): ("tanh⁻¹", tangenth_inv),
    (FunctionCategory.INVERSE_HYPERBOLIC, SubOperation.FUNC_4): ("coth⁻¹", coth_inv),
    (FunctionCategory.INVERSE_HYPERBOLIC, SubOperation.FUNC_5): ("sech⁻¹", sech_inv),
    (FunctionCategory.INVERSE_HYPERBOLIC, SubOperation.FUNC_6): ("cosech⁻¹", cosech_inv),
}


def validate_and_eval(
    op_num: int,
    sub_op_num: int,
    name: str,
    func: Callable[[Decimal], Decimal],
    val: NumberLike,
) -> str:
    """Validate input domain and execute scientific calculation."""
    try:
        if op_num == FunctionCategory.TRIGONOMETRIC:
            _validate_trig_asymptote(sub_op_num, val)
        elif op_num == FunctionCategory.HYPERBOLIC:
            _validate_hyperbolic_asymptote(sub_op_num, val)
        elif op_num == FunctionCategory.INVERSE_TRIGONOMETRIC:
            _validate_inverse_trig_domain(sub_op_num, val)
            if sub_op_num == SubOperation.FUNC_4 and _to_decimal(val) == 0:
                return f"{name}({val}) = 90"
        elif op_num == FunctionCategory.INVERSE_HYPERBOLIC:
            _validate_inverse_hyperbolic_domain(sub_op_num, val)

        result = func(_to_decimal(val))
        formatted_result = format_result(result)
        record_history_sci_calc(name, val, formatted_result)
        return f"{name}({val}) = {formatted_result}"

    except CalculatorError as e:
        return str(e)
    except (ValueError, ArithmeticError) as e:
        return f"Math Error: {e}"
    except Exception as e:
        return f"System Error: {type(e).__name__}"


def eval_trigo_func(key: Tuple[int, int]) -> None:
    """Evaluate scientific function based on user input."""
    try:
        if key not in trigo_funcs:
            print("Invalid Key Error: Please select a correct pair of main_menu and sub_menu options.")

        op_num, sub_op_num = key
        name, func = trigo_funcs[key]

        print("Enter angle:" if op_num == FunctionCategory.TRIGONOMETRIC else "Enter value: ", end="")
        val = get_val()
        if val is not None:
            answer = validate_and_eval(op_num, sub_op_num, name, func, val)
            print(answer)

    except CalculatorError:
        raise
    except Exception:
        raise


def sci_calc() -> None:
    """Scientific calculator interface loop."""
    while True:
        try:
            op_num = int(input("\nEnter operation number: "))

            if op_num in (
                SciOperation.TRIG,
                SciOperation.INVERSE_TRIG,
                SciOperation.HYPERBOLIC,
                SciOperation.INVERSE_HYPERBOLIC,
            ):
                sub_op_num = int(input("Enter sub-operation number: "))

                if validate_subOpNum(sub_op_num) == 0:
                    continue

                key = (op_num, sub_op_num)
                eval_trigo_func(key)

            elif op_num == SciOperation.SHOW_MENU:
                sci_calc_menuMsg()

            elif op_num == SciOperation.SHOW_HISTORY:
                display_hist_sci_calc()

            elif op_num == SciOperation.CLEAR_HISTORY:
                clear_hist_sci_calc()

            elif op_num == SciOperation.QUIT:
                print("\n Scientific calculator closed!\n")
                break
            else:
                print("Invalid Input: Please select 1-9")

        except CalculatorError as e:
            print(e)
            continue
        except (ValueError, TypeError):
            print("Invalid input: Please use numbers only.")
            continue
        except Exception as e:
            print(f"System Error: {type(e).__name__}")
            continue


