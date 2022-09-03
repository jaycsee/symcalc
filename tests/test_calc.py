import code
import pytest
from symcalc import Calculator, CalculatorPlugin, CalculatorContext

from tests import random_str, DefaultPlugin


def test_calc_instantiate():
    prefix = random_str()
    calc = Calculator(None, prefix)
    assert isinstance(calc.context, CalculatorContext)
    assert calc.directive_prefix == prefix
    assert calc.current_command is None
    assert calc.incomplete_command is None
    assert isinstance(calc.console, code.InteractiveConsole)
    assert not calc.strict_python
    assert len(calc.settings) == len(calc.plugins) == len(calc.plugin_priorities) == len(calc.directives) == 0


def test_calc_register_plugin():
    calc = Calculator()
    name = random_str()

    class Plugin(CalculatorPlugin):
        def __init__(self):
            super().__init__(name, -1)
            self.count = 0

        def hook(self, calc):
            self.count += 1

        def begin_interaction(self, command):
            self.count += 1

        def parse_command(self, command):
            self.count += 1

        def handle_command(self, command):
            self.count += 1

        def command_success(self, command):
            self.count += 1

        def end_interaction(self, command):
            self.count += 1

    plugin = Plugin()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins
    calc.command("pass")
    assert plugin.count == 6


def test_calc_register_directive():
    global run
    calc = Calculator()
    run = False

    def directive(calc, command):
        global run
        run = True

    c = random_str()
    calc.command(calc.directive_prefix + c)
    assert not run
    calc.register_directive(c, directive)
    assert c in calc.directives
    assert not run
    calc.command(calc.directive_prefix + c)
    assert run
    with pytest.raises(ValueError):
        calc.register_directive(c, directive)


def test_calc_notify_assert_fail():
    class BeginInteractionFail(DefaultPlugin):
        def begin_interaction(self, command):
            assert False

    class ParseFail(DefaultPlugin):
        def parse_command(self, command):
            assert False

    class HandleFail(DefaultPlugin):
        def handle_command(self, command):
            assert False

    class SyntaxErrorFail(DefaultPlugin):
        def handle_syntax_error(self, command, data):
            assert False

    class RuntimeErrorFail(DefaultPlugin):
        def handle_runtime_error(self, command, data):
            assert False

    class ResendFail(DefaultPlugin):
        def handle_resend(self, command):
            assert False

        def handle_syntax_error(self, command, data):
            command.command = "pass"
            command.resend_command = True

    class SuccessFail(DefaultPlugin):
        def command_success(self, command):
            assert False

    class FailFail(DefaultPlugin):
        def command_fail(self, command):
            assert False

    class EndInteractionFail(DefaultPlugin):
        def end_interaction(self, command):
            assert False

    calc = Calculator()
    calc.register_plugin(BeginInteractionFail())
    with pytest.raises(AssertionError) as exc:
        calc.command("pass")
    calc = Calculator()
    calc.register_plugin(HandleFail())
    with pytest.raises(AssertionError) as exc:
        calc.command("pass")
    calc = Calculator()
    calc.register_plugin(ParseFail())
    with pytest.raises(AssertionError) as exc:
        calc.command("pass")
    calc = Calculator()
    calc.register_plugin(SyntaxErrorFail())
    with pytest.raises(AssertionError) as exc:
        calc.command("is")
    calc = Calculator()
    calc.register_plugin(RuntimeErrorFail())
    with pytest.raises(AssertionError) as exc:
        calc.command("raise ValueError()")
    calc = Calculator()
    calc.register_plugin(ResendFail())
    with pytest.raises(AssertionError) as exc:
        calc.command("is")
    calc = Calculator()
    calc.register_plugin(SuccessFail())
    with pytest.raises(AssertionError) as exc:
        calc.command("pass")
    calc = Calculator()
    calc.register_plugin(FailFail())
    with pytest.raises(AssertionError) as exc:
        calc.command("is")
    calc = Calculator()
    calc.register_plugin(EndInteractionFail())
    with pytest.raises(AssertionError) as exc:
        calc.command("pass")


