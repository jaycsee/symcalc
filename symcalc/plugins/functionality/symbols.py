from __future__ import annotations

import ast
from typing import Any

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

    class CheckNames(ast.NodeTransformer):
        """Checks the names of all the nodes in the ast to look for the undefined function calls"""

        def __init__(self, calc: Calculator):
            self.calc = calc

        def visit_Name(self, node: ast.Name) -> ast.Name | None:
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and not self.calc.chksym(node.id) and not node.id.startswith("_"):
                if self.calc.settings["auto_symbol_char"]:
                    self.calc.mksym(",".join(list(node.id)))
                else:
                    print(f"New symbol: {node.id}")
                    self.calc.mksym(node.id)
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 23)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "as", "auto_symbol", True)
        self.register_raw_toggle(calc, "asc", "auto_symbol_char", False)
        self.checker = AutoSymbol.CheckNames(calc)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST and check for undefined symbols
        command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
