from __future__ import annotations

import sympy

from ...calc import Calculator
from ...plugin import CalculatorPlugin


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
