from symcalc.plugins.reminders.two_letter_symbol import ReminderTwoLetterSymbol
from tests import TestCalculator, random_str


def test_plugin_two_letter_symbol_reminder_instantiate():
    ReminderTwoLetterSymbol()


def test_plugin_two_letter_symbol_reminder_hook():
    calc = TestCalculator()
    plugin = ReminderTwoLetterSymbol()
    calc.register_plugin_and_enable(plugin)
    assert plugin in calc.plugins


def test_plugin_two_letter_symbol_reminder_validate(capfd):
    for i in range(10):
        s = random_str()[0:2]
        calc = TestCalculator()
        calc.register_plugin_and_enable(ReminderTwoLetterSymbol())
        calc.command(f"{s} = Symbol('{s}')")
        assert "treated as" in capfd.readouterr().out
        calc.command(f"del {s}")
        calc.command(f"{s} = Symbol('{s}')")
        assert "treated as" not in capfd.readouterr().out


def test_plugin_two_letter_symbol_reminder_enable_switch(capfd):
    calc = TestCalculator()
    plugin = ReminderTwoLetterSymbol()
    calc.register_plugin_and_enable(plugin)
    s = random_str()[0:2]
    calc.command(f"{s} = Symbol('{s}')")
    assert "treated as" in capfd.readouterr().out
    calc.command(f"del {s}")
    calc.command(f"{s} = Symbol('{s}')")
    assert "treated as" not in capfd.readouterr().out
