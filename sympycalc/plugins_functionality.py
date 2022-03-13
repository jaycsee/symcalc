from __future__ import annotations
from typing import Any
import re as regex
import symtable

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

    def parse_command(self, command: CalculatorCommand) -> None:
        """Use a regex to apply the substitution"""
        if not command.calc.settings[self.settings_name]:
            return
        command.command = regex.sub(r"(?<![a-zA-Z_])([\d][\d_]*(\.[\d_]+)?)", r"sympify('\1', rational=True)", command.command)


class AutoSymbol(CalculatorPlugin):
    """Calculator plugin to automatically assume that undefined variables are symbols"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 21)
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
        if not command.calc.settings[self.settings_name]:
            return
        for s in command.command_symtable.get_symbols():
            if not command.calc.chksym(s.get_name()) and not s.get_name().startswith("_"):
                if command.calc.settings[self.settings_name + "_char"]:
                    command.calc.mksym(",".join(list(s.get_name())))
                else:
                    print(f"New symbol: {s.get_name()}")
                    command.calc.mksym(s.get_name())