def test_calc_notify_plugin_exception(capfd):
    class BeginInteractionFail(DefaultPlugin):
        def begin_interaction(self, command):
            raise ValueError()

    class ParseFail(DefaultPlugin):
        def parse_command(self, command):
            raise ValueError()

    class HandleFail(DefaultPlugin):
        def handle_command(self, command):
            raise ValueError()

    class SyntaxErrorFail(DefaultPlugin):
        def handle_syntax_error(self, command, data):
            raise ValueError()

    class RuntimeErrorFail(DefaultPlugin):
        def handle_runtime_error(self, command, data):
            raise ValueError()

    class ResendFail(DefaultPlugin):
        def handle_resend(self, command):
            raise ValueError()

        def handle_syntax_error(self, command, data):
            command.command = "pass"
            command.resend_command = True

    class SuccessFail(DefaultPlugin):
        def command_success(self, command):
            raise ValueError()

    class FailFail(DefaultPlugin):
        def command_fail(self, command):
            raise ValueError()

    class EndInteractionFail(DefaultPlugin):
        def end_interaction(self, command):
            raise ValueError()

    calc = Calculator()
    calc.register_plugin(BeginInteractionFail())
    calc.command("pass")
    captured = capfd.readouterr()
    assert "BeginInteractionFail" in captured.out

    calc = Calculator()
    calc.register_plugin(ParseFail())
    calc.command("pass")
    captured = capfd.readouterr()
    assert "ParseFail" in captured.out

    calc = Calculator()
    calc.register_plugin(HandleFail())
    calc.command("pass")
    captured = capfd.readouterr()
    assert "HandleFail" in captured.out

    calc = Calculator()
    calc.register_plugin(SyntaxErrorFail())
    calc.command("is")
    captured = capfd.readouterr()
    assert "SyntaxErrorFail" in captured.out

    calc = Calculator()
    calc.register_plugin(RuntimeErrorFail())
    calc.command("raise ValueError()")
    captured = capfd.readouterr()
    assert "RuntimeErrorFail" in captured.out

    calc = Calculator()
    calc.register_plugin(ResendFail())
    calc.command("is")
    captured = capfd.readouterr()
    assert "ResendFail" in captured.out

    calc = Calculator()
    calc.register_plugin(SuccessFail())
    calc.command("pass")
    captured = capfd.readouterr()
    assert "SuccessFail" in captured.out

    calc = Calculator()
    calc.register_plugin(FailFail())
    calc.command("is")
    captured = capfd.readouterr()
    assert "FailFail" in captured.out

    calc = Calculator()
    calc.register_plugin(EndInteractionFail())
    calc.command("pass")
    captured = capfd.readouterr()
    assert "EndInteractionFail" in captured.out


def test_calc_notify_success():
    calc = Calculator()

    class Plugin(CalculatorPlugin):
        def __init__(self):
            super().__init__(random_str(), -1)
            self.count = 0

        def begin_interaction(self, command):
            assert self.count == 0
            self.count = 1

        def parse_command(self, command):
            assert self.count == 1
            self.count = 2

        def handle_command(self, command):
            assert self.count == 2
            self.count = 3

        def handle_runtime_error(self, command, data):
            assert False

        def handle_syntax_error(self, command, data):
            assert False

        def handle_syntax_error_obj(self, command, exc):
            assert False

        def handle_resend(self, command):
            assert False

        def command_success(self, command):
            assert self.count == 3
            self.count = 4

        def command_fail(self, command):
            assert False

        def end_interaction(self, command):
            assert self.count == 4
            self.count = 5

    plugin = Plugin()
    calc.register_plugin(plugin)
    calc.command("pass")
    assert plugin.count == 5


