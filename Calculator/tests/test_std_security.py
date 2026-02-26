"""
Security tests for standard calculator.
"""

from calculator.standard import evaluate_expression


class TestEvalSecurityFixes:
    """Test that eval() replacement prevents code injection."""

    def test_simple_arithmetic_still_works(self) -> None:
        """Verify basic calculations still work."""
        assert evaluate_expression("2 + 2") == "4"
        assert evaluate_expression("10 * 5") == "50"
        assert evaluate_expression("100 / 4") == "25"

    def test_code_injection_prevented_import(self) -> None:
        """Test that __import__ is blocked."""
        result = evaluate_expression("__import__('os').system('ls')")
        assert result == "0"

    def test_code_injection_prevented_exec(self) -> None:
        """Test that exec is blocked."""
        result = evaluate_expression("exec('print(1)')")
        assert result == "0"

    def test_code_injection_prevented_eval(self) -> None:
        """Test that nested eval is blocked."""
        result = evaluate_expression("eval('2+2')")
        assert result == "0"

    def test_variable_access_prevented(self) -> None:
        """Test that variable access is blocked."""
        result = evaluate_expression("__builtins__")
        assert result == "0"

    def test_function_call_prevented(self) -> None:
        """Test that function calls are blocked."""
        result = evaluate_expression("print('hello')")
        assert result == "0"

    def test_complex_expression_works(self) -> None:
        """Test that complex arithmetic still works."""
        result = evaluate_expression("(2 + 3) * 4 - 6 / 2")
        assert result == "17"

    def test_parentheses_work(self) -> None:
        """Test that parentheses are handled correctly."""
        result = evaluate_expression("((10 + 5) * 2) / 3")
        assert result == "10"

    def test_extremely_long_expression_rejected(self) -> None:
        """Test that expressions over 1000 chars are rejected."""
        long_expr = "1" + "+1" * 10000
        result = evaluate_expression(long_expr)
        assert result == "0"

    def test_max_length_expression_accepted(self) -> None:
        """Test that expressions at 1000 chars work."""
        expr = "1" + "+1" * 499
        result = evaluate_expression(expr)
        assert result == "500"
