from __future__ import annotations
from typing import Any
import re as regex

from sympy import *
from .calculator import Calculator, CalculatorCommand, CalculatorContext
from .plugin import CalculatorPlugin

class AutoExact(CalculatorPlugin):
    """Calculator plugin to convert numbers to their SymPy exact form"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 40)
        self.settings_name = "auto_exact"
        self.settings_toggle = "ax"

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name

    def handle_command(self, command: CalculatorCommand) -> None:
        """Use a regex to apply the substitution"""
        if not command.calc.settings[self.settings_name]:
            return
        command.command = regex.sub(r"(?<![a-zA-Z_])([\d][\d_]*(\.[\d_]+)?)", r"sympify('\1', rational=True)", command.command)


class AutoSymbol(CalculatorPlugin):
    """Calculator plugin to automatically assume that undefined variables are symbols"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 100)
        self.settings_name = "auto_symbol"
        self.settings_toggle = "as"
        self.fails = set()  # type: set[str]

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings[self.settings_name + "_char"] = False
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.settings_toggle[calc.command_prefix + self.settings_toggle + "c"] = self.settings_name + "_char"

    def handle_command(self, command: CalculatorCommand) -> None:
        self.fails = set()

    def handle_runtime_error(self, command: CalculatorCommand, data: str) -> None:
        """Catch any NameErrors, and then direct the calculator to resend the command"""
        if command.calc.settings[self.settings_name] and data.split("\n")[-2].startswith("NameError: ") and data.split("\n")[-2].split("'")[1] != "_":
            data = data.split("\n")[-2].split("'")[1]
            if data not in self.fails:
                self.fails.add(data)
                if command.calc.settings[self.settings_name + "_char"]:
                    data = regex.sub(r",(\d)", r"\1", ",".join(list(data)))
                command.calc.context.mksym(data)
                command.resend_command = True
                command.print_error = False
                return
