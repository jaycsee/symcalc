import sympy
from symcalc.plugins.additions.origin_vectors import AddOriginVectors
from tests import TestCalculator


def test_plugin_origin_vectors_instantiate():
    AddOriginVectors()


def test_plugin_origin_vectors_hook():
    calc = TestCalculator()
    plugin = AddOriginVectors()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins


def test_plugin_origin_vectors_context_updated():
    calc = TestCalculator()
    calc.register_plugin(AddOriginVectors())
    args = [0]
    for i in range(2, 100):
        args.append(0)
        assert calc.chksym(f"o{i}")
        assert calc.getsym(f"o{i}") == sympy.Matrix(args)


def test_plugin_origin_vectors_available():
    calc = TestCalculator()
    calc.register_plugin(AddOriginVectors())
    args = [0]
    for i in range(2, 100):
        args.append(0)
        assert calc.command(f"o{i}") == sympy.Matrix(args)
