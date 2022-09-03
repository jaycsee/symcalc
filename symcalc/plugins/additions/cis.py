from __future__ import annotations

import sympy

from symcalc.calc import Calculator
from symcalc.plugin import CalculatorPlugin


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
        calc.context.cis = self.cis  # type: ignore

    def cis(self, *args, **kwargs):
        """Implements the mathematical ``cis`` function. Available in the calculator context. All parameters are passed to :meth:`sympy.sin` and :meth:`sympy.cos` functions"""
        return sympy.cos(*args, **kwargs) + sympy.I * sympy.sin(*args, **kwargs)
