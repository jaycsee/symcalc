from __future__ import annotations

import sympy

from ...calc import Calculator
from ...plugin import CalculatorPlugin


class AddnIntegrate(CalculatorPlugin):
    """Calculator plugin to add numerical integration. ``nintegrate(x)`` is equivalent to ``Integral(x).evalf()``"""

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        setattr(calc.context, "nintegrate", self.nintegrate)

    def nintegrate(self, *args, **kwargs):
        """Implements the numerical integration. Available in the Calculator context."""
        return sympy.Integral(*args, **kwargs).evalf()  # type: ignore
