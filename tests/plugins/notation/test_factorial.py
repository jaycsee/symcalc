from __future__ import annotations

import sympy
from symcalc.plugins.notation.factorial import NotationFactorial
from tests import TestCalculator, random_int


def test_plugin_notation_factorial_instantiate():
    NotationFactorial()


def test_plugin_notation_factorial_hook():
    calc = TestCalculator()
    plugin = NotationFactorial()
    calc.register_plugin_and_enable(plugin)
    assert plugin in calc.plugins


def test_plugin_notation_factorial_use_basic():
    calc = TestCalculator()
    plugin = NotationFactorial()
    calc.register_plugin_and_enable(plugin)

    acc = 1
    for i in range(1, 100):
        acc *= i
        assert calc.command(f"{i}!") == acc


def test_plugin_notation_factorial_use_rationals():
    calc = TestCalculator()
    plugin = NotationFactorial()
    calc.register_plugin_and_enable(plugin)

    for i in range(10):
        a = random_int(1, 500)
        b = random_int(1, 100000)
        assert abs(calc.command(f"{a}!") - sympy.factorial(a)) <= 0.01  # type:ignore
        assert abs(calc.command(f"{b / 1000}!") - sympy.factorial(b / 1000)) <= 0.01  # type:ignore


def test_plugin_notation_factorial_use_nested():
    calc = TestCalculator()
    plugin = NotationFactorial()
    calc.register_plugin_and_enable(plugin)

    assert abs(calc.command("abs(-5! * 2.6! * sin(3!)) * 2!/3!") - 41.5437628) <= 0.00001  # type: ignore
    assert calc.command("(1!+2!*2!)!!") == 6689502913449127057588118054090372586752746333138029810295671352301633557244962989366874165271984981308157637893214090552534408589408121859898481114389650005964960521256960000000000000000000000000000
    assert abs(calc.command("log(log((exp(2)!+1)!))!") - 117321252.926657) <= 0.00001  # type: ignore


def test_plugin_notation_factorial_example():
    calc = TestCalculator()
    plugin = NotationFactorial()
    calc.register_plugin_and_enable(plugin)

    assert calc.command("6!") == 720
    assert abs(calc.command("2.3!") - 2.6834373) <= 0.00001  # type: ignore
    assert calc.command("-5!") == -120


def test_plugin_notation_factorial_enable_switch(capfd):
    calc = TestCalculator()
    plugin = NotationFactorial()
    calc.register_plugin(plugin)
    assert plugin.setting_name

    calc.settings[plugin.setting_name] = False
    calc.command("3!")
    assert "error" in capfd.readouterr().out.lower()

    calc.settings[plugin.setting_name] = True
    assert calc.command("3!") == 6
