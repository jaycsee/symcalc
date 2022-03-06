from __future__ import annotations

from sympy import *
from .calculator import Calculator, CalculatorCommand, CalculatorContext
from .plugin import CalculatorPlugin


class ReminderMathConstants(CalculatorPlugin):
    """Calculator plugin to remind that e is capitalized and pi is not"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 31)
        self.eenabled = True
        self.pienabled = True

    def handle_runtime_error(self, command: CalculatorCommand, data: str) -> None:
        """Catch any NameErrors, and then direct the calculator to resend the command"""
        if not (data.split("\n")[-2].startswith("NameError: ") and (d := data.split("\n")[-2].split("'")[1]) != "_"):
            return
        if self.eenabled and d == "e":
            print("`e` is a symbol. Did you mean `E`, Euler's number?")
            self.eenabled = False
        elif self.pienabled and d == "Pi":
            print("`Pi` is a symbol. Did you mean `pi`, 3.14?")
            self.pienabled = False


class ReminderTwoLetterSymbol(CalculatorPlugin):
    """Calculator plugin to remind that e is capitalized"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 31)
        self.enabled = True

    def handle_runtime_error(self, command: CalculatorCommand, data: str) -> None:
        """Catch any NameErrors, and then direct the calculator to resend the command"""
        if self.enabled and data.split("\n")[-2].startswith("NameError: ") and data.split("\n")[-2].split("'")[1] != "_":
            if len(m := data.split("\n")[-2].split("'")[1]) == 2 and m.lower() != "pi":
                print(f"`{m}` will be treated as a symbol. If you meant `{m[0]}*{m[1]}`, send `{m[0]}` and then resend this command.")
                self.enabled = False
                command.abort = True
