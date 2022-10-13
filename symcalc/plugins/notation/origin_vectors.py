from __future__ import annotations

import ast
import re

import sympy

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationOriginVectors(CalculatorPlugin):
    """Calculator plugin to add the origin vectors to the calculator context. o<n> is the origin vector in R^n

    .. code-block::

        Calculator >>> o3
        ⎡0⎤
        ⎢ ⎥
        ⎢0⎥
        ⎢ ⎥
        ⎣0⎦
    """

    class CheckNames(ast.NodeTransformer):
        """Checks the names of all the nodes in the ast to look for the undefined function calls"""

        def __init__(self, calc: Calculator):
            self.calc = calc

        def visit_Name(self, node: ast.Name) -> ast.AST | None:
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and not self.calc.chksym(node.id) and (match := re.match("^o([0-9]+)$", node.id)):
                n = int(match.groups()[0])
                self.calc.context.__dict__["o" + str(n)] = sympy.Matrix([0] * n)
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 22)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "nov", "notation_origin_vectors", True)
        self.checker = NotationOriginVectors.CheckNames(calc)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST and check for undefined symbols
        command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
