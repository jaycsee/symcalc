from symcalc.plugins.notation.constants import NotationConstants
from tests import TestCalculator, random_str, random_int


def test_plugin_constants_instantiate():
    NotationConstants()


def test_plugin_constants_hook():
    calc = TestCalculator()
    plugin = NotationConstants()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins


def test_plugin_constants_context_updated():
    calc = TestCalculator()
    calc.register_plugin(NotationConstants())
    assert calc.chksym("constants")
    assert isinstance(calc.getsym("constants"), dict)


def test_plugin_constants_available():
    calc = TestCalculator()
    calc.register_plugin(NotationConstants())
    assert isinstance(calc.command("constants"), dict)


def test_plugin_constants_use_default():
    calc = TestCalculator()
    plugin = NotationConstants()
    calc.register_plugin_and_enable(plugin)
    for k, v in plugin.table.items():
        assert calc.command(f"_{k}") == v


def test_plugin_constants_use_custom():
    calc = TestCalculator()
    table = {}
    for i in range(10):
        table[random_str()] = random_str()
    plugin = NotationConstants(table=table)
    calc.register_plugin_and_enable(plugin)
    for k, v in table.items():
        assert calc.command(f"_{k}") == v


def test_plugin_constants_expressions():
    calc = TestCalculator()
    table = {}
    for i in range(10):
        table[random_str()] = random_int(-1000000000, 1000000000)
    plugin = NotationConstants(table=table)
    calc.register_plugin_and_enable(plugin)
    for k1, v1 in table.items():
        for k2, v2 in table.items():
            assert calc.command(f"_{k1} + _{k2}") == v1 + v2
            assert calc.command(f"_{k1} * _{k2}") == v1 * v2
            assert calc.command(f"abs(_{k1}) - abs(_{k2})") == abs(v1) - abs(v2)


def test_plugin_constants_invalid(capfd):
    calc = TestCalculator()
    calc.register_plugin_and_enable(NotationConstants())
    for t in range(20):
        calc.command("_" + random_str())
        assert "NameError" in capfd.readouterr().out
        calc.command(f"{random_int(1,100)}_{random_int(1,100)}_{random_int(1,100)}")
        assert "NameError" not in capfd.readouterr().out


def test_plugin_constants_enable_switch(capfd):
    calc = TestCalculator()
    plugin = NotationConstants()
    calc.register_plugin_and_enable(plugin)
    for k, v in plugin.table.items():
        assert calc.command(f"_{k}") == v
    assert plugin.setting_name
    calc.settings[plugin.setting_name] = False
    for k in plugin.table.keys():
        calc.command(f"_{k}")
        assert "NameError" in capfd.readouterr().out