def test_calc_notify_priorities():
    calc = Calculator()
    global flag
    flag = False

    class PluginTrue(CalculatorPlugin):
        def __init__(self):
            super().__init__(random_str(), 20)

        def begin_interaction(self, command):
            global flag
            assert not flag
            flag = True

        def parse_command(self, command):
            global flag
            assert not flag
            flag = True

        def handle_command(self, command):
            global flag
            assert not flag
            flag = True

        def handle_runtime_error(self, command, data):
            global flag
            assert not flag
            flag = True

        def handle_syntax_error(self, command, data):
            global flag
            assert not flag
            flag = True

        def handle_resend(self, command):
            global flag
            assert not flag
            flag = True

        def command_success(self, command):
            global flag
            assert not flag
            flag = True

        def command_fail(self, command):
            assert False

        def end_interaction(self, command):
            global flag
            assert not flag
            flag = True

    class PluginFalse(CalculatorPlugin):
        def __init__(self):
            super().__init__(random_str(), 30)

        def begin_interaction(self, command):
            global flag
            assert flag
            flag = False

        def parse_command(self, command):
            global flag
            assert flag
            flag = False

        def handle_command(self, command):
            global flag
            assert flag
            flag = False

        def handle_runtime_error(self, command, data):
            global flag
            assert flag
            flag = False
            command.command = "pass"
            command.resend_command = True

        def handle_syntax_error(self, command, data):
            global flag
            assert flag
            flag = False
            command.command = "raise ValueError()"
            command.resend_command = True

        def handle_resend(self, command):
            global flag
            assert flag
            flag = False

        def command_success(self, command):
            global flag
            assert flag
            flag = False

        def command_fail(self, command):
            assert False

        def end_interaction(self, command):
            global flag
            assert flag
            flag = False

    pt = PluginTrue()
    pf = PluginFalse()
    calc.register_plugin(pf)
    calc.register_plugin(pt)
    calc.command("is")
    assert not flag


def test_calc_notify_abort():
    class AssertFalsePlugin(DefaultPlugin):
        def begin_interaction(self, command):
            assert False

        def parse_command(self, command):
            assert False

        def handle_command(self, command):
            assert False

        def handle_syntax_error(self, command, data):
            assert False

        def handle_runtime_error(self, command, data):
            assert False

        def handle_resend(self, command):
            assert False

        def handle_syntax_error(self, command, data):
            assert False

        def handle_syntax_error_obj(self, command, exc):
            assert False

        def command_success(self, command):
            assert False

        def command_fail(self, command):
            pass

        def end_interaction(self, command):
            pass

    class BeginInteractionAbort(AssertFalsePlugin):
        def begin_interaction(self, command):
            command.abort = True

    class ParseAbort(AssertFalsePlugin):
        def begin_interaction(self, command):
            pass

        def parse_command(self, command):
            command.abort = True

    class HandleAbort(AssertFalsePlugin):
        def begin_interaction(self, command):
            pass

        def parse_command(self, command):
            pass

        def handle_command(self, command):
            command.abort = True

    class SyntaxErrorAbort(AssertFalsePlugin):
        def begin_interaction(self, command):
            pass

        def parse_command(self, command):
            pass

        def handle_syntax_error(self, command, data):
            command.abort = True

        def handle_syntax_error_obj(self, command, exc):
            command.abort = True

    class RuntimeErrorAbort(AssertFalsePlugin):
        def begin_interaction(self, command):
            pass

        def parse_command(self, command):
            pass

        def handle_command(self, command):
            pass

        def handle_runtime_error(self, command, data):
            command.abort = True

    class ResendAbort(AssertFalsePlugin):
        def begin_interaction(self, command):
            pass

        def parse_command(self, command):
            pass

        def handle_command(self, command):
            pass

        def handle_resend(self, command):
            command.abort = True

        def handle_syntax_error(self, command, data):
            command.command = "pass"
            command.resend_command = True

        def handle_syntax_error_obj(self, command, exc):
            pass

    calc = Calculator()
    calc.register_plugin(BeginInteractionAbort())
    calc.command("pass")
    calc = Calculator()
    calc.register_plugin(HandleAbort())
    calc.command("pass")
    calc = Calculator()
    calc.register_plugin(ParseAbort())
    calc.command("pass")
    calc = Calculator()
    calc.register_plugin(SyntaxErrorAbort())
    calc.command("is")
    calc = Calculator()
    calc.register_plugin(RuntimeErrorAbort())
    calc.command("raise ValueError()")
    calc = Calculator()
    calc.register_plugin(ResendAbort())
    calc.command("is")


