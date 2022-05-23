from __future__ import annotations

import sympy

from ...calc import Calculator
from ...plugin import CalculatorPlugin


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
            calc.context.__dict__["o" + str(i)] = sympy.Matrix(args)
