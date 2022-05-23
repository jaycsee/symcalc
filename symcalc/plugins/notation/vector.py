from __future__ import annotations

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationVector(CalculatorPlugin):
    """Calculator plugin to allow for shortened vector and matrix notation

    .. code-block::

        Calculator >>> v[1,2,3]
        ⎡1⎤
        ⎢ ⎥
        ⎢2⎥
        ⎢ ⎥
        ⎣3⎦
        Calculator >>> m[1,2,3\\4,5,6]
        ⎡1  2  3⎤
        ⎢       ⎥
        ⎣4  5  6⎦

    .. note:: The current implementation may collide with subscripting variables that end in ``v`` and produce unwanted behavior. Use the toggle ``/ni`` to opt-out
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 60)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "nv", "notation_vector", True)

    @CalculatorPlugin.if_enabled
    def parse_command(self, command: CalculatorCommand) -> None:
        # Apply each expansion character by character
        # Vector expansion
        while True:
            new_command = ""
            contents = ""
            count = -1
            state = None
            for i, c in enumerate(command.command):
                if not state and new_command and new_command[-1] == "v" and c == "[":
                    new_command = new_command[:-1]
                    state = True
                    count = 1
                elif state and (c == "[" or c == "]"):
                    count += 1 if c == "[" else -1
                    if count == 0:
                        new_command += f"Matrix([{contents.replace('&', ',')}])"
                        contents = ""
                        state = False
                    else:
                        contents += c
                elif not state:
                    new_command += c
                elif state:
                    contents += c
            if state is None:
                break
            command.command = new_command
        # Matrix expansion
        while True:
            new_command = ""
            contents = ""
            count = -1
            state = None
            for c in command.command:
                if not state and new_command and new_command[-1] == "m" and c == "[":
                    new_command = new_command[:-1]
                    state = True
                    count = 1
                elif state and (c == "[" or c == "]"):
                    count += 1 if c == "[" else -1
                    if count == 0:
                        contents = contents.replace("\\\\", "],[")
                        new_command += f"Matrix([[{contents.replace('&', ',').replace(',,', '],[')}]])"
                        contents = ""
                        state = False
                    else:
                        contents += c
                elif not state:
                    new_command += c
                elif state:
                    contents += c
            if state is None:
                break
            command.command = new_command

