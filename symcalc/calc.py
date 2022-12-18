from __future__ import annotations

import code
import traceback
from collections import defaultdict
from typing import Any, Callable, NoReturn

import sympy


class Calculator:  # type: ignore
    pass


from .command import CalculatorCommand
from .context import CalculatorContext
from .plugin import CalculatorPlugin


class Calculator:
    """An interactive console containing plugins and the console"""

    def __init__(self, context: CalculatorContext | None = None, directive_prefix: str = "/"):
        """Initializes the calculator

        Parameters
        ----------
        context : :class:`CalculatorContext`
            The context that the calculator will use. If ``None``, a new context will be generated. Defaults to ``None``
        command_prefix : :class:`str`
            The prefix for commands to be interpreted as setting toggles. Defaults to ``"/"``
        """
        # Prepare the calculator context
        self.context = context if context is not None else CalculatorContext()
        # Settings
        self.directive_prefix = directive_prefix
        self.settings: dict[str, bool] = {}
        self.context.settings = self.settings
        # Command storage
        self.queued_commands: list[str] = []
        self.current_command = None
        self.incomplete_command = None
        # Prepare the calculator interperter
        self.console = code.InteractiveConsole(self.context.__dict__)
        self.console.write = self.handle_error_output
        # Strict Python mode
        self.strict_python = False
        # List of plugins and directives
        self.plugin_priorities = defaultdict(list)
        self.plugins = []
        self.directives: dict[str, Callable[[Calculator, str], None]] = {}

    def handle_error_output(self, data: str) -> None:
        """Method for handling stderr output written to the console interpreter. The data is generally passed to plugins.

        Parameters
        ----------
        data : :class:`str`
            The data written to stderr

        Returns
        -------
        None
        """
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
        """
        Register the given plugin

        Parameters
        ----------
        plugin : :class:`CalculatorPlugin`
            The plugin to register

        Returns
        -------
        :class:`Calculator`
            ``self`` for chaining
        """
        self.plugin_priorities[plugin.priority].append(plugin)
        plugin.hook(self)
        self.plugins: list[CalculatorPlugin] = []
        keys = list(self.plugin_priorities.keys())
        keys.sort()
        for k in keys:
            self.plugins.extend(self.plugin_priorities[k])
        return self

    def register_directive(self, name: str, callback: Callable[[Calculator, str], None]) -> None:
        """Register a directive

        Parameters
        ----------
        name : :class:`str`
            The text of the directive
        callback: :class:`func`
            The function to call when the directive is triggered

        Raises
        ------
        :class:`ValueError`
            If the name is already exists as a directive in the calculator
        """
        if name in self.directives:
            raise ValueError(f"{name} is already a directive in this calculator")
        self.directives[name] = callback

    def notify_plugins_begin_interaction(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of the beginning of an interaction

        Parameters
        ----------
        command_data : :class:`CalculatorCommand`
            The command which triggered this event
        """
        for plugin in self.plugins:
            try:
                plugin.begin_interaction(command_data)
                if command_data == "" or command_data.command is None:
                    print(f"Plugin {plugin.__class__.__name__} returned an invalid command after interaction initialization. Aborting.")
                    command_data.abort = True
            except AssertionError:
                raise
            except Exception:
                traceback.print_exc()
                print(f"Plugin {plugin.__class__.__name__} encountered a runtime exception during interaction initialization. Aborting command.")
                command_data.abort = True
            if command_data.abort:
                self.notify_plugins_fail(command_data)
                return

    def notify_plugins_parse(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a command to be parsed

        Parameters
        ----------
        command_data : :class:`CalculatorCommand`
            The command which triggered this event
        """
        for plugin in self.plugins:
            try:
                plugin.parse_command(command_data)
                if command_data == "" or command_data.command is None:
                    print(f"Plugin {plugin.__class__.__name__} returned an invalid command after parsing. Aborting.")
                    command_data.abort = True
            except AssertionError:
                raise
            except Exception:
                traceback.print_exc()
                print(f"Plugin {plugin.__class__.__name__} encountered a runtime exception during parsing. Aborting command.")
                command_data.abort = True
            if command_data.abort:
                return

    def notify_plugins_command(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a command to be processed

        Parameters
        ----------
        command_data : :class:`CalculatorCommand`
            The command which triggered this event
        """
        for plugin in self.plugins:
            try:
                plugin.handle_command(command_data)
                if command_data == "" or command_data.command is None or command_data.command_ast is None:
                    print(f"Plugin {plugin.__class__.__name__} returned an invalid command after processing. Aborting.")
                    command_data.abort = True
            except AssertionError:
                raise
            except Exception:
                traceback.print_exc()
                print(f"Plugin {plugin.__class__.__name__} encountered a runtime exception during processing. Aborting command.")
                command_data.abort = True
            if command_data.abort:
                return

    def notify_plugins_resend(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a resent command to be processed

        Parameters
        ----------
        command_data : :class:`CalculatorCommand`
            The command which triggered this event
        """
        for plugin in self.plugins:
            try:
                plugin.handle_resend(command_data)
                if command_data == "" or command_data.command is None:
                    print(f"Plugin {plugin.__class__.__name__} returned an invalid command after resend processing. Aborting.")
                    command_data.abort = True
            except AssertionError:
                raise
            except Exception:
                traceback.print_exc()
                print(f"Plugin {plugin.__class__.__name__} encountered a runtime exception during resend processing. Aborting command.")
                command_data.abort = True
            if command_data.abort:
                return

    def notify_plugins_syntax_error(self, command_data: CalculatorCommand, data: str, exc: SyntaxError) -> None:
        """Notify all plugins of a syntax error

        Parameters
        ----------
        command_data : :class:`CalculatorCommand`
            The command which triggered this event
        """
        for plugin in self.plugins:
            try:
                plugin.handle_syntax_error_obj(command_data, exc)
                plugin.handle_syntax_error(command_data, data)
                if command_data == "" or command_data.command is None:
                    print(f"Plugin {plugin.__class__.__name__} returned an invalid command after syntax error handling. Aborting.")
                    command_data.abort = True
            except AssertionError:
                raise
            except Exception:
                traceback.print_exc()
                print(f"Plugin {plugin.__class__.__name__} encountered a runtime exception during syntax error handling. Aborting command.")
                command_data.abort = True
            if command_data.abort:
                self.notify_plugins_fail(command_data)
                return
            if command_data.resend_command:
                return

    def notify_plugins_runtime_error(self, command_data: CalculatorCommand, data: str) -> None:
        """Notify all plugins of a runtime error

        Parameters
        ----------
        command_data : :class:`CalculatorCommand`
            The command which triggered this event
        """
        for plugin in self.plugins:
            try:
                plugin.handle_runtime_error(command_data, data)
                if command_data == "" or command_data.command is None or command_data.command_ast is None:
                    print(f"Plugin {plugin.__class__.__name__} returned an invalid command after runtime error handling. Aborting.")
                    command_data.abort = True
            except AssertionError:
                raise
            except Exception:
                traceback.print_exc()
                print(f"Plugin {plugin.__class__.__name__} encountered a runtime exception during runtime error handling. Aborting command.")
                command_data.abort = True
            if command_data.abort:
                self.notify_plugins_fail(command_data)
                return
            if command_data.resend_command:
                return

    def notify_plugins_success(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a successful command

        Parameters
        ----------
        command_data : :class:`CalculatorCommand`
            The command which triggered this event
        """
        command_data.success = True
        for plugin in self.plugins:
            try:
                plugin.command_success(command_data)
            except AssertionError:
                raise
            except Exception:
                traceback.print_exc()
                print(f"Plugin {plugin.__class__.__name__} encountered a runtime exception during success handling.")
                return

    def notify_plugins_fail(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of a failed command

        Parameters
        ----------
        command_data : :class:`CalculatorCommand`
            The command which triggered this event
        """
        command_data.success = False
        for plugin in self.plugins:
            try:
                plugin.command_fail(command_data)
            except AssertionError:
                raise
            except Exception:
                traceback.print_exc()
                print(f"Plugin {plugin.__class__.__name__} encountered a runtime exception during failure handling.")
                return

    def notify_plugins_end_interaction(self, command_data: CalculatorCommand) -> None:
        """Notify all plugins of the end of an interaction

        Parameters
        ----------
        command_data : :class:`CalculatorCommand`
            The command which triggered this event
        """
        for plugin in self.plugins:
            try:
                plugin.end_interaction(command_data)
            except AssertionError:
                raise
            except Exception:
                traceback.print_exc()
                print(f"Plugin {plugin.__class__.__name__} encountered a runtime exception during interaction conclusion.")
                return

    def mksym(self, s: str, /, **kwargs) -> sympy.Symbol | tuple[sympy.Symbol]:
        """Makes symbol(s) in the calculator context

        Parameters
        ----------
        s : :class:`str`
            Either a single word or a comma/space separated string containing multiple words. All words are created as a symbol in the :class:`CalculatorContext`

        Returns
        -------
        :class:`Symbol` | :class:`tuple[Symbol]`
            The symbol or list of symbols that were created
        """
        syms = sympy.symbols(s, **kwargs)
        try:
            for name in syms:
                self.context.__dict__[str(name)] = name
        except TypeError:
            self.context.__dict__[s] = syms
        return syms

    def getsym(self, s: str) -> Any:
        """Gets a variable in the calculator context

        Parameters
        ----------
        s : :class:`str`
            The variable to retrieve from the calculator context

        Raises
        ------
        :class:`KeyError`
            The given variable name was not found in the calculator context

        Returns
        -------
        Any
            The retrieved variable
        """
        if s in __builtins__.keys():
            return __builtins__[s]
        return self.context.__dict__[s]

    def chksym(self, s: str) -> bool:
        """Checks if a variable exists in the calculator context

        Parameters
        ----------
        s : :class:`str`
            The variable to check in the calculator context

        Returns
        -------
        :class:`bool`
            Whether the variable was found
        """
        if s == "_":
            return False
        return s in self.context.__dict__.keys() or s in __builtins__.keys()

    def reset(self) -> None:
        """Throws away the buffer from previous commands"""
        self.console.resetbuffer()
        self.current_command = None
        self.incomplete_command = None
        self.queued_commands = []

    def queue_command(self, command: str) -> None:
        """Queues a calculator command for later execution. Can be used by plugins to send another command. If no current command is being executed, this command runs immediately.

        Parameters
        ----------
        command_data: :class:`str`
            The command to queue

        .. warning:: If called from a plugin, this method must be invoked conditionally, otherwise an infinite loop will occur. Using the ``end_interaction`` hook to run once per user interaction is acceptable.
        """
        if self.current_command is None:
            self.command(command)
        self.queued_commands.append(command)

    def command(self, command: str) -> bool:
        """Push a command to the calculator.

        Parameters
        ----------
        command : :class:`str`
            The command to be pushed to the calculator

        Returns
        -------
        :class:`bool`
            ``False`` if more input is required to complete the command, ``True`` otherwise
        """
        if self.incomplete_command is not None:
            try:
                self.incomplete_command.buffer.append(command)
                if code.compile_command("\n".join(self.incomplete_command.buffer)) is None:
                    return False
                self.interpret("\n".join(self.incomplete_command.buffer))
            except AssertionError:
                raise
            except Exception as e:
                print("".join(traceback.format_exception(e)).strip() + "\n", end="")
            self.incomplete_command = None
            return True

        self.reset()
        command = command.strip()

        if not command:
            return True
        self.current_command = command_data = CalculatorCommand(self, command)
        self.notify_plugins_begin_interaction(command_data)
        if command_data.abort:
            self.notify_plugins_fail(command_data)
            self.notify_plugins_end_interaction(command_data)
            self.current_command = None
            return True

        # Handle calculator directives
        if command_data.command == "\\\\" or command_data.command == (self.directive_prefix + "py"):
            # Intercept the command and launch a strict Python mode, bypassing all plugins
            self.strict_python = True
            print()
            self.console.interact(banner="Strict Python mode. Use Ctrl-Z to exit", exitmsg="Exiting strict Python mode...")
            self.strict_python = False
            self.notify_plugins_end_interaction(command_data)
            self.current_command = None
            return True
        if command_data.command.startswith(self.directive_prefix):
            if (c := command_data.command.removeprefix(self.directive_prefix)) in self.directives:
                self.directives[c](self, command_data.command.removeprefix(self.directive_prefix + c).strip())
                self.notify_plugins_end_interaction(command_data)
                self.current_command = None
                return True
            print("Unknown command.")
            self.notify_plugins_end_interaction(command_data)
            self.current_command = None
            return True

        # Calculator input preprocessing
        self.current_command = command_data
        self.notify_plugins_parse(command_data)
        if command_data.abort:
            self.notify_plugins_fail(command_data)
            self.notify_plugins_end_interaction(command_data)
            self.current_command = None
            return True

        # Attempt to compile the code
        while True:
            command_data.resend_command = False
            command_data.success = False
            try:
                compiled = code.compile_command(command_data.command)
                if compiled is None:
                    command_data.multiline_command = True
                else:
                    command_data.multiline_command = False
                    command_data.valid_syntax = True
                break
            except SyntaxError as e:
                # Handle any syntax errors
                self.current_command.print_error = True
                self.current_command.success = False
                data = "".join(traceback.format_exception(e)).strip() + "\n"
                self.notify_plugins_syntax_error(command_data, data, e)
                if command_data.resend_command:
                    self.notify_plugins_resend(command_data)
                    if not command_data.abort:
                        continue
                if self.current_command.print_error:
                    print(data, end="")
                self.notify_plugins_fail(command_data)
                self.notify_plugins_end_interaction(command_data)
                self.current_command = None
                return True

        # Execute the command
        if not command_data.multiline_command:
            # TODO: Remake the command splitting
            try:
                commands = []
                o = command_data.command.split("\n")
                for n in command_data.command_ast.body:
                    c = [o[n.lineno - 1][n.col_offset : (n.end_col_offset if n.lineno == n.end_lineno else len(o[n.lineno - 1]))]]
                    for l in range(n.lineno, n.end_lineno - 1):
                        c.append(o[l])
                        print(l)
                    if n.lineno != n.end_lineno:
                        c.append(o[n.end_lineno - 1][: n.end_col_offset])
                    commands.append("\n".join(c))
                for c in commands:
                    cc = CalculatorCommand(self, c)
                    cc.valid_syntax = True
                    if not self.execute_command(cc):
                        break
                self.current_command = command_data
                self.notify_plugins_end_interaction(command_data)
                self.current_command = None
                return True
            except AttributeError:
                self.execute_command(c)
                self.current_command = command_data
                self.notify_plugins_end_interaction(command_data)
                self.current_command = None
                return True
        else:
            # Treat as Python code
            self.incomplete_command = CalculatorCommand(self, command)
            self.incomplete_command.buffer = []
            if not command.startswith(self.directive_prefix):
                self.incomplete_command.buffer.append(command)
            return False

    def execute_command(self, command_data: CalculatorCommand) -> bool:
        """Executes a calculator command from the command data object

        Parameters
        ----------
        command_data: :class:`CalculatorCommand`
            The command to execute

        Returns
        -------
        :class:`bool`
            Whether the command was successful
        """
        self.current_command = command_data
        self.notify_plugins_command(command_data)
        if command_data.abort:
            self.notify_plugins_fail(command_data)
            return False
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
        for qc in self.queued_commands:
            self.command(qc)
        self.incomplete_command = None
        self.current_command = None
        return command_data.success

    def interpret(self, line: str) -> None:
        """Interpret the given line as input

        Parameters
        ----------
        line : :class:`str`
            The line to push to the underlying :class:`code.InteractiveConsole`. Must be valid Python
        """
        self.console.push(line)

    def interact(self, prompt: str = "Calculator") -> NoReturn:
        """Start an interactive prompt with the calculator

        Parameters
        ----------
        prompt : :class:`str`
            The prefix to each line on each interaction. Defaults to ``"Calculator"``

        Returns
        -------
        :class:`NoReturn`
            Exits only on EOF, thus the program should not be expected to return. If it does, only cleanup and a swift exist should occur.
        """
        sympy.init_printing(wrap_line=False)
        while True:
            try:
                if self.command(command := input(prompt + " >>> ")):
                    continue
                print("Multi-line Python input")
                if not command.startswith(self.directive_prefix):
                    print(f">>> {command}")
                while not self.command(input("... ")):
                    pass
            except KeyboardInterrupt:
                print()
                self.reset()
            except EOFError:
                exit()
