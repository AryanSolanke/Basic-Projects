# 🧮 Advanced Modular Calculator

A robust, enterprise-grade Python calculator featuring a desktop UI, a console fallback, modular architecture, comprehensive unit conversions, and extensive mathematical functions. Built with clean code principles, domain-driven design, and test-driven development.

## 🌟 Features Overview

### 📊 Standard Calculator
- **Expression Evaluation**: Evaluates complex arithmetic expressions with full operator precedence
- **Persistent History**: All calculations are saved with file-based storage
- **Error Resilience**: Gracefully handles division by zero, syntax errors, and malformed input
- **Smart Formatting**: Removes trailing zeros and floating-point artifacts

### 🔬 Scientific Calculator
- **24 Engineering Functions**: Complete suite of trigonometric, inverse trigonometric, hyperbolic, and inverse hyperbolic functions
- **Domain Validation**: Explicit mathematical domain checks prevent undefined results
- **High Precision**: Results formatted to 9 significant figures with intelligent rounding
- **O(1) Dispatch**: Dictionary-based function lookup using tuple-key mapping for optimal performance

### 💻 Programmer Calculator
- **Base Conversion**: DEC, HEX, BIN, and OCT conversions with auto-detected input prefixes
- **Bitwise Operations**: AND, OR, XOR, NOT, NAND, NOR, and XNOR
- **Bit Shift Toolkit**: Arithmetic shifts, logical shifts, rotates, and carry rotates (RCL/RCR)
- **Word Size Modes**: BYTE (8-bit), WORD (16-bit), DWORD (32-bit), and QWORD (64-bit)
- **Two's Complement Semantics**: Signed/unsigned masking behavior aligned with programmer-style calculators

### 🔄 Unit Converter
Comprehensive conversion system supporting **5 categories**:

#### 📐 Angle Conversion
- Degrees, Radians, Gradians
- Bidirectional conversions

#### 🌡️ Temperature Conversion  
- Celsius, Kelvin, Fahrenheit
- Full bidirectional support

#### ⚖️ Weight Conversion
- **13 Units**: Kilogram, Gram, Milligram, Centigram, Decigram, Decagram, Hectogram, Metric Tonne, Ounce, Pound, Stone, Short Ton (US), Long Ton (UK)
- **182 Conversion Pairs**: Universal converter handles all unit combinations
- Metric and Imperial systems

#### 💨 Pressure Conversion
- **6 Units**: Atmosphere, Bar, Kilopascal, mmHg, Pascal, PSI
- **30 Conversion Pairs**: Medical, meteorological, and engineering standards
- Commonly used in weather, diving, automotive, and industrial applications

#### 💾 Data Conversion
- **35 Units**: Bits, Bytes, Nibbles, KB/KiB, MB/MiB, GB/GiB, TB/TiB, PB/PiB, EB/EiB, ZB/ZiB, YB/YiB
- **1,190 Conversion Pairs**: Covers both decimal (SI) and binary (IEC) standards
- Understand the difference between GB (1000³) and GiB (1024³)
- Perfect for computer science, networking, and data storage calculations

## 🎯 Key Technical Highlights

### Architecture
- **Modular Design**: Clear separation of concerns (standard, scientific, programmer, converters)
- **Flat Layout**: Core modules live at the repo root with grouped subpackages for converters and scientific/programmer internals
- **Stable Imports**: `calculator.*` imports still work through a lightweight root shim
- **Zero Dependencies**: Pure Python implementation (except testing)

### Mathematical Correctness
- **Domain Guarding**: Every function validates input domains
  - `sin⁻¹(x)` → valid only for -1 ≤ x ≤ 1
  - `sec(x)` → undefined at 90° + n·180°
  - `coth(x)` → undefined at x = 0
- **Precision Handling**: Deterministic formatting with no floating-point junk
- **Error Messages**: Clear, human-readable feedback instead of crashes

### Performance
- **O(1) Function Dispatch**: Tuple-key dictionary mapping eliminates long if-else chains
- **Universal Converters**: Single function handles all unit pairs efficiently
- **Minimal Overhead**: Direct mathematical operations with no unnecessary abstraction

### Code Quality
- **Type Hints**: Full type annotations throughout codebase
- **Docstrings**: Comprehensive documentation for all public functions
- **Consistent Style**: PEP 8 compliant with standardized formatting
- **Error Handling**: Defensive programming with graceful degradation

