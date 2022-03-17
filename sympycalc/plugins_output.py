from __future__ import annotations

import sympy
import re as regex
from sympy import *
from .calculator import Calculator, CalculatorCommand, CalculatorContext
from .plugin import CalculatorPlugin


class OutputDecimal(CalculatorPlugin):
    """Calculator plugin to automatically display the decimal representation of the result"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 200)
        self.settings_name = "output_decimal"
        self.settings_toggle = "od"
        self.ignore_types = set([sympy.core.numbers.One, sympy.core.numbers.Zero, sympy.core.numbers.Integer, sympy.core.numbers.Float])

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.context.output_decimal = self.output_decimal

    def command_success(self, command: CalculatorCommand) -> None:
        """Send the command to the interpreter to output the decimal represent"""
        if not command.calc.settings[self.settings_name]:
            return
        command.calc.interpret(
            """try:
    del _
except NameError: pass
"""
        )
        command.calc.interpret("output_decimal(_)")

    def output_decimal(self, output) -> None:
        """Prints the decimal of the given output"""
        try:
            if type(output) not in self.ignore_types and not output.free_symbols and (regex.match(r"^-?\d+(\.\d+)?(e-?\d+)?(\*I)?$", str(output.evalf())) or regex.match(r"^-?\d+(\.\d+)(e-?\d+)?\s?\+\s?\d+(\.\d+)?(e-?\d+)?\*I$", str(output.evalf()))):
                print(f"Decimal: ", end="")
                pretty_print(output.evalf())
        except (TypeError, AttributeError, ValueError):
            pass


class OutputStore(CalculatorPlugin):
    """Calculator plugin to automatically display the decimal representation of the result"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 210)
        self.settings_name = "output_store"
        self.settings_toggle = "os"
        self.ignore_types = set([sympy.core.symbol.Symbol, sympy.core.numbers.One, sympy.core.numbers.Zero])

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        self.context = calc.context
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.context.out = [None]
        calc.context.output_store = self.output_store

    def command_success(self, command: CalculatorCommand) -> None:
        """Send the command to the interpreter to store the output"""
        if not command.calc.settings[self.settings_name]:
            return
        command.calc.interpret(
            """try:
    del _
except NameError: pass
"""
        )
        command.calc.interpret("output_store(_)")

    def output_store(self, output) -> None:
        if output is not self.context.out and output not in self.context.out and output.__class__.__module__.startswith("sympy.") and type(output) not in self.ignore_types and str(type(output)) != "<class 'sympy.core.assumptions.ManagedProperties'>":
            self.context.out.append(output)
            print(f"Result stored in out[{len(self.context.out)-1}]")
