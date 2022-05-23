from __future__ import annotations

from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


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
