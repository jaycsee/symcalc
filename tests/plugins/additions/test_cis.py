from symcalc.plugins.additions.cis import AddCisFunction
from tests import TestCalculator


def test_plugin_cis_instantiate():
    AddCisFunction()


def test_plugin_cis_hook():
    calc = TestCalculator()
    plugin = AddCisFunction()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins


def test_plugin_cis_context_updated():
    calc = TestCalculator()
    calc.register_plugin(AddCisFunction())
    assert calc.chksym("cis")
    assert callable(calc.getsym("cis"))


def test_plugin_cis_available():
    calc = TestCalculator()
    calc.register_plugin(AddCisFunction())
    assert callable(calc.command("cis"))


def test_plugin_cis_example():
    calc = TestCalculator()
    calc.register_plugin(AddCisFunction())
    assert calc.command("2*cis(pi/3)") == calc.command("1+sqrt(3)*I")


def test_plugin_cis_validate_values():
    calc = TestCalculator()
    calc.register_plugin(AddCisFunction())
    assert calc.command("2*cis(pi/6)") == calc.command("sqrt(3)+I")
    assert calc.command("2*cis(pi/4)") == calc.command("sqrt(2)+sqrt(2)*I")
    assert calc.command("2*cis(pi/3)") == calc.command("1+sqrt(3)*I")
    assert calc.command("cis(pi/2)") == calc.command("I")
    assert calc.command("2*cis(2*pi/3)") == calc.command("-1+sqrt(3)*I")
    assert calc.command("2*cis(3*pi/4)") == calc.command("-sqrt(2)+sqrt(2)*I")
    assert calc.command("2*cis(5*pi/6)") == calc.command("-sqrt(3)+I")
    assert calc.command("2*cis(7*pi/6)") == calc.command("-sqrt(3)-I")
    assert calc.command("2*cis(5*pi/4)") == calc.command("-sqrt(2)-sqrt(2)*I")
    assert calc.command("2*cis(4*pi/3)") == calc.command("-1-sqrt(3)*I")
    assert calc.command("cis(3*pi/2)") == calc.command("-I")
    assert calc.command("2*cis(5*pi/3)") == calc.command("1-sqrt(3)*I")
    assert calc.command("2*cis(7*pi/4)") == calc.command("sqrt(2)-sqrt(2)*I")
    assert calc.command("2*cis(11*pi/6)") == calc.command("sqrt(3)-I")


def test_plugin_cis_validate_abs():
    calc = TestCalculator()
    calc.register_plugin(AddCisFunction())
    for i in range(-50, 50):
        assert calc.command(f"simplify(abs(cis({i})))") == 1
