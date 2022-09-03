# type: ignore
from __future__ import annotations

import sympy

from symcalc.calc import Calculator
from symcalc.plugin import CalculatorPlugin


class AddAliases(CalculatorPlugin):
    """Calculator plugin to add common aliases"""

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.plot_3d = sympy.plotting.plot3d
        calc.context.plot_3d_parametric_line = sympy.plotting.plot3d_parametric_line
        calc.context.plot_3d_parametric_surface = sympy.plotting.plot3d_parametric_surface
        calc.context.graph = sympy.plotting.plot
        calc.context.graph_implicit = sympy.plotting.plot_implicit
        calc.context.graph_parametric = sympy.plotting.plot_parametric
        calc.context.graph3d = calc.context.graph_3d = sympy.plotting.plot3d
        calc.context.graph3d_parametric_line = calc.context.graph_3d_parametric_line = sympy.plotting.plot3d_parametric_line
        calc.context.graph3d_parametric_surface = calc.context.graph_3d_parametric_surface = sympy.plotting.plot3d_parametric_surface
        calc.context.differentiate = calc.context.derivative = sympy.diff
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

        calc.context.sindeg = lambda x, *args, **kwargs: calc.context.sin(x * sympy.pi / 180, *args, **kwargs)
        calc.context.cosdeg = lambda x, *args, **kwargs: calc.context.cos(x * sympy.pi / 180, *args, **kwargs)
        calc.context.tandeg = lambda x, *args, **kwargs: calc.context.tan(x * sympy.pi / 180, *args, **kwargs)
        calc.context.secdeg = lambda x, *args, **kwargs: calc.context.sec(x * sympy.pi / 180, *args, **kwargs)
        calc.context.cscdeg = lambda x, *args, **kwargs: calc.context.csc(x * sympy.pi / 180, *args, **kwargs)
        calc.context.cotdeg = lambda x, *args, **kwargs: calc.context.cot(x * sympy.pi / 180, *args, **kwargs)
        calc.context.asindeg = lambda *args, **kwargs: calc.context.asin(*args, **kwargs) / sympy.pi * 180
        calc.context.acosdeg = lambda *args, **kwargs: calc.context.acos(*args, **kwargs) / sympy.pi * 180
        calc.context.atandeg = lambda *args, **kwargs: calc.context.atan(*args, **kwargs) / sympy.pi * 180
        calc.context.asecdeg = lambda *args, **kwargs: calc.context.asec(*args, **kwargs) / sympy.pi * 180
        calc.context.acscdeg = lambda *args, **kwargs: calc.context.acsc(*args, **kwargs) / sympy.pi * 180
        calc.context.acotdeg = lambda *args, **kwargs: calc.context.acot(*args, **kwargs) / sympy.pi * 180
        calc.context.arcsindeg = calc.context.asindeg
        calc.context.arccosdeg = calc.context.acosdeg
        calc.context.arctandeg = calc.context.atandeg
        calc.context.arcsecdeg = calc.context.asecdeg
        calc.context.arccscdeg = calc.context.acscdeg
        calc.context.arccotdeg = calc.context.acotdeg
