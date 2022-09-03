# from __future__ import annotations

# from ...command import CalculatorCommand
# from ...plugin import CalculatorPlugin


# class ReminderMathConstants(CalculatorPlugin):
#     """Calculator plugin to remind that ``E`` is capitalized and ``pi`` is not"""

#     def __init__(self):
#         super().__init__(self.__class__.__name__, 10)
#         self.eenabled = True
#         self.pienabled = True

#     def handle_command(self, command: CalculatorCommand) -> None:
#         # Check all the symbols for the targeted math constants
#         if not self.eenabled and not self.pienabled:
#             return
#         for s in command.command_symtable.get_symbols():
#             if (d := s.get_name()) == "e" and self.eenabled:
#                 print("`e` is a symbol. Did you mean `E`, Euler's number?")
#                 self.eenabled = False
#             elif d == "Pi" and self.pienabled:
#                 print("`Pi` is a symbol. Did you mean `pi`, 3.14?")
#                 self.pienabled = False


from symcalc.plugins.reminders.math_constants import ReminderMathConstants
from tests import TestCalculator


def test_plugin_math_constants_reminder_instantiate():
    ReminderMathConstants()


def test_plugin_math_constants_reminder_hook():
    calc = TestCalculator()
    plugin = ReminderMathConstants()
    calc.register_plugin_and_enable(plugin)
    assert plugin in calc.plugins


def test_plugin_math_constants_reminder_validate(capfd):
    calc = TestCalculator()
    calc.register_plugin_and_enable(ReminderMathConstants())
    calc.command(f"Pi = Symbol('Pi')")
    assert "symbol" in capfd.readouterr().out
    calc.command(f"del Pi")
    calc.command(f"Pi = Symbol('Pi')")
    assert "symbol" not in capfd.readouterr().out
    calc.command(f"e = Symbol('e')")
    assert "symbol" in capfd.readouterr().out
    calc.command(f"del e")
    calc.command(f"e = Symbol('e')")
    assert "symbol" not in capfd.readouterr().out
