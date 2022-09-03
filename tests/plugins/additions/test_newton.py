import sympy
from symcalc.plugins.additions.newton import AddNewtonsMethod
from tests import TestCalculator, random_int


def test_plugin_newton_instantiate():
    AddNewtonsMethod()


def test_plugin_newton_hook():
    calc = TestCalculator()
    plugin = AddNewtonsMethod()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins


def test_plugin_newton_context_updated():
    calc = TestCalculator()
    calc.register_plugin(AddNewtonsMethod())
    assert calc.chksym("newton")
    assert callable(calc.getsym("newton"))


def test_plugin_newton_available():
    calc = TestCalculator()
    calc.register_plugin(AddNewtonsMethod())
    assert callable(calc.command("newton"))


def test_plugin_newton_example():
    calc = TestCalculator()
    calc.register_plugin(AddNewtonsMethod())
    calc.command("x = Symbol('x')")
    assert calc.command("newton(x*(x**2-1), 2, x, 2)") == sympy.Rational(8192, 7117)


def test_plugin_newton_validate():
    calc = TestCalculator()
    calc.register_plugin(AddNewtonsMethod())
    calc.command("x = Symbol('x')")
    for i in range(10):
        a, b = [random_int(-1000, 1000) / 100 for x in range(2)]

        def f(x):
            return a * x**2 + b * x

        ans = calc.command(f"newton({a}*x**2+{b}*x, 2, x, 100)")
        assert abs(f(ans)) < 0.1
