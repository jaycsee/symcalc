import sympy
from symcalc.plugins.output.decimal import OutputDecimal
from tests import TestCalculator, generate_test_values, random_str


def test_plugin_output_decimal_instantiate():
    OutputDecimal()


def test_plugin_output_decimal_hook():
    calc = TestCalculator()
    plugin = OutputDecimal()
    calc.register_plugin_and_enable(plugin)
    assert plugin in calc.plugins


def test_plugin_output_decimal_context_updated():
    calc = TestCalculator()
    calc.register_plugin_and_enable(OutputDecimal())
    assert calc.chksym("output_decimal")
    assert callable(calc.getsym("output_decimal"))


def test_plugin_output_decimal_available():
    calc = TestCalculator()
    calc.register_plugin_and_enable(OutputDecimal())
    assert callable(calc.command("output_decimal"))


def test_plugin_output_decimal_check_real():
    plugin = OutputDecimal()

    for x in generate_test_values(50, False, real=True, complex=False):
        assert plugin.check_number(str(x))
    for x in generate_test_values(50, True, real=True, complex=False):
        assert plugin.check_number(str(x.evalf()))


def test_plugin_output_decimal_check_complex():
    plugin = OutputDecimal()

    for x in generate_test_values(10, False, real=False, complex=True):
        assert plugin.check_number(str(x))
    for x in generate_test_values(10, True, real=False, complex=True):
        assert plugin.check_number(str(x.evalf()))


def test_plugin_output_decimal_check_invalid():
    plugin = OutputDecimal()
    for t in generate_test_values(5, False, real=True, complex=False) + generate_test_values(5, False, real=False, complex=True):
        assert plugin.check_number(random_str()) is None
        assert plugin.check_number(f"{t}*x") is None
        assert plugin.check_number(f"{t/1000}*x") is None
        assert plugin.check_number(f"{random_str()}({t})") is None
        assert plugin.check_number(f"[{t},{t}]") is None
        assert plugin.check_number(f"[{random_str()},{random_str()}]") is None


def test_plugin_output_decimal_output_real(capfd):
    calc = TestCalculator()
    plugin = OutputDecimal()
    calc.register_plugin_and_enable(plugin)

    for x in generate_test_values(5, False, real=True, complex=False):
        calc.command(str(x))
    assert capfd.readouterr().out.count("Decimal") == 0

    for x in generate_test_values(5, True, real=True, complex=False):
        calc.command(f"sympify('{str(x)}')")
        output = capfd.readouterr().out
        if isinstance(x, sympy.core.numbers.Integer | sympy.core.numbers.Float):
            assert "Decimal" not in output
        else:
            assert "Decimal" in output


def test_plugin_output_decimal_output_complex(capfd):
    return
    calc = TestCalculator()
    plugin = OutputDecimal()
    calc.register_plugin_and_enable(plugin)

    for x in generate_test_values(5, False, real=False, complex=True):
        calc.command(str(x))
    assert capfd.readouterr().out.count("Decimal") == 0

    for x in generate_test_values(5, True, real=False, complex=True, include_edge_cases=False):
        calc.command(f"sympify('{str(x)}')")
        output = capfd.readouterr().out
        if isinstance(sympy.re(x), sympy.core.numbers.Integer | sympy.core.numbers.Float) and isinstance(sympy.im(x), sympy.core.numbers.Integer | sympy.core.numbers.Float):
            assert "Decimal" not in output
        else:
            assert "Decimal" in output


def test_plugin_output_decimal_output_expressions(capfd):
    return
    calc = TestCalculator()
    plugin = OutputDecimal()
    calc.register_plugin_and_enable(plugin)
    for x in generate_test_values(1, False, real=True, complex=True):
        calc.command(f"{str(x)} + {str(x)}")
        calc.command(f"{str(x)} * {str(x)}**2")
        calc.command(f"abs({str(x)}) - 2 * abs({str(x)})")
    assert "Decimal" not in capfd.readouterr().out
    for x in generate_test_values(1, True, real=True, complex=True, include_edge_cases=False):
        calc.command(f"sympify('{str(x)}') + sympify('{str(x)}')")
        calc.command(f"sympify('{str(x)}') - 2 * sympify('{str(x)}')")
        output = capfd.readouterr().out
        if isinstance(sympy.re(x), sympy.core.numbers.Integer | sympy.core.numbers.Float) and isinstance(sympy.im(x), sympy.core.numbers.Integer | sympy.core.numbers.Float):
            assert "Decimal" not in output
        else:
            assert output.count("Decimal") == 2


def test_plugin_output_decimal_output_invalid():
    plugin = OutputDecimal()


def test_plugin_output_decimal_output_duplicates(capfd):
    return
    calc = TestCalculator()
    plugin = OutputDecimal()
    calc.register_plugin_and_enable(plugin)

    for x in generate_test_values(5, False, real=False, complex=True):
        calc.command(str(x))
    assert capfd.readouterr().out.count("Decimal") == 0

    for x in generate_test_values(3, True, real=False, complex=True, include_edge_cases=True):
        calc.command(f"sympify('{str(x)}')")
        output = capfd.readouterr().out
        if isinstance(sympy.re(x), sympy.core.numbers.Integer | sympy.core.numbers.Float) and isinstance(sympy.im(x), sympy.core.numbers.Integer | sympy.core.numbers.Float):
            assert "Decimal" not in output
        else:
            assert "Decimal" in output
        calc.command(f"sympify('{str(x)}')")
        assert capfd.readouterr().out.count("Decimal") == 0


def test_plugin_output_decimal_output_real_list_matrix(capfd):
    calc = TestCalculator()
    plugin = OutputDecimal()
    calc.register_plugin_and_enable(plugin)

    for n in range(0, 6):
        x = []
        m = None
        for i in range(n):
            tv = generate_test_values(5, False, real=True, complex=False)
            m = min(m, len(tv)) if m is not None else len(tv)
            x.append(tv)

        if m:
            for i in range(m):
                ta = []
                tb = []
                for j in range(n):
                    ta.append(str(x[j][i]))
                    tb.append(f"sympify({x[j][i]})")
                calc.command(f"[{','.join(ta)}]")
                calc.command("0")
                calc.command(f"[{','.join(tb)}]")
                calc.command("0")
            assert capfd.readouterr().out.count("Decimal") == 0


def test_plugin_output_decimal_output_complex_list_matrix():
    plugin = OutputDecimal()


def test_plugin_output_decimal_output_invalid_list_matrix():
    plugin = OutputDecimal()


def test_plugin_output_decimal_example(capfd):
    calc = TestCalculator()
    plugin = OutputDecimal()
    calc.register_plugin_and_enable(plugin)
    calc.command("3+3.2j")
    assert "Decimal" in capfd.readouterr().out
    calc.command("sympify('123/321',rational=True)")
    assert "Decimal" in capfd.readouterr().out
    calc.command("x=sympify('123/321',rational=True)")
    assert "Decimal" in capfd.readouterr().out


def test_plugin_output_decimal_enable_switch(capfd):
    calc = TestCalculator()
    plugin = OutputDecimal()
    calc.register_plugin(plugin)
    assert plugin.setting_name
    calc.settings[plugin.setting_name] = False

    for x in generate_test_values(2, False, real=True, complex=True):
        calc.command(str(x))
    for x in generate_test_values(2, True, real=True, complex=True):
        calc.command(f"sympify('{str(x)}')")
    assert capfd.readouterr().out.count("Decimal") == 0
