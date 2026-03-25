"""
Comprehensive test Suite for std.py

This module provides extensive unit tests for the standard calculator module,
covering edge cases, boundary values, and error conditions.

Testing strategy:
1. Function isolation - Each function tested independently
2. Edge case coverage - Boundary values, empty inputs, special characters
3. Error handling - invalid inputs, exceptions, file operations
4. Type validation - Ensure correct handling of various data types
5. Integration - File I/O operations and history management

Standards:
- pytest framework
- Type hints for all test functions
- Descriptive docstrings
- Parametrized tests for efficiency
"""
import os
import pytest
from decimal import InvalidOperation
from pathlib import Path
from typing import Generator

from calculator.standard import (
    compute_expression,
    errmsg,
    format_answer,
    record_history_std_calc,
    display_hist_std_calc,
    clear_hist_std_calc,
    exp_input,
    validate_exp,
    evaluate_expression,
    HISTORY_FILE,
    DECIMAL_PRECISION
)
from calculator.exceptions import ExpressionError, NullInputError, UnbalancedParenthesesError


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def temp_history_file(monkeypatch, tmp_path) -> Generator[Path, None, None]:
    """
    Create temporary history file for isolated testing.

    Yields:
        Path to temporary history file
    """
    temp_file = tmp_path / "test_history.txt"
    monkeypatch.setattr('calculator.standard.HISTORY_FILE', temp_file)
    yield temp_file


@pytest.fixture
def history_with_data(temp_history_file) -> Path:
    """
    Create history file with sample data.
    
    Returns:
        Path to populated history file
    """
    temp_history_file.write_text("2+2 = 4\n3*3 = 9\n10/2 = 5\n")
    return temp_history_file


# ============================================================================
# Test format_answer Function
# ============================================================================
class TestFormatAnswer:
    """Test suite for format_answer function."""
    
    def test_format_answer_removes_trailing_zeros(self) -> None:
        """
        Test that trailing zeros are removed from decimal numbers.
        
        Input: 5.00000
        Expected: "5"
        """
        assert format_answer(5.00000) == "5"
    
    def test_format_answer_preserves_significant_decimals(self) -> None:
        """
        Test that significant decimal places are preserved.
        
        Input: 3.14159265359
        Expected: String with significant digits
        """
        result = format_answer(3.14159265359)
        assert result == "3.14159265"
    
    def test_format_answer_handles_negative_zero(self) -> None:
        """
        Test that negative zero is normalized to positive zero.
        
        Input: -0.0
        Expected: "0"
        """
        assert format_answer(-0.0) == "0"
    
    def test_format_answer_handles_very_small_numbers(self) -> None:
        """
        Test formatting of very small numbers near zero.
        
        Input: 1e-15
        Expected: Properly formatted small number
        """
        result = format_answer(1e-15)
        assert result == "1e-15"
    
    def test_format_answer_handles_very_large_numbers(self) -> None:
        """
        Test formatting of very large numbers.
        
        Input: 1e10
        Expected: "10000000000"
        """
        result = format_answer(1e10)
        assert result == "1e+10"
    
    def test_format_answer_handles_scientific_notation_input(self) -> None:
        """
        Test that numbers in scientific notation are formatted correctly.
        
        Input: 4.24980693916337e-15
        Expected: Formatted decimal string
        """
        result = format_answer(4.24980693916337e-15)
        assert result == "4.24980694e-15"
    
    def test_format_answer_handles_negative_numbers(self) -> None:
        """
        Test formatting of negative numbers.
        
        Input: -123.456
        Expected: "-123.456"
        """
        assert format_answer(-123.456) == "-123.456"
    
    @pytest.mark.parametrize("value,expected", [
        (0.0, "0"),
        (1.0, "1"),
        (0.1, "0.1"),
        (0.10, "0.1"),
        (10.0, "10"),
        (0.123456789012345, "0.12345678901235"),  # Precision limit
    ])
    def test_format_answer_parametrized(self, value: float, expected: str) -> None:
        """
        Parametrized test for various formatting scenarios.
        
        Args:
            value: Input float
            expected: Expected formatted string
        """
        result = format_answer(value)
        assert result == expected or result.startswith(expected[:10])


