from __future__ import annotations

import re as regex
from sympy import *
from .calculator import Calculator, CalculatorCommand, CalculatorContext
from .plugin import CalculatorPlugin


class ReminderMathConstants(CalculatorPlugin):
    """Calculator plugin to remind that e is capitalized and pi is not"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 10)
        self.eenabled = True
        self.pienabled = True

    def handle_command(self, command: CalculatorCommand) -> None:
        """Check all the symbols for the targeted math constants"""
        if not self.eenabled and not self.pienabled:
            return
        for s in command.command_symtable.get_symbols():
            if (d := s.get_name()) == "e" and self.eenabled:
                print("`e` is a symbol. Did you mean `E`, Euler's number?")
                self.eenabled = False
            elif d == "Pi" and self.pienabled:
                print("`Pi` is a symbol. Did you mean `pi`, 3.14?")
                self.pienabled = False


class ReminderTwoLetterSymbol(CalculatorPlugin):
    """Calculator plugin to remind that e is capitalized"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 10)
        self.enabled = True

    def handle_command(self, command: CalculatorCommand) -> None:
        """Check all the symbols for a undefined symbols which are two letters"""
        if not self.enabled:
            return
        for s in command.command_symtable.get_symbols():
            if len(m := s.get_name()) == 2 and m.lower() != "pi" and m.isalpha():
                print(f"`{m}` will be treated as a symbol. If you meant `{m[0]}*{m[1]}`, send `{m[0]}` and then resend this command.")
                self.enabled = False
                command.abort = True
                break


class ReminderComplexNumber(CalculatorPlugin):
    """Calculator plugin to remind that e is capitalized"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 10)
        self.enabled = True

    def parse_command(self, command: CalculatorCommand) -> None:
        """Check to see if the user has entered a complex constant"""
        if not self.enabled:
            return
        if command.calc.chksym("j"):
            self.enabled = False
            return
        if regex.match(r"(([0-9]*\.)?[0-9]+ *\+ *)?([0-9]*\.)?[0-9]+j", command.command):
            print("You seem to have entered a Python complex number. If you meant to do that, use `I` instead of `j`")
            self.enabled = False
            command.abort = True
