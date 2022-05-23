from __future__ import annotations

import ast

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class AutoSymbol(CalculatorPlugin):
    """Calculator plugin to automatically assume that undefined variables are symbols

    .. code-block::

        Calculator >>> x
        New symbol: x
        x
        Calculator >>> x
        x
        Calculator >>> yz
        New symbol: yz
        yz

    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 24)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "as", "auto_symbol", True)
        self.register_raw_toggle(calc, "asc", "auto_symbol_char", False)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST and check for undefined symbols
        for n in ast.walk(command.command_ast):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and not command.calc.chksym(n.id) and not n.id.startswith("_"):
                if command.calc.settings["auto_symbol_char"]:
                    command.calc.mksym(",".join(list(n.id)))
                else:
                    print(f"New symbol: {n.id}")
                    command.calc.mksym(n.id)