## 📁 Project Structure

```
Calculator/
│
├── calculator.py               # Import shim preserving `calculator.*`
├── gui.py                      # Tkinter desktop application
├── main.py                     # Application entry point
├── standard.py                 # Standard arithmetic engine
├── scientific.py               # Scientific functions engine
├── programmer.py               # Programmer calculator engine
├── router.py                   # Unit converter router
├── config.py                   # Central configuration
├── exceptions.py               # Custom exceptions
├── utils.py                    # Shared utilities
├── setup.py                     # Installable package metadata
├── requirements.txt             # Runtime dependencies (none)
├── requirements-dev.txt         # Dev tools (pytest, ruff, mypy, etc.)
├── history/                      # Calculator history files (ignored in git)
│
├── converters/                 # Converter modules
│   ├── __init__.py
│   ├── base.py                 # Base converter class
│   ├── converter_utils.py      # Shared converter utilities
│   ├── angle.py                # Angle conversions
│   ├── temperature.py          # Temperature conversions
│   ├── weight.py               # Weight conversions
│   ├── pressure.py             # Pressure conversions
│   └── data.py                 # Data unit conversions (35 units)
│
├── programmer_parts/           # Programmer-mode internals
│   ├── __init__.py
│   └── operations.py
│
├── scientific_parts/           # Scientific-mode internals
│   ├── __init__.py
│   ├── core.py
│   ├── functions.py
│   ├── history.py
│   └── validators.py
│
└── tests/                      # Comprehensive test suite
    ├── test_std.py            # Standard calculator tests
    ├── test_sci.py            # Scientific calculator tests
    ├── test_programmer.py     # Programmer calculator tests
    └── test_conveter/         # Converter tests
        ├── test_angle.py
        ├── test_temperature.py
        ├── test_weight.py
        └── test_pressure.py
```

## 🚀 Installation & Usage

### Prerequisites
- Python 3.10 or higher
- No external dependencies for running the calculator
- pytest required for running tests (optional)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AryanSolanke/Calculator.git
   cd Calculator
   ```

2. **Run the calculator**:
   ```bash
   python main.py
   ```
   This launches the desktop UI by default.

   Use the legacy console mode when needed:
   ```bash
   python main.py --cli
   ```

   Or install the console entry point:
   ```bash
   calculator
   ```

3. **Run tests** (optional):
   ```bash
   python -m pytest -v
   ```

### Usage Examples

#### Standard Calculator
```
➤ Enter expression (e.g., 2+3*4): (2 + 3) * 5 / (7 - 2)
✅ Result: 5
```

#### Scientific Calculator
```
➤ Enter operation number: 1
➤ Enter sub-operation number: 1
📐 Enter angle in degrees: 30
✅ Result: sin(30°) = 0.5
```

#### Unit Converter - Data Conversion
```
💾 DATA UNIT CONVERSION
➤ Enter FROM unit (1-35): 24
➤ Enter TO unit (1-35): 25
💾 Enter data amount: 500

✅ CONVERSION RESULT:
   500.0 GB = 465.66 GiB
   (Gigabyte → Gibibyte)
```

#### Programmer Calculator - Bitwise Workflow
```
PROGRAMMER CALCULATOR [QWORD (64-bit)]
1. Base Conversion
2. Bitwise Operations
3. Bit Shift
4. Toggle Word Size
5. Quit Programmer Calculator

➤ Enter choice: 2
➤ Enter value A: 0xF0
➤ Enter value B: 0b1010

Result:
  DEC : 0
  HEX : 0
  BIN : 0000 ... 0000
  OCT : 0
```

## 🧪 Testing

The project includes 352 automated tests covering:
- ✅ Normal operations and edge cases
- ✅ Domain violations and error handling
- ✅ Boundary values and extreme inputs
- ✅ Round-trip conversion accuracy
- ✅ Symmetry and mathematical properties

### Test Coverage
- **Standard Calculator**: Expression evaluation, history management, error handling
- **Scientific Calculator**: All 24 functions across all quadrants, domain validation
- **Programmer Calculator**: Base conversions, bitwise logic, shifts/rotations, and word-size masking
- **Converters**: Accuracy verification, bidirectional consistency, unit validation

### Running Tests
```bash
# Run all tests
python -m pytest -v

# Run specific test file
python -m pytest tests/test_std.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 🔧 Technical Details

### Converter Capabilities