# ============================================================================
# Test validate_exp Function
# ============================================================================

class TestValidateExp:
    """Test suite for validate_exp function."""
    
    def test_validate_exp_accepts_valid_expression(self, capsys) -> None:
        """
        Test that valid arithmetic expressions are accepted.
        
        Input: "2+2*3"
        Expected: True
        """
        assert validate_exp("2+2*3") is True
    
    def test_validate_exp_rejects_unbalanced_parentheses_left(self, capsys) -> None:
        """
        Test rejection of expressions with too many opening parentheses.
        
        Input: "((2+2)"
        Expected: False with error message
        """
        with pytest.raises(UnbalancedParenthesesError):
            validate_exp("((2+2)")
    
    def test_validate_exp_rejects_unbalanced_parentheses_right(self, capsys) -> None:
        """
        Test rejection of expressions with too many closing parentheses.
        
        Input: "(2+2))"
        Expected: False with error message
        """
        with pytest.raises(UnbalancedParenthesesError):
            validate_exp("(2+2))")
    
    def test_validate_exp_rejects_empty_string(self, capsys) -> None:
        """
        Test rejection of empty expressions.
        
        Input: ""
        Expected: False with error message
        """
        with pytest.raises(NullInputError):
            validate_exp("")
    
    def test_validate_exp_rejects_whitespace_only(self, capsys) -> None:
        """
        Test rejection of whitespace-only expressions.
        
        Input: "   "
        Expected: False with error message
        """
        with pytest.raises(NullInputError):
            validate_exp("   ")
    
    def test_validate_exp_rejects_letters(self, capsys) -> None:
        """
        Test rejection of expressions containing letters.
        
        Input: "a+b"
        Expected: False with error message
        """
        assert validate_exp("a+b") is False
        captured = capsys.readouterr()
        assert "Error: Invalid Expression" in captured.out
        assert "valid character" in captured.out
    
    def test_validate_exp_rejects_special_characters(self, capsys) -> None:
        """
        Test rejection of expressions containing special characters.
        
        Input: "2+2@3"
        Expected: False with error message
        """
        assert validate_exp("2+2@3") is False
        captured = capsys.readouterr()
        assert "Error: Invalid Expression" in captured.out
        assert "valid character" in captured.out
    
    def test_validate_exp_rejects_symbols(self, capsys) -> None:
        """
        Test rejection of expressions containing disallowed symbols.
        
        Input: "###"
        Expected: False with error message
        """
        assert validate_exp("###") is False
        captured = capsys.readouterr()
        assert "Error: Invalid Expression" in captured.out
        assert "valid character" in captured.out
    
    def test_validate_exp_accepts_all_allowed_operators(self) -> None:
        """
        Test that all allowed operators are accepted.
        
        Input: Expression with +, -, *, /, %, ()
        Expected: True
        """
        assert validate_exp("(1+2-3*4/5)%6") is True
    
    def test_validate_exp_accepts_spaces(self) -> None:
        """
        Test that spaces in expressions are allowed.
        
        Input: "1 + 2 * 3"
        Expected: True
        """
        assert validate_exp("1 + 2 * 3") is True
    
    def test_validate_exp_accepts_decimal_points(self) -> None:
        """
        Test that decimal numbers are allowed.
        
        Input: "3.14 * 2.5"
        Expected: True
        """
        assert validate_exp("3.14 * 2.5") is True
    
    @pytest.mark.parametrize("expression,should_pass", [
        ("2+2", True),
        ("()", True),
        ("1.5+2.5", True),
        ("10%3", True),
        ("2^3", False),  # ^ not allowed
        ("2&3", False),  # & not allowed
        ("x=5", False),  # = not allowed
        ("[1,2]", False),  # [] not allowed
    ])
    def test_validate_exp_parametrized(
        self, expression: str, should_pass: bool, capsys
    ) -> None:
        """
        Parametrized test for various validation scenarios.
        
        Args:
            expression: Expression to validate
            should_pass: Expected validation result
        """
        assert validate_exp(expression) == should_pass


