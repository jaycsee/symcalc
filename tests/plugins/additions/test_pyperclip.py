from symcalc.plugins.additions.pyperclip import AddPyperclip
from tests import TestCalculator, random_str


def test_plugin_pyperclip_instantiate():
    AddPyperclip()


def test_plugin_pyperclip_hook():
    calc = TestCalculator()
    plugin = AddPyperclip()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins


def test_plugin_pyperclip_context_updated():
    calc = TestCalculator()
    calc.register_plugin(AddPyperclip())
    assert calc.chksym("pyperclip")
    assert calc.chksym("copy")
    assert calc.chksym("paste")
    assert callable(calc.getsym("copy"))
    assert callable(calc.getsym("paste"))


def test_plugin_pyperclip_available():
    calc = TestCalculator()
    calc.register_plugin(AddPyperclip())
    assert callable(calc.command("copy"))
    assert callable(calc.command("paste"))


def test_plugin_pyperclip_example():
    calc = TestCalculator()
    calc.register_plugin(AddPyperclip())
    calc.command("copy('Test')")
    assert calc.command("paste()") == "Test"


def test_plugin_pyperclip_validate():
    calc = TestCalculator()
    calc.register_plugin(AddPyperclip())
    for i in range(10):
        t = random_str()
        calc.command(f"copy('{t}')")
        assert calc.command("paste()") == t