#### Data Converter - Understanding SI vs IEC Standards

**Why does my 500 GB hard drive show only 465 GB?**

- **Hard Drive Label**: 500 GB (Decimal/SI)
  - Uses base 1000: 500,000,000,000 bytes
  
- **Operating System**: Shows 465.66 GiB (Binary/IEC)
  - Uses base 1024: 500,000,000,000 ÷ 1,073,741,824 = 465.66 GiB

**No space is missing - just different measurement systems!**

The data converter handles:
- **Decimal units (SI)**: KB, MB, GB, TB, PB, EB, ZB, YB (powers of 1000)
- **Binary units (IEC)**: KiB, MiB, GiB, TiB, PiB, EiB, ZiB, YiB (powers of 1024)

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Clean modular software architecture
- ✅ Defensive programming for mathematical systems
- ✅ Domain-driven design principles
- ✅ Test-driven development methodology
- ✅ Package organization and import management
- ✅ User experience design with clear feedback
- ✅ Performance optimization through algorithmic design

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **Standard Library**: math, pathlib, enum, typing
- **Testing**: pytest framework
- **Architecture**: Modular, function-dispatch based
- **Code Style**: PEP 8 compliant

## 📋 Recent Updates

### Version 2.4 - Flat Layout Cleanup (Current)
- ✅ **Single Calculator Layer**: Removed the nested `calculator/` package directory from the repo layout
- ✅ **Root Module Layout**: Core modules now live directly under the project root
- ✅ **Stable Imports Preserved**: Added `calculator.py` so existing `calculator.*` imports still resolve cleanly
- ✅ **Package Metadata Updated**: `setup.py` now packages the flat layout explicitly
- ✅ **Pytest Bootstrap Added**: Local test config stabilizes import resolution and temp-directory handling

### Version 2.3 - Programmer Mode Expansion
- ✅ **Programmer Calculator Added**: New dedicated mode integrated into `main.py`
- ✅ **Bitwise Toolkit**: Added AND/OR/XOR/NOT/NAND/NOR/XNOR support
- ✅ **Shift + Rotate Support**: Added ASL/ASR/LSL/LSR/ROL/ROR/RCL/RCR operations
- ✅ **Word Size Control**: Added BYTE/WORD/DWORD/QWORD toggling with signed masking
- ✅ **Test Coverage Added**: New `tests/test_programmer.py` for programmer-mode behavior

### Version 2.2 - Package Reorganization
- ✅ **Proper Package Layout**: Introduced grouped modules and subpackages for clearer boundaries
- ✅ **Central Config**: History files and precision settings consolidated in `config.py`
- ✅ **Base Converter**: Shared converter behavior in `converters/base.py`
- ✅ **History Directory**: History files stored under `history/` at repo root

### Version 2.0 - Major Refactor
- ✅ **Modular Converter Architecture**: Separated converters into independent modules
- ✅ **Enhanced User Interface**: Added emojis and improved formatting for better UX
- ✅ **Standardized Documentation**: Consistent docstrings and comments across all modules
- ✅ **Import System Overhaul**: Resolved all import conflicts with proper package structure
- ✅ **Expanded Unit Support**: Added pressure conversions (6 units, 30 conversion pairs)
- ✅ **Code Quality**: Standardized commenting style, improved error messages
- ✅ **Test Coverage**: Broad automated coverage added for core and converter flows

## 📝 Code Quality Standards

### Docstring Format
```python
def function_name(param: type) -> return_type:
    """
    Brief description of function purpose.
    
    Detailed explanation of behavior and any important notes.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ErrorType: When this error occurs
    """
```

### Error Handling Pattern
```python
try:
    # Main operation
    result = operation()
except SpecificError:
    # Handle specific error
    errmsg()
except Exception:
    # Fallback handler
    errmsg()
```

## 🤝 Contributing

Contributions are welcome! Please ensure:
1. All tests pass before submitting PR
2. New features include corresponding tests
3. Code follows PEP 8 style guide
4. Docstrings are provided for all functions
5. No external dependencies added without discussion

## 📄 License

MIT. See the repository root LICENSE.

## 🙏 Acknowledgments

Built with rigorous attention to mathematical correctness, code quality, and user experience. This project serves as a comprehensive example of professional Python development practices.

---

**Built with precision, tested with rigor, designed with care.** 🎯

**Total Conversion Capabilities**: 1,440 unique conversions across 5 converter categories.
