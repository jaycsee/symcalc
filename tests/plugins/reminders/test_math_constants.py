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
