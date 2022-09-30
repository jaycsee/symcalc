import sympy
from symcalc.plugins.notation.origin_vectors import NotationOriginVectors
from tests import TestCalculator


def test_plugin_origin_vectors_instantiate():
    NotationOriginVectors()


def test_plugin_origin_vectors_hook():
    calc = TestCalculator()
    plugin = NotationOriginVectors()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins


def test_plugin_origin_vectors_available():
    calc = TestCalculator()
    calc.register_plugin(NotationOriginVectors())
    args = [0]
    for i in range(2, 100):
        args.append(0)
        assert calc.command(f"o{i}") == sympy.Matrix(args)
        assert calc.chksym(f"o{i}")
        assert calc.getsym(f"o{i}") == sympy.Matrix(args)