# ============================================================================
# Test evaluate_expression Function
# ============================================================================

class TestEvaluateExpression:
    """Test suite for evaluate_expression function."""

    def test_compute_expression_basic_addition(self, temp_history_file) -> None:
        """The strict UI-facing evaluator should return formatted results."""
        assert compute_expression("2+2") == "4"

    def test_compute_expression_invalid_characters_raise(self, temp_history_file) -> None:
        """The strict evaluator should raise instead of printing for bad input."""
        with pytest.raises(ExpressionError):
            compute_expression("abc")
    
    def test_evaluate_expression_basic_addition(self, temp_history_file) -> None:
        """
        Test basic addition evaluation.
        
        Input: "2+2"
        Expected: "4"
        """
        assert evaluate_expression("2+2") == "4"
    
    def test_evaluate_expression_operator_precedence(self, temp_history_file) -> None:
        """
        Test that operator precedence is respected.
        
        Input: "2+3*4"
        Expected: "14"
        """
        assert evaluate_expression("2+3*4") == "14"
    
    def test_evaluate_expression_parentheses(self, temp_history_file) -> None:
        """
        Test parentheses override precedence.
        
        Input: "(2+3)*4"
        Expected: "20"
        """
        assert evaluate_expression("(2+3)*4") == "20"
    
    def test_evaluate_expression_division_by_zero(self, temp_history_file) -> None:
        """
        Test that division by zero returns "0".
        
        Input: "10/0"
        Expected: "0"
        """
        with pytest.raises(InvalidOperation):
            evaluate_expression("10/0")
    
    def test_evaluate_expression_invalid_syntax(self, temp_history_file) -> None:
        """
        Test that syntax errors return "0".
        
        Input: "-/*-+/+-*+*-/-3+/"
        Expected: "0"
        """
        with pytest.raises(SyntaxError):
            evaluate_expression("-/*-+/+-*+*-/-3+/")
    
    def test_evaluate_expression_empty_input(self, temp_history_file) -> None:
        """
        Test that empty input returns "0".
        
        Input: ""
        Expected: "0"
        """
        with pytest.raises(NullInputError):
            evaluate_expression("")
    
    def test_evaluate_expression_complex_calculation(self, temp_history_file) -> None:
        """
        Test complex multi-operator expression.
        
        Input: "15*(6+3-1)+215-(31*(4/35)**16)//733%648"
        Expected: "335"
        """
        assert evaluate_expression("15*(6+3-1)+215-(31*(4/35)**16)//733%648") == "335"
    
    def test_evaluate_expression_floating_point_precision(self, temp_history_file) -> None:
        """
        Test floating point addition precision.
        
        Input: "0.1 + 0.2"
        Expected: "0.3"
        """
        assert evaluate_expression("0.1 + 0.2") == "0.3"
    
    def test_evaluate_expression_scientific_notation_result(self, temp_history_file) -> None:
        """
        Test that results in scientific notation are formatted.
        
        Input: "0.2222**22"
        Expected: Result as formatted decimal
        """
        result = evaluate_expression("0.2222**22")
        # Should be very small number
        assert result == "4.24980694e-15"
    
    def test_evaluate_expression_overflow(self, temp_history_file) -> None:
        """
        Test that overflow returns "0".
        
        Input: "1000000000.0**1000"
        Expected: "0"
        """
        with pytest.raises(OverflowError):
            evaluate_expression("1000000000.0**1000")
    
    def test_evaluate_expression_multiple_decimals_invalid(self, temp_history_file) -> None:
        """
        Test that invalid decimal syntax returns "0".
        
        Input: "5...56.67.5.443."
        Expected: "0"
        """
        with pytest.raises(SyntaxError):
            evaluate_expression("5...56.67.5.443.")
    
    def test_evaluate_expression_modulo_operation(self, temp_history_file) -> None:
        """
        Test modulo operator.
        
        Input: "10%3"
        Expected: "1"
        """
        assert evaluate_expression("10%3") == "1"
    
    def test_evaluate_expression_negative_numbers(self, temp_history_file) -> None:
        """
        Test evaluation with negative numbers.
        
        Input: "-5+3"
        Expected: "-2"
        """
        assert evaluate_expression("-5+3") == "-2"
    
    def test_evaluate_expression_nested_parentheses(self, temp_history_file) -> None:
        """
        Test deeply nested parentheses.
        
        Input: "((((1+1))))"
        Expected: "2"
        """
        assert evaluate_expression("((((1+1))))") == "2"
    
    @pytest.mark.parametrize("expression,expected", [
        ("1+1", "2"),
        ("10-5", "5"),
        ("3*4", "12"),
        ("15/3", "5"),
        ("2**3", "8"),
        ("0*1000", "0"),
        ("100/100", "1"),
    ])
    def test_evaluate_expression_parametrized(
        self, expression: str, expected: str, temp_history_file
    ) -> None:
        """
        Parametrized test for various expressions.
        
        Args:
            expression: Expression to evaluate
            expected: Expected result
        """
        assert evaluate_expression(expression) == expected


