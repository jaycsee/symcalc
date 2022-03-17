from __future__ import annotations

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
        self.symbols = set()

    def handle_command(self, command: CalculatorCommand) -> None:
        """Check all the symbols for a undefined symbols which are two letters"""
        if not self.enabled:
            return
        self.symbols.clear()
        for s in command.command_symtable.get_symbols():
            if len(m := s.get_name()) == 2 and m.lower() != "pi" and m.isalpha() and not command.calc.chksym(m):
                self.symbols.add(m)

    def command_success(self, command: CalculatorCommand) -> None:
        for s in self.symbols:
            if command.calc.chksym(s):
                print(f"`{s}` was treated as a symbol. If you meant `{s[0]}*{s[1]}`, send `del {s}`, `{s[0]}` and then resend that command.")
