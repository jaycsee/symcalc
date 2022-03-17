from __future__ import annotations
import ast
import symtable
from collections import defaultdict
from typing import NoReturn, Any
import sympy
from sympy import *
import code
import traceback
import re as regex


init_printing(wrap_line=False)


class CalculatorContext:
    """Contains all of the available methods and variables in a class. CalculatorContext.__dict__ works similarly to globals()"""

    def __init__(self) -> None:
        """Initializes the default calculator context"""
        self.__dict__["sympy"] = sympy
        self.__dict__.update(sympy.__dict__)
        self.plot_3d = plotting.plot3d


class CalculatorCommand:
    """Data for a single calculator command"""

    def __init__(self, calc: Calculator, command: str) -> None:
        self.calc = calc
        self._command = command
        self._command_ast = None
        self._command_symtable = None
        self._valid_syntax = False
        self.command_original = command
        self.multiline_command = False
        self.abort = False
        self.resend_command = False
        self.print_error = False
        self.success = False
        self.buffer = None

    @property
    def command(self) -> str:
        return self._command

    @command.setter
    def command(self, value: str) -> None:
        if self.valid_syntax and self._command != value:
            self._command_ast = ast.parse(value, filename="<input>", mode="single")
            self._command_symtable = symtable.symtable(value, filename="<input>", compile_type="single")
        self._command = value

    @property
    def valid_syntax(self) -> bool:
        return self._valid_syntax

    @valid_syntax.setter
    def valid_syntax(self, value: bool) -> None:
        self._valid_syntax = value
        if value:
            self._command_ast = ast.parse(self._command, filename="<input>", mode="single")
            self._command_symtable = symtable.symtable(self._command, filename="<input>", compile_type="single")

    @property
    def command_ast(self) -> ast.AST | None:
        if not self._valid_syntax:
            raise ValueError("Attempted to get the AST of a command without valid syntax")
        return self._command_ast

    @command_ast.setter
    def command_ast(self, value: ast.AST) -> None:
        self._valid_syntax = True
        self.command = ast.unparse(value)

    def ast_update(self) -> None:
        """Tells the command to update if the AST was modified in place"""
        self._command = ast.unparse(self._command_ast)

    @property
    def command_symtable(self) -> symtable.SymbolTable | None:
        return self._command_symtable

    def __str__(self) -> str:
        return self.command

    def __repr__(self) -> str:
        return f"CalculatorCommand({self.command})"


class Calculator:
    pass


from .plugin import CalculatorPlugin


