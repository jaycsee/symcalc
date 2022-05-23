from __future__ import annotations

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationExponent(CalculatorPlugin):
    """Calculator plugin to change ``^`` to ``**``, the Python syntax for powers

    .. code-block::

        Calculator >>> /ne
        Calculator >>> 3^3
        27

    .. note:: This is a implemented as a simple string substitution, and will not differentiate between notation and the contents of a string. For this reason, this plugin is opt-in with the ``/ne`` toggle
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 30)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "ne", "notation_exponent", False)

    @CalculatorPlugin.if_enabled
    def parse_command(self, command: CalculatorCommand) -> None:
        # Apply the substitution if enabled
        command.command = command.command.replace("^", "**")
