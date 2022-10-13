import sympy
from symcalc.plugins.functionality.exact import AutoExact
from tests import TestCalculator, generate_test_values, random_ints


def test_plugin_functionality_exact_instantiate():
    AutoExact()


def test_plugin_functionality_exact_hook():
    calc = TestCalculator()
    plugin = AutoExact()
    calc.register_plugin_and_enable(plugin)
    assert plugin in calc.plugins


def test_plugin_functionality_exact_floats():
    calc = TestCalculator()
    plugin = AutoExact()
    calc.register_plugin_and_enable(plugin)
    for t in generate_test_values(4):
        assert calc.command(str(t)) == sympy.Rational(str(t))


def test_plugin_functionality_exact_repeating():
    calc = TestCalculator()
    plugin = AutoExact()
    calc.register_plugin_and_enable(plugin)
    for t in generate_test_values(4):
        if not isinstance(t, float) or "e" in str(t):
            continue
        for x in random_ints(4):
            x = abs(x)
            if x != 0:
                assert abs(calc.command(f"{t}[{x}]") - sympy.simplify(f"{t}[{x}]")) < 0.00001
            else:
                assert abs(calc.command(f"{t}[{x}]") - sympy.simplify(str(t))) < 1


def test_plugin_functionality_exact_example():
    calc = TestCalculator()
    plugin = AutoExact()
    calc.register_plugin_and_enable(plugin)
    assert calc.command("1.2") == sympy.Rational(6, 5)
    assert calc.command("324.12") == sympy.Rational(8103, 25)
    assert calc.command("0.[127]") == sympy.Rational(127, 999)
    assert calc.command("421.1[16]") == sympy.Rational(83381, 198)


def test_plugin_functionality_exact_enable_switch():
    calc = TestCalculator()
    plugin = AutoExact()
    calc.register_plugin(plugin)
    assert plugin.setting_name

    calc.settings[plugin.setting_name] = False
    for x in generate_test_values(2, False, real=True):
        assert isinstance(calc.command(str(x)), int | float)
    calc.settings[plugin.setting_name] = True
    for x in generate_test_values(2, False, real=True):
        assert not isinstance(calc.command(str(x)), int | float)