class Calculator:
    """A calculator based on SymPy"""

    def __init__(self, context: CalculatorContext = None, command_prefix: str = "/"):
        """Initializes the calculator"""
        # Prepare the calculator context
        self.context = context if context is not None else CalculatorContext()
        # Settings
        self.command_prefix = command_prefix
        self.settings_toggle = {}  # type: dict[str, str]
        self.settings = {}  # type: dict[str, bool]
        self.context.settings = self.settings
        # Command storage
        self.current_command = None  # type: CalculatorCommand
        self.incomplete_command = None  # type: CalculatorCommand
        # Prepare the calculator interperter
        self.console = code.InteractiveConsole(self.context.__dict__)
        self.console.write = self.handle_error_output
        self.interpret("'SymPy Calculator'")
        # Strict Python mode
        self.strict_python = False
        # List of plugins
        self.plugin_priorities = defaultdict(list)
        self.plugins = []

    def handle_error_output(self, data) -> None:
        """Method for handling error output passed to the console interpreter. Given to plugins"""
        if self.strict_python:
            print(data, end="")
            return
        self.current_command.print_error = True
        self.current_command.success = False
        if data.split("\n")[-2].startswith("KeyboardInterrupt"):
            self.current_command.resend_command = False
            return
        self.notify_plugins_runtime_error(self.current_command, data)
        if self.current_command.abort or self.current_command.resend_command:
            return
        if self.current_command.print_error:
            print(data, end="")

    def register_plugin(self, plugin: CalculatorPlugin) -> Calculator:
        """Register the given plugin. Returns itself for chaining"""
        self.plugin_priorities[plugin.priority].append(plugin)
        plugin.hook(self)
        self.plugins = []  # type: list[CalculatorPlugin]
        keys = list(self.plugin_priorities.keys())
        keys.sort()
        for k in keys:
            self.plugins.extend(self.plugin_priorities[k])
        return self

    def notify_plugins_parse(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a command to be parsed"""
        for plugin in self.plugins:
            plugin.parse_command(command_data)
            if command_data.abort:
                self.notify_plugins_fail(command_data)
                return

    def notify_plugins_command(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a command to be processed"""
        for plugin in self.plugins:
            plugin.handle_command(command_data)
            if command_data.abort:
                self.notify_plugins_fail(command_data)
                return

    def notify_plugins_resend(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a resent command to be processed"""
        for plugin in self.plugins:
            plugin.handle_resend(command_data)
            if command_data.abort:
                self.notify_plugins_fail(command_data)
                return

    def notify_plugins_syntax_error(self, command_data: CalculatorCommand, data: str, exc: SyntaxError) -> None:
        """Notify all plugins of a syntax error"""
        for plugin in self.plugins:
            plugin.handle_syntax_error_obj(command_data, exc)
            plugin.handle_syntax_error(command_data, data)
            if command_data.abort:
                self.notify_plugins_fail(command_data)
                return
            if command_data.resend_command:
                return

    def notify_plugins_runtime_error(self, command_data: CalculatorCommand, data: str) -> None:
        """Notify all plugins of a runtime error"""
        for plugin in self.plugins:
            plugin.handle_runtime_error(command_data, data)
            if command_data.abort:
                self.notify_plugins_fail(command_data)
                return
            if command_data.resend_command:
                return

    def notify_plugins_success(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a successful command"""
        command_data.success = True
        for plugin in self.plugins:
            plugin.command_success(command_data)

    def notify_plugins_fail(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a failed command"""
        command_data.success = False
        for plugin in self.plugins:
            plugin.command_fail(command_data)

    def mksym(self, s: str, /, **kwargs) -> Symbol | tuple[Symbol]:
        """Makes symbol(s) in the calculator context"""
        syms = symbols(s, **kwargs)
        try:
            for name in syms:
                self.context.__dict__[str(name)] = name
        except TypeError:
            self.context.__dict__[s] = syms
        return syms

    def getsym(self, s: str) -> Any:
        return self.context.__dict__[s]

    def chksym(self, s: str) -> bool:
        if s == "_":
            return False
        return s in self.context.__dict__.keys() or s in __builtins__.keys()

    def command(self, command: str) -> bool:
        """Push a command to the calculator."""
        if self.incomplete_command is not None:
            try:
                self.incomplete_command.buffer.append(command)
                if code.compile_command("\n".join(self.incomplete_command.buffer)) is None:
                    return False
                self.interpret("\n".join(self.incomplete_command.buffer))
            except Exception as e:
                print("".join(traceback.format_exception(e)).strip() + "\n", end="")
            self.incomplete_command = None
            return True

        self.console.resetbuffer()

        if not command:
            return True
        command_data = CalculatorCommand(self, command)

        # Handle calculator commands
        if command_data.command == "\\\\" or command_data.command == (self.command_prefix + "py"):
            # Intercept the command and launch a strict Python mode, bypassing all plugins
            self.strict_python = True
            print()
            self.console.interact(banner="Strict Python mode. Use Ctrl-Z to exit", exitmsg="Exiting strict Python mode...")
            self.strict_python = False
            return True
        if command_data.command.startswith(self.command_prefix):
            if command_data.command in self.settings_toggle:
                self.settings[self.settings_toggle[command_data.command]] = not self.settings[self.settings_toggle[command_data.command]]
                return True
            print("Unknown command.")
            return True

        # Calculator input preprocessing
        self.current_command = command_data
        self.notify_plugins_parse(command_data)
        if command_data.abort:
            self.notify_plugins_fail(command_data)
            return True

        # Attempt to compile the code
        while True:
            command_data.resend_command = False
            command_data.success = True
            try:
                compiled = code.compile_command(command_data.command)
                if compiled is None:
                    command_data.multiline_command = True
                else:
                    command_data.multiline_command = False
                break
            except SyntaxError as e:
                # Handle any syntax errors
                self.current_command.print_error = True
                self.current_command.success = False
                data = "".join(traceback.format_exception(e)).strip() + "\n"
                self.notify_plugins_syntax_error(command_data, data, e)
                if command_data.resend_command:
                    self.notify_plugins_resend(command_data)
                    continue
                if self.current_command.print_error:
                    print(data, end="")
                self.notify_plugins_fail(command_data)
                return True

        # Execute the command
        if not command_data.multiline_command:
            # Single line calculator input
            # Create the ast and symbol table
            command_data.valid_syntax = True
            self.notify_plugins_command(command_data)
            if command_data.abort:
                self.notify_plugins_fail(command_data)
                return True
            # Execute the command
            command_data.success = True
            self.interpret(command_data.command)
            while command_data.resend_command:
                self.notify_plugins_resend(command_data)
                if command_data.abort:
                    command_data.success = False
                    break
                command_data.resend_command = False
                command_data.success = True
                self.interpret(command_data.command)
            # Notify success or failure
            if command_data.success:
                self.notify_plugins_success(command_data)
            else:
                self.notify_plugins_fail(command_data)
            self.incomplete_command = None
            return True
        else:
            # Treat as Python code
            self.incomplete_command = command_data
            self.incomplete_command.buffer = []
            if not command_data.command_original.startswith(self.command_prefix):
                self.incomplete_command.buffer.append(command_data.command_original)
            return False

    def interpret(self, line: str) -> None:
        """Interpret the given line as input. Should be valid Python"""
        self.console.push(line)

    def interact(self, prompt: str = "Calculator") -> NoReturn:
        """Start an interactive prompt with the calculator. Exits on EOF, in which case the program should clean up and exit"""
        while True:
            try:
                if self.command(command := input(prompt + " >>> ")):
                    continue
                print("Multi-line Python input")
                if not command.startswith(self.command_prefix):
                    print(f">>> {command}")
                while not self.command(input("... ")):
                    pass
            except KeyboardInterrupt:
                print()
            except EOFError:
                break


from .plugins_additions import *
from .plugins_functionality import *
from .plugins_meta import *
from .plugins_notation import *
from .plugins_output import *
from .plugins_reminders import *


def register_default_plugins(calculator: Calculator) -> Calculator:
    """Register the default plugins. Returns itself for chaining"""
    defaultplugins = [
        PerformanceMonitor,
        PrintCommand,
        AddCisFunction,
        AddExternalLinks,
        AddnIntegrate,
        AddNewtonsMethod,
        AddOriginVectors,
        NotationConstants,
        NotationExponent,
        AutoExact,
        NotationInterval,
        NotationMultiply,
        AutoSymbol,
        NotationVector,
        OutputDecimal,
        OutputStore,
        ReminderMathConstants,
        ReminderTwoLetterSymbol,
    ]
    for p in defaultplugins:
        calculator.register_plugin(p())
    return calculator


Calculator.register_default_plugins = register_default_plugins

# sin(x)cos(x)
# outputdecimal may time out
# nintegrate is still sad
