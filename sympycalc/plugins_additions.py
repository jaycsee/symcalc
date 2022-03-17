from __future__ import annotations
from typing import Any
from sympy import *

import webbrowser
from .calc import Calculator, CalculatorCommand, CalculatorContext
from .plugin import CalculatorPlugin


class AddCisFunction(CalculatorPlugin):
    """Calculator plugin to add cis(theta)=cos(theta)+I*sin(theta)"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.cis = self.cis

    def cis(self, *args, **kwargs):
        """Implements the mathematical cis function"""
        return cos(*args, **kwargs) + I * sin(*args, **kwargs)


class AddExternalLinks(CalculatorPlugin):
    """Calculator plugin to add external links as desmos() and symbolab()"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.desmos = self.desmos
        calc.context.symbolab = self.symbolab

    def desmos(self) -> None:
        """Opens the Desmos graphing calculator in the browser"""
        webbrowser.open_new_tab("https://desmos.com/calculator")

    def symbolab(self) -> None:
        """Opens the Desmos graphing calculator in the browser"""
        webbrowser.open_new_tab("https://www.symbolab.com/")


class AddNewtonsMethod(CalculatorPlugin):
    """Calculator plugin to add the single variable Newton's method to the calculator context"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.newton = self.newton

    def newton(self, f, x0, x=None, i: int = 1):
        """Implements single variable Newton's method with the given expression f, the independent variable x (defaults to x in the context scope) and a point x0. Runs i times"""
        if x is None:
            x = self.x
        df = diff(f, x)
        for _ in range(i):
            x0 = x0 - (f.subs(x, x0)) / (df.subs(x, x0))
        return x0


class AddnIntegrate(CalculatorPlugin):
    """Calculator plugin to add numerical integration to the calculator context"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.nintegrate = self.nintegrate

    def nintegrate(self, *args, **kwargs):
        """Returns the numerical value of integrate()"""
        return Integral(*args, **kwargs).evalf()


class AddOriginVectors(CalculatorPlugin):
    """Calculator plugin to add the origin vectors to the calculator context"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Sets the origin vectors"""
        # Make origin vectors
        args = [0]
        for i in range(2, 100):
            args.append(0)
            calc.context.__dict__["o" + str(i)] = Matrix(args)
