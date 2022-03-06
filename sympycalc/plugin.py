from __future__ import annotations
from abc import ABC

from .calculator import Calculator, CalculatorCommand


class CalculatorPlugin(ABC):
    """Plugins for the Calculator"""

    def __init__(self, name: str, priority: int) -> None:
        self.name = name
        self.priority = priority

    def hook(self, calc: Calculator) -> None:
        """Called by the calculator when the plugin is added."""
        pass

    def handle_command(self, command: CalculatorCommand) -> None:
        """Proxies the command sent to the calculator. The given command can be modified in place"""
        pass

    def handle_runtime_error(self, command: CalculatorCommand, data: str) -> None:
        """Handles the stderr output data printed by the given runtime error as a result of command"""
        pass

    def handle_syntax_error(self, command: CalculatorCommand, data: str) -> None:
        """Handles the stderr output data printed by the given syntax error as a result of command"""
        pass

    def handle_resend(self, command: CalculatorCommand) -> None:
        """Proxies a command to be resent to the calculator. The given command can be modified in place"""
        pass

    def command_success(self, command: CalculatorCommand) -> None:
        """Actions taken after a successful command"""
        pass

    def command_fail(self, command: CalculatorCommand) -> None:
        """Actions taken after a failed command"""
        pass
