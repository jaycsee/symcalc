import random
import string

import sympy
from symcalc.plugins.functionality.functions import AutoFunction
from tests import TestCalculator, generate_test_values, random_str


def test_plugin_functionality_functions_instantiate():
    AutoFunction()


def test_plugin_functionality_functions_hook():
    calc = TestCalculator()
    plugin = AutoFunction()
    calc.register_plugin_and_enable(plugin)
    assert plugin in calc.plugins


def test_plugin_functionality_functions_basic():
    calc = TestCalculator()
    plugin = AutoFunction()
    calc.register_plugin_and_enable(plugin)
    calc.mksym("sy")
    for x in string.ascii_lowercase:
        calc.command(f"{x}(sy)")
        assert isinstance(calc.getsym(x), sympy.core.function.UndefinedFunction)
    for t in range(100):
        x = random_str()
        calc.command(f"{x}(sy)")
        assert isinstance(calc.getsym(x), sympy.core.function.UndefinedFunction)


def test_plugin_functionality_functions_num():
    calc = TestCalculator()
    plugin = AutoFunction()
    calc.register_plugin_and_enable(plugin)
    calc.mksym("sy")
    for x in string.ascii_lowercase[:5]:
        for n in generate_test_values(4, False, True, True):
            calc.command(f"{x}({n})")
            assert isinstance(calc.getsym(x), sympy.core.function.UndefinedFunction)
    for t in range(3):
        x = random_str()
        for n in generate_test_values(4, False, True, True):
            calc.command(f"{x}({n})")
            assert isinstance(calc.getsym(x), sympy.core.function.UndefinedFunction)


def test_plugin_functionality_functions_multi_arg():
    calc = TestCalculator()
    plugin = AutoFunction()
    calc.register_plugin_and_enable(plugin)
    for n in range(1, 11):
        for t in range(10):
            f = random_str()
            calc.command(f"{f}({', '.join(random_str() for a in range(n))})")
            assert isinstance(calc.getsym(f), sympy.core.function.UndefinedFunction)


def test_plugin_functionality_functions_multi_arg_num():
    calc = TestCalculator()
    plugin = AutoFunction()
    calc.register_plugin_and_enable(plugin)
    v = generate_test_values(4, False, True, True, True)
    for n in range(1, 11):
        for s in range(0, n):
            for t in range(100):
                f = random_str()
                args = list(random_str() for a in range(s))
                args += random.choices(v, k=n - s)
                random.shuffle(args)
                calc.command(f"{f}({', '.join(random_str() for a in range(n))})")
                assert isinstance(calc.getsym(f), sympy.core.function.UndefinedFunction)


def test_plugin_functionality_functions_example():
    calc = TestCalculator()
    plugin = AutoFunction()
    calc.register_plugin_and_enable(plugin)
    calc.mksym("x,a,b,c")
    calc.command("f(x)")
    calc.command("g(2)")
    calc.command("h(a,b,c)")
    assert isinstance(calc.getsym("f"), sympy.core.function.UndefinedFunction)
    assert isinstance(calc.getsym("g"), sympy.core.function.UndefinedFunction)
    assert isinstance(calc.getsym("h"), sympy.core.function.UndefinedFunction)


def test_plugin_functionality_functions_enable_switch():
    calc = TestCalculator()
    plugin = AutoFunction()
    calc.register_plugin(plugin)
    assert plugin.setting_name

    calc.settings[plugin.setting_name] = False
    for x in range(100):
        f = random_str()
        calc.command(f"{f}(0)")
        assert not calc.chksym(f)

    calc.settings[plugin.setting_name] = True
    for x in range(100):
        f = random_str()
        calc.command(f"{f}(0)")
        assert calc.chksym(f)
        assert isinstance(calc.getsym(f), sympy.core.function.UndefinedFunction)
