from symcalc.plugins.additions.external_links import AddExternalLinks
from tests import TestCalculator


def test_plugin_external_links_instantiate():
    AddExternalLinks()


def test_plugin_external_links_hook():
    calc = TestCalculator()
    plugin = AddExternalLinks()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins


def test_plugin_external_links_context_updated():
    calc = TestCalculator()
    calc.register_plugin(AddExternalLinks())
    assert calc.chksym("desmos")
    assert calc.chksym("symbolab")
    assert calc.chksym("wolframalpha")
    assert calc.chksym("sympygamma")
    assert callable(calc.getsym("desmos"))
    assert callable(calc.getsym("symbolab"))
    assert callable(calc.getsym("wolframalpha"))
    assert callable(calc.getsym("sympygamma"))


def test_plugin_external_links_available():
    calc = TestCalculator()
    calc.register_plugin(AddExternalLinks())
    assert callable(calc.command("desmos"))
    assert callable(calc.command("symbolab"))
    assert callable(calc.command("wolframalpha"))
    assert callable(calc.command("sympygamma"))