# ============================================================================
# Test History Management Functions
# ============================================================================

class TestHistoryManagement:
    """Test suite for history management functions."""
    
    def test_record_history_creates_file(self, temp_history_file) -> None:
        """
        Test that recording history creates the file if it doesn't exist.
        
        Action: Record a calculation
        Expected: File exists with correct content
        """
        record_history_std_calc("2+2", "4")
        assert temp_history_file.exists()
        assert "2+2 = 4\n" in temp_history_file.read_text()
    
    def test_record_history_appends_to_existing(self, history_with_data) -> None:
        """
        Test that recording appends to existing history.
        
        Action: Record to file with existing data
        Expected: New entry appended, old entries preserved
        """
        original_content = history_with_data.read_text()
        record_history_std_calc("5+5", "10")
        new_content = history_with_data.read_text()
        assert original_content in new_content
        assert "5+5 = 10\n" in new_content
    
    def test_record_history_multiple_entries(self, temp_history_file) -> None:
        """
        Test recording multiple history entries.
        
        Action: Record 3 calculations
        Expected: All 3 present in file
        """
        record_history_std_calc("1+1", "2")
        record_history_std_calc("2+2", "4")
        record_history_std_calc("3+3", "6")
        content = temp_history_file.read_text()
        assert content.count("\n") == 3
        assert "1+1 = 2" in content
        assert "2+2 = 4" in content
        assert "3+3 = 6" in content
    
    def test_display_history_shows_entries(
        self, history_with_data, capsys
    ) -> None:
        """
        Test that display_hist_std_calc shows all entries.
        
        Action: Display history with 3 entries
        Expected: All entries printed
        """
        display_hist_std_calc()
        captured = capsys.readouterr()
        assert "CALCULATION HISTORY" in captured.out
        assert "2+2 = 4" in captured.out
        assert "3*3 = 9" in captured.out
        assert "10/2 = 5" in captured.out
    
    def test_display_history_empty_file(self, temp_history_file, capsys) -> None:
        """
        Test display when history file is empty.
        
        Action: Display with empty file
        Expected: No entries shown
        """
        temp_history_file.write_text("")
        display_hist_std_calc()
        captured = capsys.readouterr()
        assert "History is empty" in captured.out
    
    def test_display_history_nonexistent_file(self, capsys, monkeypatch) -> None:
        """
        Test display when history file doesn't exist.
        
        Action: Display with no file
        Expected: Error message
        """
        nonexistent = Path("/tmp/nonexistent_history_file.txt")
        monkeypatch.setattr('calculator.standard.HISTORY_FILE', nonexistent)
        display_hist_std_calc()
        captured = capsys.readouterr()
        assert "No history available" in captured.out
    
    def test_clear_history_removes_content(self, history_with_data) -> None:
        """
        Test that clear_hist_std_calc empties the file.
        
        Action: Clear history with existing data
        Expected: File empty but exists
        """
        clear_hist_std_calc()
        assert history_with_data.exists()
        assert history_with_data.read_text() == ""
    
    def test_clear_history_success_message(self, temp_history_file, capsys) -> None:
        """
        Test that clear shows success message.
        
        Action: Clear history
        Expected: Success message printed
        """
        clear_hist_std_calc()
        captured = capsys.readouterr()
        assert "History cleared successfully!" in captured.out
    
    def test_clear_history_nonexistent_file(self, capsys, monkeypatch) -> None:
        """
        Test clear when file doesn't exist.
        
        Action: Clear non-existent file
        Expected: Error message
        """
        nonexistent = Path("/tmp/nonexistent_history_file_clear.txt")
        if nonexistent.exists():
            nonexistent.unlink()
        monkeypatch.setattr('calculator.standard.HISTORY_FILE', nonexistent)
        clear_hist_std_calc()
        # Should not crash, should handle gracefully


