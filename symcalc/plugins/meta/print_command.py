from __future__ import annotations

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class PrintCommand(CalculatorPlugin):
    """Calculator plugin to print the resulting command after processing to stdout

    With the default plugin :class:`AutoExact` enabled:

    .. code-block::

        Calculator >>> /pc
        Calculator >>> 1.2
        Parsed Command: 1.2
        Handled Command: sympify('1.2', rational=True)
        6/5
        Calculator >>> 324.12
        Parsed Command: 324.12
        Handled Command: sympify('324.12', rational=True)
        8103
        ────
         25

    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 999)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "pc", "print_command", False)

    @CalculatorPlugin.if_enabled
    def parse_command(self, command: CalculatorCommand) -> None:
        # Print the command if the plugin is enabled
        print(f"Parsed Command: {command.command}")

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Print the command if the plugin is enabled
        print(f"Handled Command: {command.command}")

    @CalculatorPlugin.if_enabled
    def handle_resend(self, command: CalculatorCommand) -> None:
        # Print the command if the plugin is enabled
        print(f"Resent command: {command.command}")
