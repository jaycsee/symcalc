from symcalc.plugins.output.store import OutputStore
from tests import TestCalculator, generate_test_values, random_str


def test_plugin_output_store_instantiate():
    OutputStore()


def test_plugin_output_store_hook():
    calc = TestCalculator()
    plugin = OutputStore()
    calc.register_plugin_and_enable(plugin)
    assert plugin in calc.plugins


def test_plugin_output_store_context_updated():
    calc = TestCalculator()
    calc.register_plugin_and_enable(OutputStore())
    assert calc.chksym("output_store")
    assert callable(calc.getsym("output_store"))


def test_plugin_output_store_available():
    calc = TestCalculator()
    calc.register_plugin_and_enable(OutputStore())
    assert callable(calc.command("output_store"))


def test_plugin_output_store_python(capfd):
    calc = TestCalculator()
    plugin = OutputStore()
    calc.register_plugin_and_enable(plugin)
    l = [None]
    for i in range(20):
        s = random_str()
        calc.command(f"'{s}'")
        l.append(s)
        assert "Result" in capfd.readouterr().out
        assert calc.context.out[-1] == s
    for x in generate_test_values(4, real=True, complex=True, include_edge_cases=False):
        l.append(x)
        calc.command(str(x))
        assert "Result" in capfd.readouterr().out
        assert calc.context.out[-1] == x


def test_plugin_output_store_sympy(capfd):
    calc = TestCalculator()
    plugin = OutputStore()
    calc.register_plugin_and_enable(plugin)
    l = [None]
    for x in generate_test_values(4, sympy_objects=True, real=True, complex=True, include_edge_cases=False):
        if abs(x) < 0.00000000001:
            continue
        l.append(x)
        calc.command(f"sympify('{str(x)}',rational=True)")
        assert "Result" in capfd.readouterr().out
        assert abs(calc.context.out[-1].evalf() - x.evalf()) < 0.0001


def test_plugin_output_store_invalid():
    plugin = OutputStore()
    calc = TestCalculator()
    plugin = OutputStore()
    calc.register_plugin_and_enable(plugin)
    for i in range(100):
        calc.command("sympify(0)")
        calc.command("sympify(1)")
        calc.command(f"Symbol('{random_str()}')")
    assert len(calc.context.out) == 1


def test_plugin_output_store_duplicates(capfd):
    calc = TestCalculator()
    plugin = OutputStore()
    calc.register_plugin_and_enable(plugin)
    l = [None]
    for i in range(20):
        s = random_str()
        calc.command(f"'{s}'")
        l.append(s)
        assert "Result" in capfd.readouterr().out
        assert len(calc.context.out) == len(l)
        calc.command(f"'{s}'")
        calc.command(f"'{s}'")
        assert len(calc.context.out) == len(l)


def test_plugin_output_store_example(capfd):
    calc = TestCalculator()
    plugin = OutputStore()
    calc.register_plugin_and_enable(plugin)
    calc.command("x=Symbol('x')")
    r = calc.command("2*x")
    assert "Result" in capfd.readouterr().out
    assert len(calc.context.out) == 2
    assert calc.context.out[1] == calc.context.out[-1] == calc.command("out[1]") == calc.command("out[-1]") == r


def test_plugin_output_store_enable_switch(capfd):
    calc = TestCalculator()
    plugin = OutputStore()
    calc.register_plugin(plugin)
    calc.settings[plugin.setting_name] = False

    for x in generate_test_values(2, False, real=True, complex=True):
        calc.command(str(x))
    for x in generate_test_values(2, True, real=True, complex=True):
        calc.command(f"sympify('{str(x)}')")
    assert capfd.readouterr().out.count("Decimal") == 0
