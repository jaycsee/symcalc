from __future__ import annotations

import code
import traceback
from collections import defaultdict
from typing import Any, NoReturn

from sympy import *


class Calculator:
    pass


from .command import CalculatorCommand
from .context import CalculatorContext
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
        if s in __builtins__.keys():
            return __builtins__[s]
        return self.context.__dict__[s]

    def chksym(self, s: str, strict: bool = False) -> bool:
        if s == "_":
            return False
        return s in self.context.__dict__.keys() or s in __builtins__.keys()

    def reset(self) -> None:
        """Throws away the buffer from previous commands"""
        self.console.resetbuffer()
        self.incomplete_command = None

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

        self.reset()

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
        init_printing(wrap_line=False)
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
                self.reset()
            except EOFError:
                break


# sin(x)cos(x)
# outputdecimal may time out
# nintegrate is still sad
