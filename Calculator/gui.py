"""Desktop UI for the advanced calculator."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext, ttk

from config import SCI_HISTORY_FILE, STD_HISTORY_FILE
from converters.angle import AngleConverter
from converters.base import BaseConverter
from converters.data import DataConverter
from converters.pressure import PressureConverter
from converters.temperature import TemperatureConverter
from converters.weight import WeightConverter
from exceptions import CalculatorError
from programmer import (
    WORD_SIZE_LABELS,
    WordSize,
    _parse_int,
    bin_to_dec,
    bitwise_and,
    bitwise_nand,
    bitwise_nor,
    bitwise_not,
    bitwise_or,
    bitwise_xnor,
    bitwise_xor,
    get_word_size,
    hex_to_dec,
    oct_to_dec,
    rotate_left,
    rotate_left_carry,
    rotate_right,
    rotate_right_carry,
    set_word_size,
    shift_arithmetic_left,
    shift_arithmetic_right,
    shift_logical_left,
    shift_logical_right,
    show_all_bases_map,
)
from scientific import trigo_funcs, validate_and_eval
from scientific_parts.core import FunctionCategory
from standard import compute_expression


PALETTE = {
    "bg": "#101820",
    "panel": "#152430",
    "card": "#F3E7D5",
    "card_alt": "#E7D6C1",
    "text": "#1F1A14",
    "muted": "#665B4F",
    "accent": "#C96F33",
    "accent_dark": "#8B4513",
    "secondary": "#18485A",
    "secondary_dark": "#0F2E3A",
    "line": "#D4B898",
    "entry": "#FFF9F0",
    "white": "#FFFDF8",
}

TITLE_FONT = ("Bahnschrift", 28, "bold")
SUBTITLE_FONT = ("Bahnschrift", 11)
CARD_TITLE_FONT = ("Bahnschrift", 17, "bold")
BODY_FONT = ("Bahnschrift", 12)
SMALL_FONT = ("Bahnschrift", 10)
DISPLAY_FONT = ("Bahnschrift", 26, "bold")
CODE_FONT = ("Consolas", 12)


@dataclass(frozen=True)
class ScientificCategory:
    """UI metadata for scientific calculator categories."""

    title: str
    op_num: int
    hint: str


SCIENTIFIC_CATEGORIES = [
    ScientificCategory("Trig", FunctionCategory.TRIGONOMETRIC, "Angles are interpreted in degrees."),
    ScientificCategory("Inv Trig", FunctionCategory.INVERSE_TRIGONOMETRIC, "Enter x where inverse trig is defined."),
    ScientificCategory("Hyper", FunctionCategory.HYPERBOLIC, "Enter any real value for the hyperbolic functions."),
    ScientificCategory("Inv Hyper", FunctionCategory.INVERSE_HYPERBOLIC, "Enter x inside the valid inverse hyperbolic domain."),
]

PROGRAMMER_WORD_BUTTONS = [
    ("QWORD", WordSize.QWORD),
    ("DWORD", WordSize.DWORD),
    ("WORD", WordSize.WORD),
    ("BYTE", WordSize.BYTE),
]

PROGRAMMER_BASE_MODES = ("Auto", "DEC", "HEX", "BIN", "OCT")
PROGRAMMER_BITWISE_OPS = ("AND", "OR", "XOR", "NOT", "NAND", "NOR", "XNOR")
PROGRAMMER_SHIFT_OPS = ("ASL", "ASR", "LSL", "LSR", "ROL", "ROR", "RCL", "RCR")

ButtonCommand = Callable[[], object]
BinaryIntOperation = Callable[[int, int], int]


def make_button(
    parent: tk.Misc,
    text: str,
    command: ButtonCommand,
    *,
    variant: str = "primary",
    width: int | None = None,
) -> tk.Button:
    """Create a consistently styled button."""
    styles = {
        "primary": (PALETTE["accent"], PALETTE["white"], PALETTE["accent_dark"]),
        "secondary": (PALETTE["secondary"], PALETTE["white"], PALETTE["secondary_dark"]),
        "neutral": (PALETTE["card_alt"], PALETTE["text"], PALETTE["line"]),
    }
    bg, fg, active_bg = styles[variant]
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=active_bg,
        activeforeground=fg,
        relief="flat",
        bd=0,
        padx=12,
        pady=9,
        font=BODY_FONT,
        cursor="hand2",
    )
    if width is not None:
        button.configure(width=width)
    return button


def make_card(parent: tk.Misc, title: str, subtitle: str = "") -> tuple[tk.Frame, tk.Frame]:
    """Create a styled card with a title and content frame."""
    card = tk.Frame(
        parent,
        bg=PALETTE["card"],
        highlightbackground=PALETTE["line"],
        highlightthickness=1,
        bd=0,
    )
    header = tk.Frame(card, bg=PALETTE["card"])
    header.pack(fill="x", padx=18, pady=(16, 6))

    tk.Label(
        header,
        text=title,
        bg=PALETTE["card"],
        fg=PALETTE["text"],
        font=CARD_TITLE_FONT,
    ).pack(anchor="w")
    if subtitle:
        tk.Label(
            header,
            text=subtitle,
            bg=PALETTE["card"],
            fg=PALETTE["muted"],
            font=SMALL_FONT,
        ).pack(anchor="w", pady=(2, 0))

    body = tk.Frame(card, bg=PALETTE["card"])
    body.pack(fill="both", expand=True, padx=18, pady=(0, 18))
    return card, body


def set_text(widget: scrolledtext.ScrolledText, content: str) -> None:
    """Replace the contents of a read-only text widget."""
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.insert("1.0", content)
    widget.configure(state="disabled")


def read_history(path: Path, empty_message: str) -> str:
    """Read a history file with a UI-friendly fallback message."""
    try:
        if not path.exists():
            return empty_message
        content = path.read_text(encoding="utf-8").strip()
        return content if content else empty_message
    except OSError as exc:
        return f"Unable to read history: {exc}"


def clear_history(path: Path) -> None:
    """Clear a history file without printing to the terminal."""
    path.write_text("", encoding="utf-8")


def require_history_path(converter: BaseConverter) -> Path:
    """Return a converter history path with a non-optional type for the UI."""
    history_path = converter.history_file
    if history_path is None:
        raise ValueError(f"{converter.name.title()} history is not configured.")
    return history_path


def parse_decimal(raw: str, field_name: str) -> Decimal:
    """Parse a Decimal from text for UI forms."""
    if not raw.strip():
        raise ValueError(f"{field_name} is required.")
    try:
        return Decimal(raw.strip())
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be numeric.") from exc


def parse_decimal_int(raw: str, field_name: str) -> int:
    """Parse a base-10 integer from text for UI forms."""
    if not raw.strip():
        raise ValueError(f"{field_name} is required.")
    try:
        return int(raw.strip(), 10)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a base-10 integer.") from exc


class StandardPanel(tk.Frame):
    """Standard calculator tab."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, bg=PALETTE["bg"])
        self.expression_var = tk.StringVar()
        self.result_var = tk.StringVar(value="0")
        self.feedback_var = tk.StringVar(value="Safe expression evaluator with persistent history.")
        self.expression_entry: tk.Entry
        self.history_text: scrolledtext.ScrolledText
        self._build()
        self.refresh_history()

    def _build(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        calc_card, calc_body = make_card(
            self,
            "Standard Calculator",
            "Keyboard input is supported. Press Enter or use the on-screen keypad.",
        )
        calc_card.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)

        history_card, history_body = make_card(
            self,
            "History",
            "Expressions are written to the same history file used by the CLI.",
        )
        history_card.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)

        display_frame = tk.Frame(calc_body, bg=PALETTE["panel"], padx=16, pady=16)
        display_frame.pack(fill="x", pady=(0, 14))

        tk.Label(
            display_frame,
            text="Result",
            bg=PALETTE["panel"],
            fg=PALETTE["card_alt"],
            font=SMALL_FONT,
        ).pack(anchor="w")
        tk.Label(
            display_frame,
            textvariable=self.result_var,
            bg=PALETTE["panel"],
            fg=PALETTE["white"],
            font=DISPLAY_FONT,
            anchor="e",
            justify="right",
        ).pack(fill="x", pady=(4, 12))

        self.expression_entry = tk.Entry(
            display_frame,
            textvariable=self.expression_var,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=("Consolas", 16),
            relief="flat",
            bd=0,
            justify="right",
        )
        self.expression_entry.pack(fill="x", ipady=10)
        self.expression_entry.bind("<Return>", lambda _event: self.evaluate())

        action_row = tk.Frame(calc_body, bg=PALETTE["card"])
        action_row.pack(fill="x", pady=(0, 12))
        make_button(action_row, "Evaluate", self.evaluate).pack(side="left")
        make_button(action_row, "Clear", self.clear_expression, variant="neutral").pack(side="left", padx=8)
        make_button(action_row, "Backspace", self.backspace, variant="secondary").pack(side="left")

        keypad = tk.Frame(calc_body, bg=PALETTE["card"])
        keypad.pack(fill="both", expand=True)
        layout = [
            ["(", ")", "//", "DEL"],
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "%", "+"],
            ["**", "C", "=", " "],
        ]
        for row_index, row in enumerate(layout):
            keypad.rowconfigure(row_index, weight=1)
            for col_index, token in enumerate(row):
                keypad.columnconfigure(col_index, weight=1)
                if token == " ":
                    spacer = tk.Frame(keypad, bg=PALETTE["card"])
                    spacer.grid(row=row_index, column=col_index, padx=6, pady=6, sticky="nsew")
                    continue
                if token == "=":
                    command = self.evaluate
                    variant = "primary"
                elif token in {"DEL", "C"}:
                    command = self.backspace if token == "DEL" else self.clear_expression
                    variant = "secondary" if token == "DEL" else "neutral"
                else:
                    command = lambda value=token: self.append_token(value)
                    variant = "neutral"
                make_button(keypad, token, command, variant=variant, width=6).grid(
                    row=row_index,
                    column=col_index,
                    padx=6,
                    pady=6,
                    sticky="nsew",
                )

        tk.Label(
            calc_body,
            textvariable=self.feedback_var,
            bg=PALETTE["card"],
            fg=PALETTE["muted"],
            font=BODY_FONT,
            wraplength=520,
            justify="left",
        ).pack(anchor="w", fill="x", pady=(8, 0))

        history_controls = tk.Frame(history_body, bg=PALETTE["card"])
        history_controls.pack(fill="x", pady=(0, 10))
        make_button(history_controls, "Refresh", self.refresh_history, variant="secondary").pack(side="left")
        make_button(history_controls, "Clear History", self.clear_history, variant="neutral").pack(side="left", padx=8)

        self.history_text = scrolledtext.ScrolledText(
            history_body,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            font=CODE_FONT,
            relief="flat",
            bd=0,
            wrap="word",
        )
        self.history_text.pack(fill="both", expand=True)
        self.history_text.configure(state="disabled")

    def append_token(self, token: str) -> None:
        self.expression_var.set(f"{self.expression_var.get()}{token}")
        self.expression_entry.focus_set()

    def clear_expression(self) -> None:
        self.expression_var.set("")
        self.result_var.set("0")
        self.feedback_var.set("Expression cleared.")

    def backspace(self) -> None:
        expression = self.expression_var.get()
        self.expression_var.set(expression[:-1])
        self.expression_entry.focus_set()

    def evaluate(self) -> None:
        expression = self.expression_var.get()
        try:
            result = compute_expression(expression)
        except (CalculatorError, SyntaxError, InvalidOperation, OverflowError) as exc:
            self.result_var.set("Error")
            self.feedback_var.set(str(exc).strip() or "Unable to evaluate the expression.")
            return

        self.expression_var.set(result)
        self.result_var.set(result)
        self.feedback_var.set(f"{expression} = {result}")
        self.refresh_history()

    def refresh_history(self) -> None:
        set_text(self.history_text, read_history(STD_HISTORY_FILE, "No standard-calculator history yet."))

    def clear_history(self) -> None:
        clear_history(STD_HISTORY_FILE)
        self.feedback_var.set("Standard history cleared.")
        self.refresh_history()


