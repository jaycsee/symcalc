import pytest
from symcalc import Calculator, CalculatorPlugin

from tests import DefaultPlugin, random_str


def test_plugin_instantiate():
    plugin = CalculatorPlugin(n := random_str(), -1)
    assert plugin.name == n
    assert plugin.priority == -1
    assert plugin.setting_name is None


def test_plugin_register_raw_toggle():
    calc = Calculator()
    plugin = CalculatorPlugin(n := random_str(), -1)
    calc.register_plugin(plugin)
    plugin.register_raw_toggle(calc, t := random_str(), s := random_str(), True)
    assert calc.settings[s]
    calc.command(calc.directive_prefix + t)
    assert not calc.settings[s]
    calc.command(calc.directive_prefix + t)
    assert calc.settings[s]


def test_plugin_register_raw_toggle_fail():
    calc = Calculator()
    plugin = CalculatorPlugin(n := random_str(), -1)
    calc.register_plugin(plugin)
    with pytest.raises(ValueError):
        plugin.register_raw_toggle(calc, None, random_str(), True)
    with pytest.raises(ValueError):
        plugin.register_raw_toggle(calc, random_str(), None, True)


def test_plugin_register_toggle():
    calc = Calculator()
    plugin = CalculatorPlugin(n := random_str(), -1)
    calc.register_plugin(plugin)
    plugin.register_toggle(calc, t := random_str(), s := random_str(), True)
    assert plugin.setting_name == s
    assert calc.settings[s]
    calc.command(calc.directive_prefix + t)
    assert not calc.settings[s]
    calc.command(calc.directive_prefix + t)
    assert calc.settings[s]
    with pytest.raises(ValueError):
        plugin.register_toggle(calc, random_str(), random_str(), False)


def test_plugin_if_enabled():
    calc = Calculator()
    t = random_str()

    class Plugin(CalculatorPlugin):
        def __init__(self):
            super().__init__(random_str(), -1)
            self.count = 0

        def hook(self, calc: Calculator) -> None:
            self.register_toggle(calc, t, random_str(), False)

        @CalculatorPlugin.if_enabled
        def handle_command(self, command):
            self.count += 1

    plugin = Plugin()
    assert plugin.count == 0
    calc.register_plugin(plugin)
    assert plugin.count == 0
    calc.command("pass")
    assert plugin.count == 0
    calc.command("pass")
    assert plugin.count == 0
    calc.command(calc.directive_prefix + t)
    assert plugin.count == 0
    calc.command("pass")
    assert plugin.count == 1
    calc.command("pass")
    assert plugin.count == 2


def test_plugin_if_enabled_fail(capfd):
    calc = Calculator()
    t = random_str()

    class Plugin(DefaultPlugin):
        @CalculatorPlugin.if_enabled
        def handle_command(self, command):
            pass

    plugin = Plugin()
    calc.register_plugin(plugin)
    calc.command("pass")
    assert "toggle" in capfd.readouterr().err


def test_plugin_if_external_enabled():
    calc = Calculator()
    t1 = random_str()
    t2 = random_str()
    s1 = random_str()
    s2 = random_str()

    class Plugin(CalculatorPlugin):
        def __init__(self):
            super().__init__(random_str(), -1)
            self.count = 0

        def hook(self, calc: Calculator) -> None:
            self.register_raw_toggle(calc, t1, s1, False)
            self.register_raw_toggle(calc, t2, s2, False)

        @CalculatorPlugin.if_external_enabled(s1, s2)
        def handle_command(self, command):
            self.count += 1

    plugin = Plugin()

    assert plugin.count == 0
    calc.register_plugin(plugin)
    assert plugin.count == 0

    calc.command("pass")
    assert plugin.count == 0
    calc.command("pass")
    assert plugin.count == 0

    calc.command(calc.directive_prefix + t1)
    assert plugin.count == 0
    calc.command("pass")
    assert plugin.count == 0
    calc.command(calc.directive_prefix + t1)
    assert plugin.count == 0
    calc.command("pass")
    assert plugin.count == 0

    calc.command(calc.directive_prefix + t2)
    assert plugin.count == 0
    calc.command("pass")
    assert plugin.count == 0
    calc.command(calc.directive_prefix + t2)
    assert plugin.count == 0
    calc.command("pass")
    assert plugin.count == 0

    calc.command(calc.directive_prefix + t1)
    calc.command(calc.directive_prefix + t2)

    calc.command("pass")
    assert plugin.count == 1
    calc.command("pass")
    assert plugin.count == 2


def test_plugin_no_action():
    calc = Calculator()

    for name in [random_str() for i in range(5)]:
        calc.command(f"{name } = 0")

    original = {}
    original.update(calc.context.__dict__)

    calc.register_plugin(CalculatorPlugin("Plugin", -1))
    calc.command("")
    calc.command("1+2")
    calc.command("is")
    calc.command("raise ValueError()")

    new = {}
    new.update(calc.context.__dict__)

    assert original == new
