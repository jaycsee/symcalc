import string

from symcalc.plugins.functionality.symbols import AutoSymbol
from tests import TestCalculator, random_str


def test_plugin_functionality_symbols_instantiate():
    AutoSymbol()


def test_plugin_functionality_symbols_hook():
    calc = TestCalculator()
    plugin = AutoSymbol()
    calc.register_plugin_and_enable(plugin)
    assert plugin in calc.plugins


def test_plugin_functionality_symbols_use():
    for l in range(1, len(random_str()), 2):
        calc = TestCalculator()
        plugin = AutoSymbol()
        calc.register_plugin_and_enable(plugin)
        calc.settings["auto_symbol_char"] = False
        for x in range(100):
            t = random_str()[:l]
            if calc.chksym(t):
                continue
            calc.command(t)
            assert calc.chksym(t)


def test_plugin_functionality_symbols_use_char():
    for l in range(1, len(random_str()), 2):
        calc = TestCalculator()
        plugin = AutoSymbol()
        calc.register_plugin_and_enable(plugin)
        for x in range(30):
            t = random_str()[:l]
            calc.command(t)
            for a in t:
                assert calc.chksym(a)


def test_plugin_functionality_symbols_use_expr():
    calc = TestCalculator()
    plugin = AutoSymbol()
    calc.register_plugin_and_enable(plugin)
    calc.settings["auto_symbol_char"] = False
    calc.command("a+1")
    calc.command("2*b")
    calc.command("c/d")
    calc.command("E**e")
    calc.command("sin(f)")
    calc.command("cos(g*h/i**j+k)-3*l**2")
    calc.command("exp(2**9*m)*n**o**p+q*r/s")
    calc.command("1/t*u*(9*v)*w+x-y**z")
    calc.command("aa+1")
    calc.command("2*ab")
    calc.command("ac/ad")
    calc.command("E**ae")
    calc.command("sin(af)")
    calc.command("cos(ag*ah/ai**aj+ak)-3*al**2")
    calc.command("exp(2**9*am)*an**ao**ap+aq*ar")
    calc.mksym("as")
    calc.command("1/at*au*(9*av)*aw+ax-ay**az")
    for x in string.ascii_lowercase:
        assert calc.chksym(x)
        assert calc.chksym(f"a{x}")


def test_plugin_functionality_symbols_use_expr_char():
    calc = TestCalculator()
    plugin = AutoSymbol()
    calc.register_plugin_and_enable(plugin)
    calc.command("cos(ab*cd/ef**gh+ij)-3*kl**2")
    calc.command("exp(2**9*mn)*no**pq**rs+tu")
    calc.command("1/vw*xy*(9*z)")
    for x in string.ascii_lowercase:
        assert calc.chksym(x)


def test_plugin_functionality_symbols_example():
    calc = TestCalculator()
    plugin = AutoSymbol()
    calc.register_plugin_and_enable(plugin)
    calc.settings["auto_symbol_char"] = False

    assert not calc.chksym("x")
    calc.command("x")
    assert calc.chksym("x")

    calc.command("x")
    assert calc.chksym("x")

    assert not calc.chksym("yz")
    calc.command("yz")
    assert calc.chksym("yz")


def test_plugin_functionality_symbols_example_char():
    calc = TestCalculator()
    plugin = AutoSymbol()
    calc.register_plugin_and_enable(plugin)

    assert not calc.chksym("x")
    calc.command("x")
    assert calc.chksym("x")

    calc.command("x")
    assert calc.chksym("x")

    assert not calc.chksym("yz")
    calc.command("yz")
    assert calc.chksym("y")
    assert calc.chksym("z")


def test_plugin_functionality_symbols_enable_switch(capfd):
    calc = TestCalculator()
    plugin = AutoSymbol()
    calc.register_plugin(plugin)
    assert plugin.setting_name

    calc.settings[plugin.setting_name] = False
    for x in range(10):
        t = random_str()
        calc.command(t)
        assert "error" in capfd.readouterr().out.lower()

    calc.settings[plugin.setting_name] = True
    for x in range(10):
        t = random_str()
        calc.command(t)
        assert "error" not in capfd.readouterr().out.lower()
        assert calc.chksym(t)
