"""
Compatibility shim for calculator.scientific.

This module exists to preserve older import paths. New code should prefer:
    from calculator.scientific import <name>

Notes:
    - Re-exports all public names from calculator.scientific.
    - Kept intentionally minimal to avoid divergence.
"""

from calculator.scientific import *  # noqa: F401,F403
