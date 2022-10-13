from __future__ import annotations

import sympy

from ...calc import Calculator
from ...plugin import CalculatorPlugin


class AddNewtonsMethod(CalculatorPlugin):
    """Calculator plugin to add the single variable Newton's method

    .. code-block::

        Calculator >>> newton(x*(x**2-1), 2, x, 2)
        8192
        ────
        7117
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)
        self.x = sympy.Symbol("x")

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        setattr(calc.context, "newton", self.newton)

    def newton(self, f, x0, x=None, i: int = 1):
        """Implements single variable Newton's method. Available in the Calculator context.

        Parameters
        ----------
        f : :class:`sympy.core.Expr`
            The expression to perform Newton's method on
        x0 : :class:`int`
            The initial guess for the root
        x : :class:`sympy.core.symbol.Symbol`
            The independent variable x, defaults to x
        i : :class:`int`
            The amount of times to iterate
        """
        if x is None:
            x = self.x
        df = sympy.diff(f, x)
        for _ in range(i):
            x0 = x0 - (f.subs(x, x0)) / (df.subs(x, x0))
        return x0
