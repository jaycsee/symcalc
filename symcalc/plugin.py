from __future__ import annotations

from abc import ABC

from .calc import Calculator
from .command import CalculatorCommand


class CalculatorPlugin(ABC):
    """Plugins for the Calculator"""

    def __init__(self, name: str, priority: int):
        """Initializes the plugin

        Parameters
        ----------
        name : :class:`str`
            The name of the plugin
        priority : :class:`int`
            The priority of the plugin. Lower numbers designate that a plugin should be run before others
        """
        self.name = name
        self.priority = priority
        self.setting_name = None

    def hook(self, calc: Calculator) -> None:
        """Called by the calculator when the plugin is added

        Parameters
        ----------
        calc : :class:`Calculator`
            The calculator for which this plugin was registered
        """
        pass

    def begin_interaction(self, command: CalculatorCommand) -> None:
        """The beginning of a calculator interaction. The command may be complete, incomplete, or a multiline statement. No guarantees are made about the command. The object can be modified in place. The command may or may not be modified, split, or aborted before being parsed, handled, or executed.

        Paramters
        ---------
        command : :class:`CalculatorCommand`
            The command that begins the interaction
        """
        pass

    def parse_command(self, command: CalculatorCommand) -> None:
        """A command to be parsed by the plugin, meant to be overriden by subclasses. The given command may or may not be valid Python syntax, and the object can be modified in place.

        The given command may have mutliple statements, such as 1+2;3+4

        Parameters
        ----------
        command : :class:`CalculatorCommand`
            The command to be parsed
        """
        pass

    def handle_command(self, command: CalculatorCommand) -> None:
        """A command to be handled by the plugin, meant to be overriden by subclasses. The given command is guaranteed to be valid Python syntax, and the object can be modified in place.

        Parameters
        ----------
        command : :class:`CalculatorCommand`
            The command to be parsed
        """
        pass

    def handle_syntax_error_obj(self, command: CalculatorCommand, exc: SyntaxError) -> None:
        """The syntax error to be handled by the plugin, meant to be overriden by subclasses. The given command is guaranteed to be invalid Python syntax, and the object can be modified in place.

        The given command may have mutliple statements, such as 1+2;3+4

        Parameters
        ----------
        command : :class:`CalculatorCommand`
            The command which caused the syntax error
        exc : :class:`SyntaxError`
            The resulting syntax error
        """
        pass

    def handle_syntax_error(self, command: CalculatorCommand, data: str) -> None:
        """The syntax error stderr output to be handled by the plugin, meant to be overriden by subclasses. The given command is guaranteed to be invalid Python syntax, and the object can be modified in place.

        The given command may have mutliple statements, such as 1+2;3+4

        Parameters
        ----------
        command : :class:`CalculatorCommand`
            The command which caused the syntax error
        exc : :class:`SyntaxError`
            The stderr output from the resulting syntax error
        """
        pass

    def handle_runtime_error(self, command: CalculatorCommand, data: str) -> None:
        """The stderr output to be handled by the plugin, meant to be overriden by subclasses. The given command is guaranteed to be valid Python syntax, and the object can be modified in place.

        Parameters
        ----------
        command : :class:`CalculatorCommand`
            The command which caused the runtime error
        data : :class:`str`
            The stderr data
        """
        pass

    def handle_resend(self, command: CalculatorCommand) -> None:
        """Proxies a command to be resent to the calculator. This occurs after a runtime or syntax error. No guarantees are made about the validity of the syntax, and the given command can be modified in place"""
        pass

    def command_success(self, command: CalculatorCommand) -> None:
        """Notifies the plugin after a successful command.

        .. note:: The :class:`Calculator` will not respect :attr:`CalculatorCommand.abort`, or :attr:`CalculatorCommand.resend_command` after the plugins are notified.

        Parameters
        ----------
        command : :class:`CalculatorCommand`
            The command that was executed
        """
        pass

    def command_fail(self, command: CalculatorCommand) -> None:
        """Notifies the plugin after a failed command. This could be due to ``SIGINT``, an uncaught error, or other failing conditions

        Parameters
        ----------
        command : :class:`CalculatorCommand`
            The command that was executed
        """
        pass

    def end_interaction(self, command: CalculatorCommand) -> None:
        """The end of a calculator interaction. The command given is the fully parsed command, which is valid Python syntax but may not be the raw statement that was executed.

        Parameters
        ----------
        command : :class:`CalculatorCommand`
            The command that began the interaction
        """
        pass

    def register_toggle(self, calc: Calculator, toggle_name: str, setting_name: str, default: bool) -> None:
        """Called by the plugin to register a toggle for the plugin with the Calculator. Should be used with :attr:`CalculatorPlugin.if_enabled`. Should not be overridden by plugins

        Parameters
        ----------
        calc : :class:`Calculator`
            The calculator to register the toggle
        toggle_name : :class:`str`
            The name of the directive to register. Cannot be None
        setting_name : :class:`str`
            The name of the setting in the calculator to hold the toggle. Cannot be None

        Raises
        ------
        :class:`ValueError`
            If the toggle has already been registered or if toggle_name or setting_name is None
        """
        if self.setting_name is not None:
            raise ValueError("A toggle for the plugin has already been registered")
        self.setting_name = setting_name
        self.register_raw_toggle(calc, toggle_name, setting_name, default)

    def register_raw_toggle(self, calc: Calculator, toggle_name: str, setting_name: str, default: bool) -> None:
        """Called by the plugin to register a raw toggle for the plugin with the Calculator. Should not be overridden by plugins

        Parameters
        ----------
        calc : :class:`Calculator`
            The calculator to register the toggle
        toggle_name : :class:`str`
            The name of the directive to register. Cannot be None
        setting_name : :class:`str`
            The name of the setting in the calculator to hold the toggle. Cannot be None

        Raises
        ------
        :class:`ValueError`
            If the toggle has already been registered or if toggle_name or setting_name is None
        """
        if toggle_name is None:
            raise ValueError("toggle_name cannot be None")
        if setting_name is None:
            raise ValueError("setting_name cannot be None")

        def toggle(calc: Calculator, command: str) -> None:
            calc.settings[setting_name] = not calc.settings[setting_name]

        calc.register_directive(toggle_name, toggle)
        calc.settings[setting_name] = default

    @staticmethod
    def if_enabled(func):
        """A decorator to ensure that a function is only called when the plugin is enabled. Must have called :func:`CalculatorPlugin.register_toggle` first"""

        def wrapper(self, command, *args, **kwargs) -> None:
            if self.setting_name is None:
                raise ValueError("A toggle for the plugin has not been registered")
            if command.calc.settings[self.setting_name]:
                func(self, command, *args, **kwargs)

        return wrapper

    @staticmethod
    def if_external_enabled(*status):
        """A decorator factory to ensure that a function is only called when some external setting is enabled"""

        def decorator(func):
            def wrapper(self, command, *args, **kwargs) -> None:
                run = True
                for s in status:
                    run = run and command.calc.settings[s]
                if run:
                    func(self, command, *args, **kwargs)

            return wrapper

        return decorator
