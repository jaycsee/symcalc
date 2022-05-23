from __future__ import annotations

import sympy

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class ReminderFunctionClass(CalculatorPlugin):
    """Calculator plugin to remind that some symbols may be callable FunctionClass, which is not obvious in the pretty print

    .. code-block::

        Calculator >>> sin
        sin is a function
        Calculator >>> cos
        cos
        cos is a function
        Calculator >>> arg
        arg
        arg is a function

    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 10)

    def hook(self, calc: Calculator) -> None:
        calc.context.output_functionclass = self.output_functionclass

    def command_success(self, command: CalculatorCommand) -> None:
        command.calc.interpret("try:\n\toutput_functionclass(_)\nexcept NameError: pass\n")

    def output_functionclass(self, out) -> None:
        """Checks if the output was a function class"""
        if isinstance(out, sympy.FunctionClass):
            print(f"{out} is a function")