class ScientificPanel(tk.Frame):
    """Scientific calculator tab."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, bg=PALETTE["bg"])
        self.current_category = SCIENTIFIC_CATEGORIES[0]
        self.current_suboperation = 1
        self.value_var = tk.StringVar()
        self.hint_var = tk.StringVar(value=self.current_category.hint)
        self.result_var = tk.StringVar(value="Choose a function, enter a value, and calculate.")
        self.category_buttons: dict[int, tk.Button] = {}
        self.function_buttons: list[tk.Button] = []
        self.history_text: scrolledtext.ScrolledText
        self._build()
        self.refresh_history()
        self._sync_category_buttons()
        self._sync_function_buttons()

    def _build(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        control_card, control_body = make_card(
            self,
            "Scientific Calculator",
            "All scientific functions reuse the validated Decimal-backed engine.",
        )
        control_card.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)

        history_card, history_body = make_card(
            self,
            "History",
            "Successful scientific evaluations are stored here.",
        )
        history_card.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)

        category_row = tk.Frame(control_body, bg=PALETTE["card"])
        category_row.pack(fill="x")
        for category in SCIENTIFIC_CATEGORIES:
            button = make_button(
                category_row,
                category.title,
                lambda item=category: self.select_category(item),
                variant="neutral",
            )
            button.pack(side="left", padx=(0, 8))
            self.category_buttons[category.op_num] = button

        self.function_frame = tk.Frame(control_body, bg=PALETTE["card"])
        self.function_frame.pack(fill="x", pady=(14, 16))
        for index in range(1, 7):
            button = make_button(
                self.function_frame,
                "",
                lambda selected=index: self.select_function(selected),
                variant="neutral",
                width=12,
            )
            button.grid(row=(index - 1) // 3, column=(index - 1) % 3, padx=6, pady=6, sticky="nsew")
            self.function_frame.columnconfigure((index - 1) % 3, weight=1)
            self.function_buttons.append(button)

        input_frame = tk.Frame(control_body, bg=PALETTE["panel"], padx=16, pady=16)
        input_frame.pack(fill="x")
        tk.Label(
            input_frame,
            text="Input",
            bg=PALETTE["panel"],
            fg=PALETTE["card_alt"],
            font=SMALL_FONT,
        ).pack(anchor="w")
        tk.Entry(
            input_frame,
            textvariable=self.value_var,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=("Consolas", 15),
            relief="flat",
            bd=0,
        ).pack(fill="x", ipady=10, pady=(4, 10))
        tk.Label(
            input_frame,
            textvariable=self.hint_var,
            bg=PALETTE["panel"],
            fg=PALETTE["card_alt"],
            font=SMALL_FONT,
            wraplength=540,
            justify="left",
        ).pack(anchor="w")

        action_row = tk.Frame(control_body, bg=PALETTE["card"])
        action_row.pack(fill="x", pady=(14, 12))
        make_button(action_row, "Calculate", self.calculate).pack(side="left")
        make_button(action_row, "Clear Input", self.clear_input, variant="neutral").pack(side="left", padx=8)

        result_panel = tk.Frame(control_body, bg=PALETTE["card_alt"], padx=16, pady=16)
        result_panel.pack(fill="both", expand=True)
        tk.Label(
            result_panel,
            text="Output",
            bg=PALETTE["card_alt"],
            fg=PALETTE["muted"],
            font=SMALL_FONT,
        ).pack(anchor="w")
        tk.Label(
            result_panel,
            textvariable=self.result_var,
            bg=PALETTE["card_alt"],
            fg=PALETTE["text"],
            font=BODY_FONT,
            justify="left",
            wraplength=540,
        ).pack(anchor="w", fill="both", expand=True, pady=(6, 0))

        history_controls = tk.Frame(history_body, bg=PALETTE["card"])
        history_controls.pack(fill="x", pady=(0, 10))
        make_button(history_controls, "Refresh", self.refresh_history, variant="secondary").pack(side="left")
        make_button(history_controls, "Clear History", self.clear_history, variant="neutral").pack(side="left", padx=8)

        self.history_text = scrolledtext.ScrolledText(
            history_body,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            font=CODE_FONT,
            relief="flat",
            bd=0,
            wrap="word",
        )
        self.history_text.pack(fill="both", expand=True)
        self.history_text.configure(state="disabled")

    def select_category(self, category: ScientificCategory) -> None:
        self.current_category = category
        self.current_suboperation = 1
        self.hint_var.set(category.hint)
        self._sync_category_buttons()
        self._sync_function_buttons()

    def select_function(self, suboperation: int) -> None:
        self.current_suboperation = suboperation
        self._sync_function_buttons()

    def _sync_category_buttons(self) -> None:
        for category in SCIENTIFIC_CATEGORIES:
            selected = category.op_num == self.current_category.op_num
            bg = PALETTE["accent"] if selected else PALETTE["card_alt"]
            fg = PALETTE["white"] if selected else PALETTE["text"]
            active = PALETTE["accent_dark"] if selected else PALETTE["line"]
            self.category_buttons[category.op_num].configure(
                bg=bg,
                fg=fg,
                activebackground=active,
                activeforeground=fg,
            )

    def _sync_function_buttons(self) -> None:
        for index, button in enumerate(self.function_buttons, start=1):
            name, _func = trigo_funcs[(self.current_category.op_num, index)]
            selected = index == self.current_suboperation
            bg = PALETTE["secondary"] if selected else PALETTE["card_alt"]
            fg = PALETTE["white"] if selected else PALETTE["text"]
            active = PALETTE["secondary_dark"] if selected else PALETTE["line"]
            button.configure(
                text=name,
                bg=bg,
                fg=fg,
                activebackground=active,
                activeforeground=fg,
            )

    def calculate(self) -> None:
        raw_value = self.value_var.get()
        try:
            value = parse_decimal(raw_value, "Scientific input")
        except ValueError as exc:
            self.result_var.set(str(exc))
            return

        name, func = trigo_funcs[(self.current_category.op_num, self.current_suboperation)]
        self.result_var.set(
            validate_and_eval(
                self.current_category.op_num,
                self.current_suboperation,
                name,
                func,
                value,
            )
        )
        self.refresh_history()

    def clear_input(self) -> None:
        self.value_var.set("")
        self.result_var.set("Choose a function, enter a value, and calculate.")

    def refresh_history(self) -> None:
        set_text(self.history_text, read_history(SCI_HISTORY_FILE, "No scientific history yet."))

    def clear_history(self) -> None:
        clear_history(SCI_HISTORY_FILE)
        self.result_var.set("Scientific history cleared.")
        self.refresh_history()


class ConverterPanel(tk.Frame):
    """Converter tab covering all unit categories."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, bg=PALETTE["bg"])
        self.converters: dict[str, BaseConverter] = {
            "Angle": AngleConverter(),
            "Temperature": TemperatureConverter(),
            "Weight": WeightConverter(),
            "Pressure": PressureConverter(),
            "Data": DataConverter(),
        }
        self.current_converter_name = "Angle"
        self.current_unit_lookup: dict[str, int] = {}
        self.category_buttons: dict[str, tk.Button] = {}
        self.value_var = tk.StringVar()
        self.from_unit_var = tk.StringVar()
        self.to_unit_var = tk.StringVar()
        self.result_var = tk.StringVar(value="Select a converter, choose units, and run the conversion.")
        self.from_combo: ttk.Combobox
        self.to_combo: ttk.Combobox
        self.history_text: scrolledtext.ScrolledText
        self._build()
        self.select_converter("Angle")

    def _build(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        control_card, control_body = make_card(
            self,
            "Unit Converter",
            "Every converter uses the same validated Decimal-based engine as the terminal version.",
        )
        control_card.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)

        history_card, history_body = make_card(
            self,
            "Converter History",
            "History refreshes for the currently selected converter category.",
        )
        history_card.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)

        category_row = tk.Frame(control_body, bg=PALETTE["card"])
        category_row.pack(fill="x")
        for name in self.converters:
            button = make_button(
                category_row,
                name,
                lambda category=name: self.select_converter(category),
                variant="neutral",
            )
            button.pack(side="left", padx=(0, 8))
            self.category_buttons[name] = button

        form = tk.Frame(control_body, bg=PALETTE["panel"], padx=16, pady=16)
        form.pack(fill="x", pady=(14, 14))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Value", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(
            row=0, column=0, sticky="w", columnspan=2
        )
        tk.Entry(
            form,
            textvariable=self.value_var,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=("Consolas", 15),
            relief="flat",
            bd=0,
        ).grid(row=1, column=0, columnspan=2, sticky="ew", ipady=10, pady=(4, 12))

        tk.Label(form, text="From", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(
            row=2, column=0, sticky="w"
        )
        tk.Label(form, text="To", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(
            row=2, column=1, sticky="w"
        )

        self.from_combo = ttk.Combobox(form, textvariable=self.from_unit_var, state="readonly", font=BODY_FONT)
        self.from_combo.grid(row=3, column=0, sticky="ew", pady=(4, 0), padx=(0, 6))
        self.to_combo = ttk.Combobox(form, textvariable=self.to_unit_var, state="readonly", font=BODY_FONT)
        self.to_combo.grid(row=3, column=1, sticky="ew", pady=(4, 0), padx=(6, 0))

        action_row = tk.Frame(control_body, bg=PALETTE["card"])
        action_row.pack(fill="x", pady=(0, 12))
        make_button(action_row, "Convert", self.convert_value).pack(side="left")
        make_button(action_row, "Swap", self.swap_units, variant="secondary").pack(side="left", padx=8)
        make_button(action_row, "Clear Input", self.clear_input, variant="neutral").pack(side="left")

        result_panel = tk.Frame(control_body, bg=PALETTE["card_alt"], padx=16, pady=16)
        result_panel.pack(fill="both", expand=True)
        tk.Label(
            result_panel,
            text="Result",
            bg=PALETTE["card_alt"],
            fg=PALETTE["muted"],
            font=SMALL_FONT,
        ).pack(anchor="w")
        tk.Label(
            result_panel,
            textvariable=self.result_var,
            bg=PALETTE["card_alt"],
            fg=PALETTE["text"],
            font=BODY_FONT,
            justify="left",
            wraplength=540,
        ).pack(anchor="w", fill="both", expand=True, pady=(6, 0))

        history_controls = tk.Frame(history_body, bg=PALETTE["card"])
        history_controls.pack(fill="x", pady=(0, 10))
        make_button(history_controls, "Refresh", self.refresh_history, variant="secondary").pack(side="left")
        make_button(history_controls, "Clear History", self.clear_history, variant="neutral").pack(side="left", padx=8)

        self.history_text = scrolledtext.ScrolledText(
            history_body,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            font=CODE_FONT,
            relief="flat",
            bd=0,
            wrap="word",
        )
        self.history_text.pack(fill="both", expand=True)
        self.history_text.configure(state="disabled")

    @property
    def current_converter(self) -> BaseConverter:
        return self.converters[self.current_converter_name]

    def select_converter(self, name: str) -> None:
        self.current_converter_name = name
        for category_name, button in self.category_buttons.items():
            selected = category_name == name
            bg = PALETTE["accent"] if selected else PALETTE["card_alt"]
            fg = PALETTE["white"] if selected else PALETTE["text"]
            active = PALETTE["accent_dark"] if selected else PALETTE["line"]
            button.configure(bg=bg, fg=fg, activebackground=active, activeforeground=fg)

        converter = self.current_converter
        options: list[str] = []
        self.current_unit_lookup.clear()
        for unit_id, (unit_name, unit_abbrev) in sorted(converter.units.items(), key=lambda item: int(item[0])):
            label = f"{unit_name} ({unit_abbrev})"
            options.append(label)
            self.current_unit_lookup[label] = int(unit_id)

        combo_values = tuple(options)
        self.from_combo.configure(values=combo_values)
        self.to_combo.configure(values=combo_values)
        if options:
            self.from_unit_var.set(options[0])
            self.to_unit_var.set(options[min(1, len(options) - 1)])

        self.result_var.set(f"{name} converter ready.")
        self.refresh_history()

    def convert_value(self) -> None:
        try:
            value = parse_decimal(self.value_var.get(), "Conversion value")
            from_unit = self.current_unit_lookup[self.from_unit_var.get()]
            to_unit = self.current_unit_lookup[self.to_unit_var.get()]
        except KeyError:
            self.result_var.set("Choose both units before converting.")
            return
        except ValueError as exc:
            self.result_var.set(str(exc))
            return

        converter = self.current_converter
        try:
            if from_unit == to_unit:
                result = value
            else:
                result = converter.convert(value, from_unit, to_unit)
        except CalculatorError as exc:
            self.result_var.set(str(exc).strip())
            return

        formatted_result = converter.format_result(result)
        from_name, from_abbrev = converter.units[from_unit]
        to_name, to_abbrev = converter.units[to_unit]
        if from_unit != to_unit:
            converter.record_history(value, from_unit, to_unit, formatted_result)
        self.result_var.set(
            f"{value} {from_abbrev} = {formatted_result} {to_abbrev}\n"
            f"{from_name} -> {to_name}"
        )
        self.refresh_history()

    def swap_units(self) -> None:
        from_value = self.from_unit_var.get()
        to_value = self.to_unit_var.get()
        self.from_unit_var.set(to_value)
        self.to_unit_var.set(from_value)

    def clear_input(self) -> None:
        self.value_var.set("")
        self.result_var.set(f"{self.current_converter_name} converter ready.")

    def refresh_history(self) -> None:
        history_path = require_history_path(self.current_converter)
        empty_message = f"No {self.current_converter_name.lower()} history yet."
        set_text(self.history_text, read_history(history_path, empty_message))

    def clear_history(self) -> None:
        clear_history(require_history_path(self.current_converter))
        self.result_var.set(f"{self.current_converter_name} history cleared.")
        self.refresh_history()


class ProgrammerPanel(tk.Frame):
    """Programmer calculator tab."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, bg=PALETTE["bg"])
        self.base_mode_var = tk.StringVar(value="Auto")
        self.base_input_var = tk.StringVar()
        self.bitwise_op_var = tk.StringVar(value=PROGRAMMER_BITWISE_OPS[0])
        self.bitwise_a_var = tk.StringVar()
        self.bitwise_b_var = tk.StringVar()
        self.shift_op_var = tk.StringVar(value=PROGRAMMER_SHIFT_OPS[0])
        self.shift_value_var = tk.StringVar()
        self.shift_amount_var = tk.StringVar()
        self.shift_carry_var = tk.StringVar(value="0")
        self.output_title_var = tk.StringVar(value="Awaiting programmer-mode input.")
        self.output_dec_var = tk.StringVar(value="-")
        self.output_hex_var = tk.StringVar(value="-")
        self.output_bin_var = tk.StringVar(value="-")
        self.output_oct_var = tk.StringVar(value="-")
        self.carry_var = tk.StringVar(value="Carry out: -")
        self.word_status_var = tk.StringVar(value="")
        self.word_buttons: dict[WordSize, tk.Button] = {}
        self.bitwise_combo: ttk.Combobox
        self.bitwise_a_entry: tk.Entry
        self.bitwise_b_entry: tk.Entry
        self.shift_combo: ttk.Combobox
        self.shift_value_entry: tk.Entry
        self.shift_amount_entry: tk.Entry
        self.shift_carry_entry: tk.Entry
        self._build()
        self._sync_word_buttons()
        self._sync_bitwise_fields()
        self._sync_shift_fields()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        word_card, word_body = make_card(
            self,
            "Programmer Calculator",
            "Base conversion, bitwise logic, and shifts all respect the active word size.",
        )
        word_card.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        button_row = tk.Frame(word_body, bg=PALETTE["card"])
        button_row.pack(fill="x")
        for label, word_size in PROGRAMMER_WORD_BUTTONS:
            button = make_button(
                button_row,
                label,
                lambda size=word_size: self.change_word_size(size),
                variant="neutral",
                width=8,
            )
            button.pack(side="left", padx=(0, 8))
            self.word_buttons[word_size] = button

        tk.Label(
            word_body,
            textvariable=self.word_status_var,
            bg=PALETTE["card"],
            fg=PALETTE["muted"],
            font=BODY_FONT,
        ).pack(anchor="w", pady=(10, 0))

        output_card, output_body = make_card(
            self,
            "Output Registers",
            "Results are displayed simultaneously in DEC, HEX, BIN, and OCT.",
        )
        output_card.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        output_body.columnconfigure(1, weight=1)

        tk.Label(output_body, textvariable=self.output_title_var, bg=PALETTE["card"], fg=PALETTE["text"], font=BODY_FONT).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )
        rows = [
            ("DEC", self.output_dec_var),
            ("HEX", self.output_hex_var),
            ("BIN", self.output_bin_var),
            ("OCT", self.output_oct_var),
        ]
        for row_index, (label, variable) in enumerate(rows, start=1):
            tk.Label(output_body, text=label, bg=PALETTE["card"], fg=PALETTE["muted"], font=SMALL_FONT).grid(
                row=row_index, column=0, sticky="nw", pady=(0, 8)
            )
            tk.Label(
                output_body,
                textvariable=variable,
                bg=PALETTE["card"],
                fg=PALETTE["text"],
                font=CODE_FONT,
                justify="left",
                anchor="w",
                wraplength=980,
            ).grid(row=row_index, column=1, sticky="ew", pady=(0, 8))

        tk.Label(
            output_body,
            textvariable=self.carry_var,
            bg=PALETTE["card"],
            fg=PALETTE["muted"],
            font=SMALL_FONT,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 0))

        notebook = ttk.Notebook(self, style="Inner.TNotebook")
        notebook.grid(row=2, column=0, sticky="nsew", padx=16, pady=(8, 16))

        base_tab = tk.Frame(notebook, bg=PALETTE["bg"])
        bitwise_tab = tk.Frame(notebook, bg=PALETTE["bg"])
        shift_tab = tk.Frame(notebook, bg=PALETTE["bg"])
        notebook.add(base_tab, text="Base Conversion")
        notebook.add(bitwise_tab, text="Bitwise")
        notebook.add(shift_tab, text="Shift + Rotate")

        self._build_base_tab(base_tab)
        self._build_bitwise_tab(bitwise_tab)
        self._build_shift_tab(shift_tab)

    def _build_base_tab(self, tab: tk.Frame) -> None:
        tab.columnconfigure(0, weight=1)
        card, body = make_card(tab, "Base Conversion", "Use Auto to honor prefixes like 0x, 0b, and 0o.")
        card.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        form = tk.Frame(body, bg=PALETTE["panel"], padx=16, pady=16)
        form.pack(fill="x")
        tk.Label(form, text="Input mode", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).pack(anchor="w")
        _base_combo = ttk.Combobox(form, textvariable=self.base_mode_var, state="readonly", values=PROGRAMMER_BASE_MODES, font=BODY_FONT)
        _base_combo.pack(fill="x", pady=(4, 12))
        tk.Label(form, text="Value", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).pack(anchor="w")
        tk.Entry(
            form,
            textvariable=self.base_input_var,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=("Consolas", 15),
            relief="flat",
            bd=0,
        ).pack(fill="x", ipady=10, pady=(4, 0))

        actions = tk.Frame(body, bg=PALETTE["card"])
        actions.pack(fill="x", pady=(14, 0))
        make_button(actions, "Show All Bases", self.convert_base).pack(side="left")
        make_button(actions, "Clear", lambda: self.base_input_var.set(""), variant="neutral").pack(side="left", padx=8)

    def _build_bitwise_tab(self, tab: tk.Frame) -> None:
        tab.columnconfigure(0, weight=1)
        card, body = make_card(tab, "Bitwise Operations", "Prefixes like 0xF0 and 0b1010 are accepted.")
        card.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        form = tk.Frame(body, bg=PALETTE["panel"], padx=16, pady=16)
        form.pack(fill="x")
        tk.Label(form, text="Operation", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(row=0, column=0, sticky="w", columnspan=2)
        self.bitwise_combo = ttk.Combobox(
            form,
            textvariable=self.bitwise_op_var,
            state="readonly",
            values=PROGRAMMER_BITWISE_OPS,
            font=BODY_FONT,
        )
        self.bitwise_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 12))
        self.bitwise_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_bitwise_fields())

        tk.Label(form, text="Value A", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(row=2, column=0, sticky="w")
        tk.Label(form, text="Value B", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(row=2, column=1, sticky="w")
        self.bitwise_a_entry = tk.Entry(
            form,
            textvariable=self.bitwise_a_var,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=("Consolas", 15),
            relief="flat",
            bd=0,
        )
        self.bitwise_a_entry.grid(row=3, column=0, sticky="ew", pady=(4, 0), padx=(0, 6), ipady=10)
        self.bitwise_b_entry = tk.Entry(
            form,
            textvariable=self.bitwise_b_var,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=("Consolas", 15),
            relief="flat",
            bd=0,
        )
        self.bitwise_b_entry.grid(row=3, column=1, sticky="ew", pady=(4, 0), padx=(6, 0), ipady=10)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        actions = tk.Frame(body, bg=PALETTE["card"])
        actions.pack(fill="x", pady=(14, 0))
        make_button(actions, "Run Operation", self.run_bitwise).pack(side="left")
        make_button(actions, "Clear", self.clear_bitwise_fields, variant="neutral").pack(side="left", padx=8)

    def _build_shift_tab(self, tab: tk.Frame) -> None:
        tab.columnconfigure(0, weight=1)
        card, body = make_card(tab, "Shift and Rotate", "Carry is only used for RCL and RCR.")
        card.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        form = tk.Frame(body, bg=PALETTE["panel"], padx=16, pady=16)
        form.pack(fill="x")
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)

        tk.Label(form, text="Operation", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        self.shift_combo = ttk.Combobox(
            form,
            textvariable=self.shift_op_var,
            state="readonly",
            values=PROGRAMMER_SHIFT_OPS,
            font=BODY_FONT,
        )
        self.shift_combo.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 12))
        self.shift_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_shift_fields())

        tk.Label(form, text="Value", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(row=2, column=0, sticky="w")
        tk.Label(form, text="Amount", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(row=2, column=1, sticky="w")
        tk.Label(form, text="Carry", bg=PALETTE["panel"], fg=PALETTE["card_alt"], font=SMALL_FONT).grid(row=2, column=2, sticky="w")

        self.shift_value_entry = tk.Entry(
            form,
            textvariable=self.shift_value_var,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=("Consolas", 15),
            relief="flat",
            bd=0,
        )
        self.shift_value_entry.grid(row=3, column=0, sticky="ew", pady=(4, 0), padx=(0, 6), ipady=10)
        self.shift_amount_entry = tk.Entry(
            form,
            textvariable=self.shift_amount_var,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=("Consolas", 15),
            relief="flat",
            bd=0,
        )
        self.shift_amount_entry.grid(row=3, column=1, sticky="ew", pady=(4, 0), padx=6, ipady=10)
        self.shift_carry_entry = tk.Entry(
            form,
            textvariable=self.shift_carry_var,
            bg=PALETTE["entry"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=("Consolas", 15),
            relief="flat",
            bd=0,
        )
        self.shift_carry_entry.grid(row=3, column=2, sticky="ew", pady=(4, 0), padx=(6, 0), ipady=10)

        actions = tk.Frame(body, bg=PALETTE["card"])
        actions.pack(fill="x", pady=(14, 0))
        make_button(actions, "Run Shift", self.run_shift).pack(side="left")
        make_button(actions, "Clear", self.clear_shift_fields, variant="neutral").pack(side="left", padx=8)

    def change_word_size(self, word_size: WordSize) -> None:
        set_word_size(word_size)
        self._sync_word_buttons()

    def _sync_word_buttons(self) -> None:
        active_size = get_word_size()
        self.word_status_var.set(f"Active word size: {WORD_SIZE_LABELS[active_size]}")
        for word_size, button in self.word_buttons.items():
            selected = word_size == active_size
            bg = PALETTE["accent"] if selected else PALETTE["card_alt"]
            fg = PALETTE["white"] if selected else PALETTE["text"]
            active = PALETTE["accent_dark"] if selected else PALETTE["line"]
            button.configure(bg=bg, fg=fg, activebackground=active, activeforeground=fg)

    def _sync_bitwise_fields(self) -> None:
        uses_second_operand = self.bitwise_op_var.get() != "NOT"
        state = "normal" if uses_second_operand else "disabled"
        self.bitwise_b_entry.configure(state=state)
        if not uses_second_operand:
            self.bitwise_b_var.set("")

    def _sync_shift_fields(self) -> None:
        uses_carry = self.shift_op_var.get() in {"RCL", "RCR"}
        state = "normal" if uses_carry else "disabled"
        self.shift_carry_entry.configure(state=state)
        if not uses_carry:
            self.shift_carry_var.set("0")

    def _update_output(self, title: str, value: int, carry_out: int | None = None) -> None:
        bases = show_all_bases_map(value)
        self.output_title_var.set(title)
        self.output_dec_var.set(bases["DEC"])
        self.output_hex_var.set(bases["HEX"])
        self.output_bin_var.set(bases["BIN"])
        self.output_oct_var.set(bases["OCT"])
        self.carry_var.set("Carry out: -" if carry_out is None else f"Carry out: {carry_out}")

    def convert_base(self) -> None:
        raw = self.base_input_var.get().strip()
        try:
            mode = self.base_mode_var.get()
            if mode == "Auto":
                value = _parse_int(raw)
            elif mode == "DEC":
                value = parse_decimal_int(raw, "Decimal input")
            elif mode == "HEX":
                value = hex_to_dec(raw.removeprefix("0x").removeprefix("0X"))
            elif mode == "BIN":
                value = bin_to_dec(raw.removeprefix("0b").removeprefix("0B").replace(" ", ""))
            else:
                value = oct_to_dec(raw.removeprefix("0o").removeprefix("0O"))
        except (CalculatorError, ValueError) as exc:
            self.output_title_var.set(str(exc).strip() or "Unable to convert the input.")
            return

        self._update_output(f"Base conversion from {self.base_mode_var.get()}", value)

    def run_bitwise(self) -> None:
        try:
            a_value = _parse_int(self.bitwise_a_var.get())
            operation = self.bitwise_op_var.get()
            if operation == "NOT":
                result = bitwise_not(a_value)
                self._update_output(f"NOT {self.bitwise_a_var.get().strip()}", result)
                return

            b_value = _parse_int(self.bitwise_b_var.get())
            operation_map: dict[str, BinaryIntOperation] = {
                "AND": bitwise_and,
                "OR": bitwise_or,
                "XOR": bitwise_xor,
                "NAND": bitwise_nand,
                "NOR": bitwise_nor,
                "XNOR": bitwise_xnor,
            }
            result = operation_map[operation](a_value, b_value)
        except CalculatorError as exc:
            self.output_title_var.set(str(exc).strip())
            return

        self._update_output(
            f"{self.bitwise_a_var.get().strip()} {operation} {self.bitwise_b_var.get().strip()}",
            result,
        )

    def run_shift(self) -> None:
        try:
            value = _parse_int(self.shift_value_var.get())
            amount = parse_decimal_int(self.shift_amount_var.get(), "Shift amount")
            operation = self.shift_op_var.get()
            if operation in {"RCL", "RCR"}:
                carry = parse_decimal_int(self.shift_carry_var.get(), "Carry")
                if carry not in (0, 1):
                    raise ValueError("Carry must be 0 or 1.")
                if operation == "RCL":
                    result, carry_out = rotate_left_carry(value, amount, carry)
                else:
                    result, carry_out = rotate_right_carry(value, amount, carry)
                self._update_output(f"{operation} {self.shift_value_var.get().strip()} by {amount}", result, carry_out)
                return

            operation_map: dict[str, BinaryIntOperation] = {
                "ASL": shift_arithmetic_left,
                "ASR": shift_arithmetic_right,
                "LSL": shift_logical_left,
                "LSR": shift_logical_right,
                "ROL": rotate_left,
                "ROR": rotate_right,
            }
            result = operation_map[operation](value, amount)
        except (CalculatorError, ValueError) as exc:
            self.output_title_var.set(str(exc).strip())
            return

        self._update_output(f"{operation} {self.shift_value_var.get().strip()} by {amount}", result)

    def clear_bitwise_fields(self) -> None:
        self.bitwise_a_var.set("")
        self.bitwise_b_var.set("")

    def clear_shift_fields(self) -> None:
        self.shift_value_var.set("")
        self.shift_amount_var.set("")
        self.shift_carry_var.set("0")


class CalculatorApp(tk.Tk):
    """Top-level desktop application."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Advanced Modular Calculator")
        self.geometry("1380x920")
        self.minsize(1180, 760)
        self.configure(bg=PALETTE["bg"])
        self._configure_styles()
        self._build()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Main.TNotebook",
            background=PALETTE["bg"],
            borderwidth=0,
            tabmargins=(16, 0, 16, 0),
        )
        style.configure(
            "Main.TNotebook.Tab",
            background=PALETTE["panel"],
            foreground=PALETTE["card_alt"],
            padding=(18, 10),
            font=BODY_FONT,
            borderwidth=0,
        )
        style.map(
            "Main.TNotebook.Tab",
            background=[("selected", PALETTE["accent"])],
            foreground=[("selected", PALETTE["white"])],
        )
        style.configure(
            "Inner.TNotebook",
            background=PALETTE["bg"],
            borderwidth=0,
            tabmargins=(12, 0, 12, 0),
        )
        style.configure(
            "Inner.TNotebook.Tab",
            background=PALETTE["panel"],
            foreground=PALETTE["card_alt"],
            padding=(14, 8),
            font=BODY_FONT,
            borderwidth=0,
        )
        style.map(
            "Inner.TNotebook.Tab",
            background=[("selected", PALETTE["secondary"])],
            foreground=[("selected", PALETTE["white"])],
        )
        style.configure("TCombobox", fieldbackground=PALETTE["entry"], background=PALETTE["entry"])

    def _build(self) -> None:
        self._build_header()

        notebook = ttk.Notebook(self, style="Main.TNotebook")
        notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        notebook.add(StandardPanel(notebook), text="Standard")
        notebook.add(ScientificPanel(notebook), text="Scientific")
        notebook.add(ConverterPanel(notebook), text="Converter")
        notebook.add(ProgrammerPanel(notebook), text="Programmer")

    def _build_header(self) -> None:
        canvas = tk.Canvas(self, height=124, bg=PALETTE["bg"], highlightthickness=0, bd=0)
        canvas.pack(fill="x", padx=12, pady=(12, 8))
        canvas.create_rectangle(0, 20, 560, 110, fill=PALETTE["panel"], outline="")
        canvas.create_rectangle(584, 28, 980, 102, fill=PALETTE["accent"], outline="")
        canvas.create_oval(1010, 18, 1120, 128, fill=PALETTE["secondary"], outline="")
        canvas.create_text(
            32,
            38,
            anchor="nw",
            text="Advanced Modular Calculator",
            fill=PALETTE["white"],
            font=TITLE_FONT,
        )
        canvas.create_text(
            34,
            82,
            anchor="nw",
            text="Desktop UI over the existing standard, scientific, converter, and programmer engines.",
            fill=PALETTE["card_alt"],
            font=SUBTITLE_FONT,
        )
        canvas.create_text(
            620,
            56,
            anchor="nw",
            text="No extra dependencies",
            fill=PALETTE["white"],
            font=("Bahnschrift", 14, "bold"),
        )
        canvas.create_text(
            620,
            82,
            anchor="nw",
            text="CLI remains available with --cli",
            fill=PALETTE["white"],
            font=SUBTITLE_FONT,
        )


def launch_gui() -> None:
    """Start the desktop application."""
    app = CalculatorApp()
    app.mainloop()
