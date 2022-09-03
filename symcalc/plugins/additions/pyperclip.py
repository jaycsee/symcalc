from __future__ import annotations

import pyperclip

from ...calc import Calculator
from ...plugin import CalculatorPlugin


class AddPyperclip(CalculatorPlugin):
    """Calculator plugin to add Pyperclip to the calculator context

    .. code-block::

        Calculator >>> copy("Test")
        Calculator >>> paste()
        Test

    """

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.pyperclip = pyperclip  # type: ignore
        calc.context.copy = pyperclip.copy  # type: ignore
        calc.context.paste = pyperclip.paste  # type: ignore
