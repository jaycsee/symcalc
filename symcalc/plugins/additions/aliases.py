from __future__ import annotations

import sympy
import sympy.functions.combinatorial.factorials
import sympy.parsing.latex
import sympy.parsing.mathematica
import sympy.parsing.maxima
from symcalc.calc import Calculator
from symcalc.plugin import CalculatorPlugin


class AddAliases(CalculatorPlugin):
    """Calculator plugin to add common aliases"""

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        setattr(calc.context, "mksym", calc.mksym)
        setattr(calc.context, "getsym", calc.getsym)
        setattr(calc.context, "chksym", calc.chksym)

        setattr(calc.context, "parse_latex", sympy.parsing.latex.parse_latex)
        setattr(calc.context, "parse_maxima", sympy.parsing.maxima.parse_maxima)
        setattr(calc.context, "parse_mathematica", sympy.parsing.mathematica.parse_mathematica)

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

        setattr(calc.context, "sindeg", lambda arg: sympy.sin(arg * sympy.pi / 180))
        setattr(calc.context, "cosdeg", lambda arg: sympy.cos(arg * sympy.pi / 180))
        setattr(calc.context, "tandeg", lambda arg: sympy.tan(arg * sympy.pi / 180))
        setattr(calc.context, "secdeg", lambda arg: sympy.sec(arg * sympy.pi / 180))
        setattr(calc.context, "cscdeg", lambda arg: sympy.csc(arg * sympy.pi / 180))
        setattr(calc.context, "cotdeg", lambda arg: sympy.cot(arg * sympy.pi / 180))
        setattr(calc.context, "asindeg", lambda arg: sympy.asin(arg) / sympy.pi * 180)
        setattr(calc.context, "acosdeg", lambda arg: sympy.acos(arg) / sympy.pi * 180)
        setattr(calc.context, "atandeg", lambda arg: sympy.atan(arg) / sympy.pi * 180)
        setattr(calc.context, "asecdeg", lambda arg: sympy.asec(arg) / sympy.pi * 180)
        setattr(calc.context, "acscdeg", lambda arg: sympy.acsc(arg) / sympy.pi * 180)
        setattr(calc.context, "acotdeg", lambda arg: sympy.acot(arg) / sympy.pi * 180)
        setattr(calc.context, "arcsindeg", getattr(calc.context, "asindeg"))
        setattr(calc.context, "arccosdeg", getattr(calc.context, "acosdeg"))
        setattr(calc.context, "arctandeg", getattr(calc.context, "atandeg"))
        setattr(calc.context, "arcsecdeg", getattr(calc.context, "asecdeg"))
        setattr(calc.context, "arccscdeg", getattr(calc.context, "acscdeg"))
        setattr(calc.context, "arccotdeg", getattr(calc.context, "acotdeg"))
