from __future__ import annotations

import sympy

from ...calc import Calculator
from ...plugin import CalculatorPlugin


class AddInverseTrig(CalculatorPlugin):
    """Calculator plugin to add aliases for inverse trigonometric functions"""

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.arcsin = sympy.asin
        calc.context.arccos = sympy.acos
        calc.context.arctan = sympy.atan
        calc.context.arcsec = sympy.asec
        calc.context.arccsc = sympy.acsc
        calc.context.arccot = sympy.acot
        calc.context.arcsinh = sympy.asinh
        calc.context.arccosh = sympy.acosh
        calc.context.arctanh = sympy.atanh
        calc.context.arcsech = sympy.asech
        calc.context.arccsch = sympy.acsch
        calc.context.arccoth = sympy.acoth
