import sympy
from symcalc.plugins.additions.factordb import AddFactorDB
from tests import TestCalculator, random_int


def test_plugin_factordb_instantiate():
    AddFactorDB()


def test_plugin_factordb_hook():
    calc = TestCalculator()
    plugin = AddFactorDB()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins


def test_plugin_factordb_context_updated():
    calc = TestCalculator()
    calc.register_plugin(AddFactorDB())
    assert calc.chksym("factordb")
    assert callable(calc.getsym("factordb"))


def test_plugin_factordb_available():
    calc = TestCalculator()
    calc.register_plugin(AddFactorDB())
    assert callable(calc.command("factordb"))


def test_plugin_factordb_example():
    calc = TestCalculator()
    calc.register_plugin(AddFactorDB())
    calc.command("r = factordb(29928893193015398318666605389344864349536211)")
    r = calc.getsym("r")
    assert r.n == 29928893193015398318666605389344864349536211
    assert r.status == "FF"
    assert r.factors == {3: 1, 11: 1, 648181: 1, 1399202008951362319095335248405636807: 1}


def test_plugin_factordb_validate():
    calc = TestCalculator()
    calc.register_plugin(AddFactorDB())
    for i in range(3):
        n = random_int(10000, 100000)
        c = calc.command(f"factordb({n})")
        assert c is not None
        assert c.factors == sympy.factorint(n)
