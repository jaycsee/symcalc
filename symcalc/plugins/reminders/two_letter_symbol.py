from __future__ import annotations

import sympy

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


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
            if command.calc.chksym(s) and isinstance(x := command.calc.getsym(s), sympy.Symbol) and str(x) == s:
                command.calc.settings["reminder_two_letter_symbol"] = False
                print(f"`{s}` was treated as a symbol. If you meant `{s[0]}*{s[1]}`, send `del {s}`, `{s[0]}` and then resend that command.")
