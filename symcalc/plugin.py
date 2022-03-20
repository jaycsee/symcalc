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

    def hook(self, calc: Calculator) -> None:
        """Called by the calculator when the plugin is added

        Parameters
        ----------
        calc : :class:`Calculator`
            The calculator for which this plugin was registered
        """
        pass

    def parse_command(self, command: CalculatorCommand) -> None:
        """A command to be parsed by the plugin, meant to be overriden by subclasses. The given command may or may not be valid Python syntax, and the object can be modified in place.

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
        """Proxies a command to be resent to the calculator. The given command can be modified in place"""
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
