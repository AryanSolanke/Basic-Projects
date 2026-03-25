"""
Comprehensive Test Suite for sci.py

This module provides extensive unit tests for the scientific calculator module,
covering trignometric, hyperbolic, inverse functions with domain validation.

Testing strategy:
1. Domain validation - Test all domain boundaries 
2. Mathematical correctness - Verify computational accuracy
3. Error handling - Domain erros, asymptotes, edge cases
4. Special values - Zero, infinity, very large/small numbers
5. Symmetry - Test function properties (even/odd)
6. Range validation - Ensure outputs are within expected ranges

Standards:
- pytest framework
- Type hints for all test functions
- Parametrized tests for efficiency
- Property-based testing concepts
"""

import pytest
import math
from decimal import Decimal
from typing import Callable, Tuple, Generator
from pathlib import Path
import tempfile

from calculator.scientific import (
    # Utility functions
    get_val,
    format_result,
    validate_subOpNum,
    validate_and_eval,
    
    # Trigonometric functions
    sine as sci_sine,
    cosine as sci_cosine,
    tangent as sci_tangent,
    cot as sci_cot,
    sec as sci_sec,
    cosec as sci_cosec,
    
    # Inverse trigonometric functions
    sine_inv as sci_sine_inv,
    cosine_inv as sci_cosine_inv,
    tangent_inv as sci_tangent_inv,
    cot_inv as sci_cot_inv,
    sec_inv as sci_sec_inv,
    cosec_inv as sci_cosec_inv,
    
    # Hyperbolic functions
    sineh as sci_sineh,
    cosineh as sci_cosineh,
    tangenth as sci_tangenth,
    coth as sci_coth,
    sech as sci_sech,
    cosech as sci_cosech,
    
    # Inverse hyperbolic functions
    sineh_inv as sci_sineh_inv,
    cosineh_inv as sci_cosineh_inv,
    tangenth_inv as sci_tangenth_inv,
    coth_inv as sci_coth_inv,
    sech_inv as sci_sech_inv,
    cosech_inv as sci_cosech_inv,
    
    # Constants and enums
    FunctionCategory,
    SubOperation,
    RESULT_PRECISION,
    ANGLE_TOLERANCE,
    
    # History functions
    display_hist_sci_calc,
    record_history_sci_calc,
    clear_hist_sci_calc,
)

def _to_float(value):
    return float(value) if isinstance(value, Decimal) else value


def _wrap(func):
    return lambda *args, **kwargs: _to_float(func(*args, **kwargs))


sine = _wrap(sci_sine)
cosine = _wrap(sci_cosine)
tangent = _wrap(sci_tangent)
cot = _wrap(sci_cot)
sec = _wrap(sci_sec)
cosec = _wrap(sci_cosec)

sine_inv = _wrap(sci_sine_inv)
cosine_inv = _wrap(sci_cosine_inv)
tangent_inv = _wrap(sci_tangent_inv)
cot_inv = _wrap(sci_cot_inv)
sec_inv = _wrap(sci_sec_inv)
cosec_inv = _wrap(sci_cosec_inv)

sineh = _wrap(sci_sineh)
cosineh = _wrap(sci_cosineh)
tangenth = _wrap(sci_tangenth)
coth = _wrap(sci_coth)
sech = _wrap(sci_sech)
cosech = _wrap(sci_cosech)

sineh_inv = _wrap(sci_sineh_inv)
cosineh_inv = _wrap(sci_cosineh_inv)
tangenth_inv = _wrap(sci_tangenth_inv)
coth_inv = _wrap(sci_coth_inv)
sech_inv = _wrap(sci_sech_inv)
cosech_inv = _wrap(sci_cosech_inv)

# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def temp_sci_history_file(monkeypatch) -> Generator[Path, None, None]:
    """Create temporary history file for isolated testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='_sci.txt', delete=False) as tmp:
        temp_file = Path(tmp.name)
    monkeypatch.setattr('calculator.scientific.HISTORY_FILE', temp_file)
    yield temp_file
    if temp_file.exists():
        temp_file.unlink()


# ============================================================================
# Test Utility Functions
# ============================================================================

class TestUtilityFunctions:
    """Test suite for utility functions."""
    
    def test_format_result_precision(self) -> None:
        """
        Test that format_result uses correct precision.
        
        Input: Pi to many decimals
        Expected: 9 significant figures
        """
        result = format_result(math.pi)
        assert result == "3.14159265"
    
    def test_format_result_removes_trailing_zeros(self) -> None:
        """
        Test removal of trailing zeros.
        
        Input: 5.0
        Expected: "5"
        """
        assert format_result(5.0) == "5"
    
    def test_format_result_very_small_number(self) -> None:
        """
        Test formatting of very small numbers.
        
        Input: 1e-12
        Expected: Scientific notation or very small decimal
        """
        result = format_result(1e-12)
        assert result != "0"
    
    def test_format_result_very_large_number(self) -> None:
        """
        Test formatting of very large numbers.
        
        Input: 1e12
        Expected: "1000000000000" or "1e+12"
        """
        result = format_result(1e12)
        assert "1" in result
    
    def test_validate_subOpNum_valid_range(self) -> None:
        """
        Test that valid sub-operation numbers (1-6) are accepted.
        
        Inputs: 1, 2, 3, 4, 5, 6
        Expected: All return 1
        """
        for i in range(1, 7):
            assert validate_subOpNum(i) == 1
    
    def test_validate_subOpNum_invalid_numbers(self, capsys) -> None:
        """
        Test that invalid sub-operation numbers are rejected.
        
        Inputs: 0, 7, -1, 100
        Expected: All return 0 with error message
        """
        for invalid in [0, 7, -1, 100]:
            result = validate_subOpNum(invalid)
            assert result == 0
    
    @pytest.mark.parametrize("value", [1, 2, 3, 4, 5, 6])
    def test_validate_subOpNum_parametrized_valid(self, value: int) -> None:
        """Parametrized test for valid sub-operation numbers."""
        assert validate_subOpNum(value) == 1
    
    @pytest.mark.parametrize("value", [0, 7, -1, 10, 100, -5])
    def test_validate_subOpNum_parametrized_invalid(self, value: int) -> None:
        """Parametrized test for invalid sub-operation numbers."""
        assert validate_subOpNum(value) == 0


# ============================================================================
# Test Trigonometric Functions
# ============================================================================

class TestTrigonometricFunctions:
    """Test suite for standard trigonometric functions."""
    
    # Sine function tests
    def test_sine_standard_angles(self) -> None:
        """
        Test sine at standard angles.
        
        Inputs: 0°, 30°, 45°, 60°, 90°
        Expected: 0, 0.5, √2/2, √3/2, 1
        """
        assert abs(sine(0) - 0) < 1e-9
        assert abs(sine(30) - 0.5) < 1e-9
        assert abs(sine(45) - math.sqrt(2)/2) < 1e-9
        assert abs(sine(60) - math.sqrt(3)/2) < 1e-9
        assert abs(sine(90) - 1) < 1e-9
    
    def test_sine_negative_angle(self) -> None:
        """
        Test sine with negative angles (odd function).
        
        Property: sin(-x) = -sin(x)
        """
        angle = 30
        assert abs(sine(-angle) - (-sine(angle))) < 1e-9
    
    def test_sine_periodicity(self) -> None:
        """
        Test sine periodicity.
        
        Property: sin(x) = sin(x + 360°)
        """
        angle = 45
        assert abs(sine(angle) - sine(angle + 360)) < 1e-9
    
    def test_sine_range(self) -> None:
        """
        Test that sine stays within [-1, 1].
        
        Test angles: 0° to 360° in 15° steps
        Expected: All values in [-1, 1]
        """
        for angle in range(0, 361, 15):
            value = sine(angle)
            assert -1 <= value <= 1
    
    # Cosine function tests
    def test_cosine_standard_angles(self) -> None:
        """Test cosine at standard angles."""
        assert abs(cosine(0) - 1) < 1e-9
        assert abs(cosine(60) - 0.5) < 1e-9
        assert abs(cosine(90) - 0) < 1e-9
    
    def test_cosine_negative_angle(self) -> None:
        """
        Test cosine with negative angles (even function).
        
        Property: cos(-x) = cos(x)
        """
        angle = 45
        assert abs(cosine(-angle) - cosine(angle)) < 1e-9
    
    # Tangent function tests
    def test_tangent_standard_angles(self) -> None:
        """Test tangent at standard angles."""
        assert abs(tangent(0) - 0) < 1e-9
        assert abs(tangent(45) - 1) < 1e-9
    
    def test_tangent_asymptote_detection(self) -> None:
        """
        Test that tangent detects asymptotes at 90°, 270°.
        
        Inputs: 90, -90, 270
        Expected: Asymptote error messages
        """
        result_90 = validate_and_eval(
            FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_3,
            "tan", tangent, 90
        )
        assert "Asymptote" in result_90 or "divide by zero" in result_90.lower()
    
    # Cotangent function tests
    def test_cot_standard_angles(self) -> None:
        """Test cotangent at standard angles."""
        assert abs(cot(45) - 1) < 1e-9
    
    def test_cot_asymptote_at_zero(self) -> None:
        """
        Test cotangent asymptote at 0°, 180°.
        
        Expected: Asymptote error
        """
        result = validate_and_eval(
            FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_4,
            "cot", cot, 0
        )
        assert "Asymptote" in result or "divide by zero" in result.lower()
    
    # Secant function tests
    def test_sec_at_zero(self) -> None:
        """Test secant at 0° equals 1."""
        assert abs(sec(0) - 1) < 1e-9
    
    def test_sec_asymptote_at_90(self) -> None:
        """Test secant asymptote at 90°."""
        result = validate_and_eval(
            FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_5,
            "sec", sec, 90
        )
        assert "Asymptote" in result or "divide by zero" in result.lower()
    
    # Cosecant function tests
    def test_cosec_at_90(self) -> None:
        """Test cosecant at 90° equals 1."""
        assert abs(cosec(90) - 1) < 1e-9
    
    def test_cosec_asymptote_at_zero(self) -> None:
        """Test cosecant asymptote at 0°."""
        result = validate_and_eval(
            FunctionCategory.TRIGONOMETRIC, SubOperation.FUNC_6,
            "cosec", cosec, 0
        )
        assert "Asymptote" in result or "divide by zero" in result.lower()
    
    @pytest.mark.parametrize("angle,expected_sin", [
        (0, 0),
        (30, 0.5),
        (90, 1),
        (180, 0),
        (270, -1),
    ])
    def test_sine_parametrized(self, angle: float, expected_sin: float) -> None:
        """Parametrized sine tests."""
        assert abs(sine(angle) - expected_sin) < 1e-9


# ============================================================================
# Test Inverse Trigonometric Functions
# ============================================================================

class TestInverseTrigonometricFunctions:
    """Test suite for inverse trigonometric functions."""
    
    def test_sine_inv_domain_valid(self) -> None:
        """
        Test arcsin with valid domain [-1, 1].
        
        Inputs: -1, 0, 0.5, 1
        Expected: Valid angle outputs
        """
        assert abs(sine_inv(0) - 0) < 1e-9
        assert abs(sine_inv(0.5) - 30) < 1e-6
        assert abs(sine_inv(1) - 90) < 1e-9
    
    def test_sine_inv_domain_invalid(self) -> None:
        """
        Test arcsin rejects values outside [-1, 1].
        
        Inputs: -1.5, 1.5, 2
        Expected: Domain error messages
        """
        for invalid in [-1.5, 1.5, 2]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_TRIGONOMETRIC,
                SubOperation.FUNC_1,
                "sin⁻¹", sine_inv, invalid
            )
            assert "Domain Error" in result
    
    def test_sine_inv_returns_degrees(self) -> None:
        """
        Test that arcsin returns degrees, not radians.
        
        Input: 1
        Expected: 90 (not π/2 ≈ 1.57)
        """
        result = sine_inv(1)
        assert abs(result - 90) < 1e-9
        assert result > 10  # Definitely degrees
    
    def test_cosine_inv_domain_valid(self) -> None:
        """Test arccos with valid domain."""
        assert abs(cosine_inv(1) - 0) < 1e-9
        assert abs(cosine_inv(0) - 90) < 1e-9
    
    def test_cosine_inv_domain_invalid(self) -> None:
        """Test arccos rejects invalid domain."""
        result = validate_and_eval(
            FunctionCategory.INVERSE_TRIGONOMETRIC,
            SubOperation.FUNC_2,
            "cos⁻¹", cosine_inv, 1.5
        )
        assert "Domain Error" in result
    
    def test_tangent_inv_all_reals(self) -> None:
        """
        Test that arctan accepts all real numbers.
        
        Inputs: -1000, 0, 1000
        Expected: All valid
        """
        for val in [-1000, 0, 1000]:
            result = tangent_inv(val)
            assert -90 < result < 90

    def test_tangent_inv_exact_one(self) -> None:
        """atan(1) should resolve promptly to 45 degrees."""
        assert abs(tangent_inv(1) - 45) < 1e-9

    def test_cot_inv_special_case_zero(self) -> None:
        """
        Test that cot⁻¹(0) = 90°.
        
        Input: 0
        Expected: Exactly 90
        """
        result = validate_and_eval(
            FunctionCategory.INVERSE_TRIGONOMETRIC,
            SubOperation.FUNC_4,
            "cot⁻¹", cot_inv, 0
        )
        assert "90" in result

    def test_cot_inv_exact_one(self) -> None:
        """acot(1) should resolve promptly to 45 degrees."""
        assert abs(cot_inv(1) - 45) < 1e-9
    
    def test_sec_inv_domain_valid(self) -> None:
        """Test arcsec with |x| >= 1."""
        result = validate_and_eval(
            FunctionCategory.INVERSE_TRIGONOMETRIC,
            SubOperation.FUNC_5,
            "sec⁻¹", sec_inv, 2
        )
        assert "Domain Error" not in result
    
    def test_sec_inv_domain_invalid(self) -> None:
        """Test arcsec rejects |x| < 1."""
        result = validate_and_eval(
            FunctionCategory.INVERSE_TRIGONOMETRIC,
            SubOperation.FUNC_5,
            "sec⁻¹", sec_inv, 0.5
        )
        assert "Domain Error" in result
    
    def test_cosec_inv_domain(self) -> None:
        """Test arccosec domain validation."""
        # Valid: |x| >= 1
        valid_result = validate_and_eval(
            FunctionCategory.INVERSE_TRIGONOMETRIC,
            SubOperation.FUNC_6,
            "cosec⁻¹", cosec_inv, 2
        )
        assert "Domain Error" not in valid_result
        
        # Invalid: |x| < 1
        invalid_result = validate_and_eval(
            FunctionCategory.INVERSE_TRIGONOMETRIC,
            SubOperation.FUNC_6,
            "cosec⁻¹", cosec_inv, 0.5
        )
        assert "Domain Error" in invalid_result
    
    @pytest.mark.parametrize("value,in_domain", [
        (-1.0, True),
        (-0.5, True),
        (0.0, True),
        (0.5, True),
        (1.0, True),
        (-1.1, False),
        (1.1, False),
    ])
    def test_sine_inv_domain_parametrized(
        self, value: float, in_domain: bool
    ) -> None:
        """Parametrized domain test for arcsin."""
        result = validate_and_eval(
            FunctionCategory.INVERSE_TRIGONOMETRIC,
            SubOperation.FUNC_1,
            "sin⁻¹", sine_inv, value
        )
        if in_domain:
            assert "Domain Error" not in result
        else:
            assert "Domain Error" in result


# ============================================================================
# Test Hyperbolic Functions
# ============================================================================

class TestHyperbolicFunctions:
    """Test suite for hyperbolic functions."""
    
    def test_sineh_at_zero(self) -> None:
        """
        Test sinh(0) = 0.
        
        Input: 0
        Expected: 0
        """
        assert abs(sineh(0) - 0) < 1e-9
    
    def test_sineh_odd_function(self) -> None:
        """
        Test that sinh is odd: sinh(-x) = -sinh(x).
        
        Input: x = 2
        Expected: sinh(-2) = -sinh(2)
        """
        x = 2
        assert abs(sineh(-x) - (-sineh(x))) < 1e-9
    
    def test_cosineh_at_zero(self) -> None:
        """
        Test cosh(0) = 1.
        
        Input: 0
        Expected: 1
        """
        assert abs(cosineh(0) - 1) < 1e-9
    
    def test_cosineh_even_function(self) -> None:
        """
        Test that cosh is even: cosh(-x) = cosh(x).
        
        Input: x = 2
        Expected: cosh(-2) = cosh(2)
        """
        x = 2
        assert abs(cosineh(-x) - cosineh(x)) < 1e-9
    
    def test_cosineh_always_positive(self) -> None:
        """
        Test that cosh(x) >= 1 for all x.
        
        Test values: -10, -1, 0, 1, 10
        Expected: All >= 1
        """
        for x in [-10, -1, 0, 1, 10]:
            assert cosineh(x) >= 1
    
    def test_tangenth_range(self) -> None:
        """
        Test that tanh(x) ∈ (-1, 1) with asymptotic behavior.
        
        Test values: Small and large
        Expected: Strictly in (-1,1) for small, approaches ±1 for large
        """
        # For moderate values, strictly in open interval
        for x in [-10, -1, 0, 1, 10]:
            value = tangenth(x)
            assert -1 < value < 1
        
        # For very large values, approaches boundaries
        for x in [-100, 100]:
            value = tangenth(x)
            assert -1 <= value <= 1  # May equal boundaries due to float precision
            assert abs(abs(value) - 1) < 1e-10
    
    def test_coth_asymptote_at_zero(self) -> None:
        """
        Test that coth(0) is undefined.
        
        Input: 0
        Expected: Asymptote error
        """
        result = validate_and_eval(
            FunctionCategory.HYPERBOLIC,
            SubOperation.FUNC_4,
            "coth", coth, 0
        )
        assert "Undefined" in result or "divide by zero" in result.lower()
    
    def test_sech_at_zero(self) -> None:
        """
        Test sech(0) = 1.
        
        Input: 0
        Expected: 1
        """
        assert abs(sech(0) - 1) < 1e-9
    
    def test_sech_range(self) -> None:
        """
        Test that sech(x) ∈ (0, 1].
        
        Test values: -5, -1, 0, 1, 5
        Expected: All in (0, 1]
        """
        for x in [-5, -1, 0, 1, 5]:
            value = sech(x)
            assert 0 < value <= 1
    
    def test_cosech_asymptote_at_zero(self) -> None:
        """
        Test that cosech(0) is undefined.
        
        Input: 0
        Expected: Asymptote error
        """
        result = validate_and_eval(
            FunctionCategory.HYPERBOLIC,
            SubOperation.FUNC_6,
            "cosech", cosech, 0
        )
        assert "Undefined" in result or "divide by zero" in result.lower()
    
    def test_hyperbolic_identity(self) -> None:
        """
        Test hyperbolic identity: cosh²(x) - sinh²(x) = 1.
        
        Test values: 0, 1, 2, 5
        Expected: Identity holds within tolerance
        """
        for x in [0, 1, 2, 5]:
            cosh_sq = cosineh(x) ** 2
            sinh_sq = sineh(x) ** 2
            assert abs((cosh_sq - sinh_sq) - 1) < 1e-9


# ============================================================================
# Test Inverse Hyperbolic Functions
# ============================================================================

class TestInverseHyperbolicFunctions:
    """Test suite for inverse hyperbolic functions."""
    
    def test_sineh_inv_all_reals(self) -> None:
        """
        Test that asinh accepts all real numbers.
        
        Inputs: -1000, 0, 1000
        Expected: All valid
        """
        for val in [-1000, 0, 1000]:
            result = sineh_inv(val)
            assert isinstance(result, float)
    
    def test_sineh_inv_at_zero(self) -> None:
        """
        Test asinh(0) = 0.
        
        Input: 0
        Expected: 0
        """
        assert abs(sineh_inv(0) - 0) < 1e-9
    
    def test_cosineh_inv_domain_valid(self) -> None:
        """
        Test acosh with x >= 1.
        
        Inputs: 1, 2, 10
        Expected: Valid results
        """
        for val in [1, 2, 10]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_HYPERBOLIC,
                SubOperation.FUNC_2,
                "cosh⁻¹", cosineh_inv, val
            )
            assert "Domain Error" not in result
    
    def test_cosineh_inv_domain_invalid(self) -> None:
        """
        Test acosh rejects x < 1.
        
        Inputs: 0, 0.5, -1
        Expected: Domain errors
        """
        for val in [0, 0.5, -1]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_HYPERBOLIC,
                SubOperation.FUNC_2,
                "cosh⁻¹", cosineh_inv, val
            )
            assert "Domain Error" in result
    
    def test_tangenth_inv_domain_valid(self) -> None:
        """
        Test atanh with x ∈ (-1, 1).
        
        Inputs: 0, 0.5, -0.5
        Expected: Valid results
        """
        for val in [0, 0.5, -0.5]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_HYPERBOLIC,
                SubOperation.FUNC_3,
                "tanh⁻¹", tangenth_inv, val
            )
            assert "Domain Error" not in result
    
    def test_tangenth_inv_domain_invalid(self) -> None:
        """
        Test atanh rejects x at boundaries ±1.
        
        Inputs: -1, 1, 2
        Expected: Domain errors
        """
        for val in [-1, 1, 2]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_HYPERBOLIC,
                SubOperation.FUNC_3,
                "tanh⁻¹", tangenth_inv, val
            )
            assert "Domain Error" in result
    
    def test_coth_inv_domain(self) -> None:
        """
        Test acoth domain |x| > 1.
        
        Valid: 2, -2
        Invalid: 0, 0.5, -0.5
        """
        # Valid
        for val in [2, -2]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_HYPERBOLIC,
                SubOperation.FUNC_4,
                "coth⁻¹", coth_inv, val
            )
            assert "Domain Error" not in result
        
        # Invalid
        for val in [0, 0.5, -0.5]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_HYPERBOLIC,
                SubOperation.FUNC_4,
                "coth⁻¹", coth_inv, val
            )
            assert "Domain Error" in result
    
    def test_sech_inv_domain(self) -> None:
        """
        Test asech domain x ∈ (0, 1].
        
        Valid: 0.5, 1
        Invalid: 0, -0.5, 1.5
        """
        # Valid
        for val in [0.5, 1]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_HYPERBOLIC,
                SubOperation.FUNC_5,
                "sech⁻¹", sech_inv, val
            )
            assert "Domain Error" not in result
        
        # Invalid
        for val in [0, -0.5, 1.5]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_HYPERBOLIC,
                SubOperation.FUNC_5,
                "sech⁻¹", sech_inv, val
            )
            assert "Domain Error" in result
    
    def test_cosech_inv_domain(self) -> None:
        """
        Test acosech undefined at x = 0.
        
        Valid: ±1, ±2
        Invalid: 0
        """
        # Valid
        for val in [-2, -1, 1, 2]:
            result = validate_and_eval(
                FunctionCategory.INVERSE_HYPERBOLIC,
                SubOperation.FUNC_6,
                "cosech⁻¹", cosech_inv, val
            )
            assert "Domain Error" not in result
        
        # Invalid
        result = validate_and_eval(
            FunctionCategory.INVERSE_HYPERBOLIC,
            SubOperation.FUNC_6,
            "cosech⁻¹", cosech_inv, 0
        )
        assert "Domain Error" in result


# ============================================================================
# Test Inverse Relationships
# ============================================================================

class TestInverseRelationships:
    """Test that inverse functions correctly invert their counterparts."""
    
    def test_sine_sine_inv_identity(self) -> None:
        """
        Test sin(arcsin(x)) = x for x ∈ [-1, 1].
        
        Inputs: -1, -0.5, 0, 0.5, 1
        Expected: Round-trip gives original value
        """
        for x in [-1, -0.5, 0, 0.5, 1]:
            angle = sine_inv(x)
            result = sine(angle)
            assert abs(result - x) < 1e-9
    
    def test_sinh_sineh_inv_identity(self) -> None:
        """
        Test sinh(asinh(x)) = x.
        
        Inputs: -5, 0, 5
        Expected: Round-trip gives original value
        """
        for x in [-5, 0, 5]:
            result = sineh(sineh_inv(x))
            assert abs(result - x) < 1e-9
    
    def test_cosh_cosineh_inv_identity(self) -> None:
        """
        Test cosh(acosh(x)) = x for x >= 1.
        
        Inputs: 1, 2, 5
        Expected: Round-trip gives original value
        """
        for x in [1, 2, 5]:
            result = cosineh(cosineh_inv(x))
            assert abs(result - x) < 1e-6


# ============================================================================
# Test Edge Cases and Special Values
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_large_angle(self) -> None:
        """
        Test trigonometric functions with very large angles.
        
        Input: 1,000,000°
        Expected: Valid result due to periodicity
        """
        result = sine(1_000_000)
        assert -1 <= result <= 1
    
    def test_very_small_angle(self) -> None:
        """
        Test trigonometric functions with very small angles.
        
        Input: 0.0001°
        Expected: sin(x) ≈ x for small x (in radians)
        """
        result = sine(0.0001)
        assert abs(result) < 0.01
    
    def test_negative_angles(self) -> None:
        """
        Test that negative angles are handled correctly.
        
        Input: -45°
        Expected: Valid result
        """
        result = sine(-45)
        assert -1 <= result <= 1
    
    def test_hyperbolic_large_values(self) -> None:
        """
        Test hyperbolic functions don't overflow with reasonable inputs.
        
        Input: sinh(20)
        Expected: Valid large number
        """
        result = sineh(20)
        assert result > 0
        assert math.isfinite(result)
    
    def test_hyperbolic_small_values(self) -> None:
        """
        Test hyperbolic functions with very small inputs.
        
        Input: sinh(0.001)
        Expected: ≈ 0.001 (small angle approximation)
        """
        result = sineh(0.001)
        assert abs(result - 0.001) < 0.0001


# ============================================================================
# Test History Functions
# ============================================================================

class TestHistoryFunctions:
    """Test suite for history management."""
    
    def test_record_history(self, temp_sci_history_file) -> None:
        """
        Test that calculations are recorded to history.
        
        Action: Record a calculation
        Expected: File contains the entry
        """
        record_history_sci_calc("sin", 45, "0.707106781")
        content = temp_sci_history_file.read_text()
        assert "sin(45) = 0.707106781" in content
    
    def test_clear_history(self, temp_sci_history_file, capsys) -> None:
        """
        Test that clear_hist_sci_calc empties the file.
        
        Action: Record then clear
        Expected: File is empty
        """
        record_history_sci_calc("cos", 0, "1")
        clear_hist_sci_calc()
        assert temp_sci_history_file.read_text() == ""
        captured = capsys.readouterr()
        assert "cleared successfully" in captured.out


# ============================================================================
# Test Error Messages
# ============================================================================

class TestErrorMessages:
    """Test that appropriate error messages are returned."""
    
    def test_asymptote_error_format(self) -> None:
        """
        Test asymptote error messages are descriptive.
        
        Input: tan(90)
        Expected: Error message mentions asymptote
        """
        result = validate_and_eval(
            FunctionCategory.TRIGONOMETRIC,
            SubOperation.FUNC_3,
            "tan", tangent, 90
        )
        assert "Error" in result
        assert "90" in result or "Asymptote" in result
    
    def test_domain_error_format(self) -> None:
        """
        Test domain error messages are descriptive.
        
        Input: arcsin(2)
        Expected: Error message mentions domain
        """
        result = validate_and_eval(
            FunctionCategory.INVERSE_TRIGONOMETRIC,
            SubOperation.FUNC_1,
            "sin⁻¹", sine_inv, 2
        )
        assert "Domain Error" in result


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_calculation_workflow(self, temp_sci_history_file) -> None:
        """
        Test complete calculation with history.
        
        Action: Calculate, check result, verify history
        Expected: Correct result and history entry
        """
        result = validate_and_eval(
            FunctionCategory.TRIGONOMETRIC,
            SubOperation.FUNC_1,
            "sin", sine, 30
        )
        assert "0.5" in result
        
        # Check history was recorded
        content = temp_sci_history_file.read_text()
        assert "sin(30)" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