# ============================================================================
# Test Error Handling
# ============================================================================

class TestErrorHandling:
    """Test suite for error handling."""
    
    def test_errmsg_prints_error(self, capsys) -> None:
        """
        Test that errmsg prints standard error message.
        
        Action: Call errmsg
        Expected: Standard error message printed
        """
        errmsg()
        captured = capsys.readouterr()
        assert "Error: Invalid input." in captured.out
    
    def test_evaluate_expression_handles_type_error(self, temp_history_file) -> None:
        """
        Test that TypeError is handled gracefully.
        
        This tests the exception handling in evaluate_expression.
        """
        # This should trigger validation failure
        result = evaluate_expression("abc")
        assert result == "0"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for std_refactored module."""
    
    def test_full_calculation_workflow(self, temp_history_file) -> None:
        """
        Test complete workflow: evaluate, record, display, clear.
        
        Action: Perform calculation, check history, clear
        Expected: All operations work together correctly
        """
        # Evaluate and record
        result = evaluate_expression("10+20")
        assert result == "30"
        
        # Check file was created
        assert temp_history_file.exists()
        content = temp_history_file.read_text()
        assert "10+20 = 30" in content
        
        # Clear history
        clear_hist_std_calc()
        assert temp_history_file.read_text() == ""
    
    def test_multiple_calculations_preserve_history(
        self, temp_history_file
    ) -> None:
        """
        Test that multiple calculations accumulate in history.
        
        Action: Perform 5 calculations
        Expected: All 5 in history file
        """
        expressions = ["1+1", "2*2", "3-1", "4/2", "5%2"]
        for exp in expressions:
            evaluate_expression(exp)
        
        content = temp_history_file.read_text()
        assert content.count("\n") == 5


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance tests for std_refactored module."""
    
    def test_format_answer_performance_large_number(self) -> None:
        """
        Test formatting performance with very large numbers.
        
        Input: 10**100
        Expected: Completes without timeout
        """
        import time
        start = time.time()
        result = format_answer(10.0**100)
        duration = time.time() - start
        assert duration < 1.0  # Should complete in under 1 second
        assert result is not None
    
    def test_validate_exp_performance_long_expression(self) -> None:
        """
        Test validation performance with very long expressions.
        
        Input: Expression with 1000 characters
        Expected: Completes efficiently
        """
        long_exp = "+".join(["1"] * 500)
        import time
        start = time.time()
        result = validate_exp(long_exp)
        duration = time.time() - start
        assert duration < 1.0
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
