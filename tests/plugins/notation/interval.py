from __future__ import annotations

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationInterval(CalculatorPlugin):
    """Calculator plugin to allow for shortened interval notation

    .. code-block::

        Calculator >>> i[0,oo[
        [0, ∞)
        Result stored in out[6]
        Calculator >>> i[-3,3]
        [-3, 3]

    .. note:: The current implementation may collide with subscripting variables that end in ``i`` and produce unwanted behavior. Use the toggle ``/ni`` to opt-out

    .. note:: This plugin only understands the french notation for open intervals. eg. ``i]-oo,oo[``
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 61)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "ni", "notation_interval", True)

    @CalculatorPlugin.if_enabled
    def parse_command(self, command: CalculatorCommand) -> None:
        # Apply the substitution if enabled
        # Interval expansion
        while True:
            new_command = ""
            contents = ""
            state = None
            left_open = False
            for i, c in enumerate(command.command):
                if not state and new_command and new_command[-1] == "i" and (c == "[" or c == "]"):
                    left_open = c == "]"
                    new_command = new_command[:-1]
                    state = True
                elif state and (c == "[" or c == "]"):
                    new_command += f"Interval({contents}, {left_open=}, right_open={c == '['})"
                    contents = ""
                    state = False
                elif not state:
                    new_command += c
                elif state:
                    contents += c
            if state is None:
                break
            command.command = new_command