def test_calc_notify_resend():
    global flag
    flag = False

    class FailAssertFalsePlugin(DefaultPlugin):
        def command_fail(self, command):
            assert False

    class SyntaxErrorResend(FailAssertFalsePlugin):
        def handle_syntax_error(self, command, data):
            command.command = "pass"
            command.resend_command = True

        def command_success(self, command):
            global flag
            flag = True

    class RuntimeErrorResend(FailAssertFalsePlugin):
        def handle_runtime_error(self, command, data):
            command.command = "pass"
            command.resend_command = True

        def command_success(self, command):
            global flag
            flag = True

    calc = Calculator()
    calc.register_plugin(SyntaxErrorResend())
    assert not flag
    calc.command("is")
    assert flag

    flag = False

    calc = Calculator()
    calc.register_plugin(RuntimeErrorResend())
    assert not flag
    calc.command("raise ValueError()")
    assert flag


def test_calc_notify_order_syntax_error():
    calc = Calculator()

    class Plugin(CalculatorPlugin):
        def __init__(self):
            super().__init__(random_str(), -1)
            self.count = 0

        def begin_interaction(self, command):
            assert self.count == 0
            self.count = 1

        def parse_command(self, command):
            assert self.count == 1
            self.count = 2

        def handle_command(self, command):
            assert False

        def handle_runtime_error(self, command, data):
            assert False

        def handle_syntax_error(self, command, data):
            assert self.count == 3
            self.count = 4

        def handle_syntax_error_obj(self, command, exc):
            assert self.count == 2
            self.count = 3

        def handle_resend(self, command):
            assert False

        def command_success(self, command):
            assert False

        def command_fail(self, command):
            assert self.count == 4
            self.count = 5

        def end_interaction(self, command):
            assert self.count == 5
            self.count = 6

    plugin = Plugin()
    calc.register_plugin(plugin)
    calc.command("is")
    assert plugin.count == 6


def test_calc_notify_order_runtime_error():
    calc = Calculator()

    class Plugin(CalculatorPlugin):
        def __init__(self):
            super().__init__(random_str(), -1)
            self.count = 0

        def begin_interaction(self, command):
            assert self.count == 0
            self.count = 1

        def parse_command(self, command):
            assert self.count == 1
            self.count = 2

        def handle_command(self, command):
            assert self.count == 2
            self.count = 3

        def handle_runtime_error(self, command, data):
            assert self.count == 3
            self.count = 4

        def handle_syntax_error(self, command, data):
            assert False

        def handle_syntax_error_obj(self, command, exc):
            assert False

        def handle_resend(self, command):
            assert False

        def command_success(self, command):
            assert False

        def command_fail(self, command):
            assert self.count == 4
            self.count = 5

        def end_interaction(self, command):
            assert self.count == 5
            self.count = 6

    plugin = Plugin()
    calc.register_plugin(plugin)
    calc.command("raise ValueError()")
    assert plugin.count == 6


