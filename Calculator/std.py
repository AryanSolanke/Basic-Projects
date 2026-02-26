"""
Compatibility shim for calculator.standard.

This module exists to preserve older import paths. New code should prefer:
    from calculator.standard import <name>

Notes:
    - Re-exports all public names from calculator.standard.
    - Kept intentionally minimal to avoid divergence.
"""

from calculator.standard import *  # noqa: F401,F403
