from __future__ import annotations

import sympy
import sympy.functions.combinatorial.factorials
from symcalc.calc import Calculator
from symcalc.plugin import CalculatorPlugin


class AddAliases(CalculatorPlugin):
    """Calculator plugin to add common aliases"""

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        setattr(calc.context, "mksym", calc.mksym)

        setattr(calc.context, "nCr", lambda n, k: sympy.functions.combinatorial.factorials.binomial(n, k))
        setattr(calc.context, "ncr", lambda n, k: sympy.functions.combinatorial.factorials.binomial(n, k))
        setattr(calc.context, "nPr", lambda n, k: sympy.functions.combinatorial.factorials.binomial(n, k) * sympy.functions.combinatorial.factorials.factorial(k))  # type: ignore
        setattr(calc.context, "npr", lambda n, k: sympy.functions.combinatorial.factorials.binomial(n, k) * sympy.functions.combinatorial.factorials.factorial(k))  # type: ignore

        setattr(calc.context, "plot_3d", sympy.plotting.plot3d)
        setattr(calc.context, "plot_3d_parametric_line", sympy.plotting.plot3d_parametric_line)
        setattr(calc.context, "plot_3d_parametric_surface", sympy.plotting.plot3d_parametric_surface)
        setattr(calc.context, "graph", sympy.plotting.plot)
        setattr(calc.context, "graph_implicit", sympy.plotting.plot_implicit)
        setattr(calc.context, "graph_parametric", sympy.plotting.plot_parametric)

        setattr(calc.context, "graph3d", sympy.plotting.plot3d)
        setattr(calc.context, "graph_3d", sympy.plotting.plot3d)
        setattr(calc.context, "graph3d_parametric_line", sympy.plotting.plot3d_parametric_line)
        setattr(calc.context, "graph_3d_parametric_line", sympy.plotting.plot3d_parametric_line)
        setattr(calc.context, "graph3d_parametric_surface", sympy.plotting.plot3d_parametric_surface)
        setattr(calc.context, "graph_3d_parametric_surface", sympy.plotting.plot3d_parametric_surface)
        setattr(calc.context, "differentiate", sympy.diff)
        setattr(calc.context, "derivative", sympy.diff)

        setattr(calc.context, "arcsin", sympy.asin)
        setattr(calc.context, "arccos", sympy.acos)
        setattr(calc.context, "arctan", sympy.atan)
        setattr(calc.context, "arcsec", sympy.asec)
        setattr(calc.context, "arccsc", sympy.acsc)
        setattr(calc.context, "arccot", sympy.acot)
        setattr(calc.context, "arcsinh", sympy.asinh)
        setattr(calc.context, "arccosh", sympy.acosh)
        setattr(calc.context, "arctanh", sympy.atanh)
        setattr(calc.context, "arcsech", sympy.asech)
        setattr(calc.context, "arccsch", sympy.acsch)
        setattr(calc.context, "arccoth", sympy.acoth)

        setattr(calc.context, "sindeg", lambda x, *args, **kwargs: sympy.sin(x * sympy.pi / 180, *args, **kwargs))
        setattr(calc.context, "cosdeg", lambda x, *args, **kwargs: sympy.cos(x * sympy.pi / 180, *args, **kwargs))
        setattr(calc.context, "tandeg", lambda x, *args, **kwargs: sympy.tan(x * sympy.pi / 180, *args, **kwargs))
        setattr(calc.context, "secdeg", lambda x, *args, **kwargs: sympy.sec(x * sympy.pi / 180, *args, **kwargs))
        setattr(calc.context, "cscdeg", lambda x, *args, **kwargs: sympy.csc(x * sympy.pi / 180, *args, **kwargs))
        setattr(calc.context, "cotdeg", lambda x, *args, **kwargs: sympy.cot(x * sympy.pi / 180, *args, **kwargs))
        setattr(calc.context, "asindeg", lambda *args, **kwargs: sympy.asin(*args, **kwargs) / sympy.pi * 180)
        setattr(calc.context, "acosdeg", lambda *args, **kwargs: sympy.acos(*args, **kwargs) / sympy.pi * 180)
        setattr(calc.context, "atandeg", lambda *args, **kwargs: sympy.atan(*args, **kwargs) / sympy.pi * 180)
        setattr(calc.context, "asecdeg", lambda *args, **kwargs: sympy.asec(*args, **kwargs) / sympy.pi * 180)
        setattr(calc.context, "acscdeg", lambda *args, **kwargs: sympy.acsc(*args, **kwargs) / sympy.pi * 180)
        setattr(calc.context, "acotdeg", lambda *args, **kwargs: sympy.acot(*args, **kwargs) / sympy.pi * 180)
        setattr(calc.context, "arcsindeg", getattr(calc.context, "asindeg"))
        setattr(calc.context, "arccosdeg", getattr(calc.context, "acosdeg"))
        setattr(calc.context, "arctandeg", getattr(calc.context, "atandeg"))
        setattr(calc.context, "arcsecdeg", getattr(calc.context, "asecdeg"))
        setattr(calc.context, "arccscdeg", getattr(calc.context, "acscdeg"))
        setattr(calc.context, "arccotdeg", getattr(calc.context, "acotdeg"))