def test_calc_notify_order_syntax_error_resend():
    calc = Calculator()

    class Plugin(CalculatorPlugin):
        def __init__(self):
            super().__init__(random_str(), -1)
            self.count = 0

        def begin_interaction(self, command):
            assert self.count == 0
            self.count = 1

        def parse_command(self, command):
            assert self.count == 1
            self.count = 2

        def handle_command(self, command):
            assert self.count == 5
            self.count = 6

        def handle_runtime_error(self, command, data):
            assert False

        def handle_syntax_error(self, command, data):
            assert self.count == 3
            self.count = 4
            command.command = "pass"
            command.resend_command = True

        def handle_syntax_error_obj(self, command, exc):
            assert self.count == 2
            self.count = 3

        def handle_resend(self, command):
            assert self.count == 4
            self.count = 5

        def command_success(self, command):
            assert self.count == 6
            self.count = 7

        def command_fail(self, command):
            assert False

        def end_interaction(self, command):
            assert self.count == 7
            self.count = 8

    plugin = Plugin()
    calc.register_plugin(plugin)
    calc.command("is")
    assert plugin.count == 8


def test_calc_notify_order_runtime_error_resend():
    calc = Calculator()

    class Plugin(CalculatorPlugin):
        def __init__(self):
            super().__init__(random_str(), -1)
            self.count = 0

        def begin_interaction(self, command):
            assert self.count == 0
            self.count = 1

        def parse_command(self, command):
            assert self.count == 1
            self.count = 2

        def handle_command(self, command):
            assert self.count == 2
            self.count = 3

        def handle_runtime_error(self, command, data):
            assert self.count == 3
            self.count = 4
            command.command = "pass"
            command.resend_command = True

        def handle_syntax_error(self, command, data):
            assert False

        def handle_syntax_error_obj(self, command, exc):
            assert False

        def handle_resend(self, command):
            assert self.count == 4
            self.count = 5

        def command_success(self, command):
            assert self.count == 5
            self.count = 6

        def command_fail(self, command):
            assert False

        def end_interaction(self, command):
            assert self.count == 6
            self.count = 7

    plugin = Plugin()
    calc.register_plugin(plugin)
    calc.command("raise ValueError()")
    assert plugin.count == 7


def test_calc_chksym():
    calc = Calculator()

    name1 = random_str()
    name2 = random_str()

    assert not calc.chksym(name1)
    assert not calc.chksym(name2)

    calc.command(f"{name1} = 0")

    assert calc.chksym(name1)
    assert not calc.chksym(name2)

    calc.command(f"del {name1}")

    assert not calc.chksym(name1)
    assert not calc.chksym(name2)

    calc.command(f"{name2} = 0")

    assert not calc.chksym(name1)
    assert calc.chksym(name2)

    calc.command(f"del {name2}")

    assert not calc.chksym(name1)
    assert not calc.chksym(name2)

    calc.command(f"{name1} = {name2} = 0")

    assert calc.chksym(name1)
    assert calc.chksym(name2)

    assert not calc.chksym("_")


def test_calc_getsym():
    calc = Calculator()

    name = random_str()

    for i in range(5):
        value = random_str()
        calc.command(f"{name} = '{value}'")
        assert calc.getsym(name) == value

    assert calc.getsym("exec") is exec


def test_calc_mksym():
    calc = Calculator()

    for name in range(5):
        name = random_str()
        assert not calc.chksym(name)
        assert calc.mksym(name)
        assert calc.chksym(name)
        sym = calc.getsym(name)
        assert sym.name == name

    syms = [random_str() for i in range(5)]
    calc.mksym(syms)
    for name in syms:
        assert calc.chksym(name)
        sym = calc.getsym(name)
        assert sym.name == name


def test_calc_reset():
    calc = Calculator()
    assert not calc.command(f"def {random_str()}():")
    assert calc.incomplete_command is not None
    calc.reset()
    assert not calc.incomplete_command


def test_calc_command_empty():
    calc = Calculator()

    for name in [random_str() for i in range(5)]:
        calc.command(f"{name } = 0")

    original = {}
    original.update(calc.context.__dict__)

    calc.command("")

    new = {}
    new.update(calc.context.__dict__)

    assert original == new


def test_calc_command_multiline():
    calc = Calculator()
    name = random_str()
    a = random_str()

    assert not calc.command(f"def {name}(s):")
    assert not calc.command(f"  return s + '{a}'")
    assert calc.command("")

    t = random_str()
    assert t + a == calc.getsym(name)(t)
