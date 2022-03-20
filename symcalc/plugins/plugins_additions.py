from __future__ import annotations

import webbrowser
from typing import Any

from sympy import *

from ..calc import Calculator
from ..plugin import CalculatorPlugin


class AddCisFunction(CalculatorPlugin):
    """Calculator plugin to add the ``cis`` function. ``cis(x)`` is equivalent to ``cos(x)+I*sin(x)``

    .. code-block::

        Calculator >>> 2*cis(pi/3)
        1 + √3⋅ⅈ

    """

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.cis = self.cis

    def cis(self, *args, **kwargs):
        """Implements the mathematical ``cis`` function. Available in the calculator context. All parameters are passed to :meth:`sympy.sin` and :meth:`sympy.cos` functions"""
        return cos(*args, **kwargs) + I * sin(*args, **kwargs)


class AddExternalLinks(CalculatorPlugin):
    """Calculator plugin to add external links as ``desmos()`` and ``symbolab()``"""

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.desmos = self.desmos
        calc.context.symbolab = self.symbolab

    def desmos(self) -> None:
        """Opens the Desmos graphing calculator in the browser. Available in the calculator context"""
        webbrowser.open_new_tab("https://desmos.com/calculator")

    def symbolab(self) -> None:
        """Opens the Desmos graphing calculator in the browser. Available in the calculator context"""
        webbrowser.open_new_tab("https://www.symbolab.com/")


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

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.newton = self.newton

    def newton(self, f, x0, x=None, i: int = 1):
        """Implements single variable Newton's methodAvailable in the Calculator context.

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
        df = diff(f, x)
        for _ in range(i):
            x0 = x0 - (f.subs(x, x0)) / (df.subs(x, x0))
        return x0


class AddnIntegrate(CalculatorPlugin):
    """Calculator plugin to add numerical integration. ``nintegrate(x)`` is equivalent to ``Integral(x).evalf()``"""

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.nintegrate = self.nintegrate

    def nintegrate(self, *args, **kwargs):
        """Implements the numerical integration. Available in the Calculator context."""
        return Integral(*args, **kwargs).evalf()


class AddOriginVectors(CalculatorPlugin):
    """Calculator plugin to add the origin vectors to the calculator context. o<n> is the origin vector in R^n

    .. code-block::

        Calculator >>> o3
        ⎡0⎤
        ⎢ ⎥
        ⎢0⎥
        ⎢ ⎥
        ⎣0⎦
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Sets the origin vectors"""
        # Make origin vectors
        args = [0]
        for i in range(2, 100):
            args.append(0)
            calc.context.__dict__["o" + str(i)] = Matrix(args)
