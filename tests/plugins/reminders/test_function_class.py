from symcalc.plugins.reminders.function_class import ReminderFunctionClass
from tests import TestCalculator


def test_plugin_function_class_reminder_instantiate():
    ReminderFunctionClass()


def test_plugin_function_class_reminder_hook():
    calc = TestCalculator()
    plugin = ReminderFunctionClass()
    calc.register_plugin_and_enable(plugin)
    assert plugin in calc.plugins


def test_plugin_function_class_reminder_context_updated():
    calc = TestCalculator()
    calc.register_plugin_and_enable(ReminderFunctionClass())
    assert calc.chksym("output_functionclass")
    assert callable(calc.getsym("output_functionclass"))


def test_plugin_function_class_reminder_available():
    calc = TestCalculator()
    calc.register_plugin_and_enable(ReminderFunctionClass())
    assert callable(calc.command("output_functionclass"))


def test_plugin_function_class_reminder_example(capfd):
    calc = TestCalculator()
    calc.register_plugin_and_enable(ReminderFunctionClass())
    calc.command("sin")
    assert "is a function" in capfd.readouterr().out
    calc.command("cos")
    assert "is a function" in capfd.readouterr().out
    calc.command("arg")
    assert "is a function" in capfd.readouterr().out


def test_plugin_function_class_reminder_validate(capfd):
    calc = TestCalculator()
    calc.register_plugin_and_enable(ReminderFunctionClass())
    remind = ["sin", "cos", "tan", "csc", "sec", "cot", "arg", "sinh", "cosh", "tanh", "csch", "sech", "coth", "asin", "acos", "atan", "acsc", "asec", "acot", "asinh", "acosh", "atanh", "acsch", "asech", "acoth"]
    for r in remind:
        calc.command(r)
        assert "is a function" in capfd.readouterr().out
    calc.command("exec")
    calc.command("eval")
    calc.command("compile")
    calc.command("int")
    calc.command("float")
    assert "is a function" not in capfd.readouterr().out


def test_plugin_function_class_reminder_enable_switch(capfd):
    calc = TestCalculator()
    plugin = ReminderFunctionClass()
    calc.register_plugin_and_enable(plugin)
    calc.command("sin")
    assert "is a function" in capfd.readouterr().out
    calc.command("cos")
    assert "is a function" in capfd.readouterr().out
    calc.command("arg")
    assert "is a function" in capfd.readouterr().out
    assert plugin.setting_name
    calc.settings[plugin.setting_name] = False
    calc.command("sin")
    calc.command("cos")
    calc.command("arg")
    assert "is a function" not in capfd.readouterr().out
