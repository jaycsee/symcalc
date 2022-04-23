from __future__ import annotations

import sympy
from sympy import *

from ..calc import Calculator
from ..command import CalculatorCommand
from ..plugin import CalculatorPlugin


class ReminderMathConstants(CalculatorPlugin):
    """Calculator plugin to remind that ``E`` is capitalized and ``pi`` is not"""

    def __init__(self):
        super().__init__(self.__class__.__name__, 10)
        self.eenabled = True
        self.pienabled = True

    def handle_command(self, command: CalculatorCommand) -> None:
        # Check all the symbols for the targeted math constants
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
    """Calculator plugin to remind that symbols are not multiplied together automatically"""

    def __init__(self):
        super().__init__(self.__class__.__name__, 10)
        self.enabled = True
        self.symbols = set()

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "r2", "reminder_two_letter_symbol", True)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Check all the symbols for a undefined symbols which are two letters
        self.symbols.clear()
        for s in command.command_symtable.get_symbols():
            if len(m := s.get_name()) == 2 and m.lower() != "pi" and m.isalpha() and not command.calc.chksym(m):
                self.symbols.add(m)

    @CalculatorPlugin.if_enabled
    def command_success(self, command: CalculatorCommand) -> None:
        # Of the symbols found, check if they are now defined
        for s in self.symbols:
            if command.calc.chksym(s) and isinstance(x := command.calc.getsym(s), Symbol) and str(x) == s:
                command.calc.settings["reminder_two_letter_symbol"] = False
                print(f"`{s}` was treated as a symbol. If you meant `{s[0]}*{s[1]}`, send `del {s}`, `{s[0]}` and then resend that command.")


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
