from __future__ import annotations

import ast
import numbers
import re as regex

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class AutoExact(CalculatorPlugin):
    """Calculator plugin to convert numbers to their SymPy exact form. Supports the SymPy Notation for repeating decimals. This plugin must run early to ensure full functionality.

    .. code-block::

        Calculator >>> 1.2
        6/5
        Calculator >>> 324.12
        8103
        ────
         25
        Calculator >>> 0.[127]
        127
        ───
        999
        Calculator >>> 421.1[16]
        83381
        ─────
         198

    """

    class CheckNumbers(ast.NodeTransformer):
        """Checks the ast for constants to convert them to SymPy objects and subscripts to convert them to repeating decimals"""

        def __init__(self):
            self._current_command = None

        @property
        def current_command(self) -> CalculatorCommand:
            return self._current_command

        @current_command.setter
        def current_command(self, command: CalculatorCommand) -> None:
            self._current_command = command
            self.lines = command.command.split("\n")

        def visit_Constant(self, node: ast.Constant) -> ast.AST | None:
            # This function does not work with multiline commands within the function call
            if isinstance(node.value, numbers.Number):
                return ast.Call(ast.Name(id="sympify", ctx=ast.Load()), [ast.Constant(self.lines[node.lineno - 1][node.col_offset : node.end_col_offset])], [ast.keyword("rational", ast.Constant(True))])
            return self.generic_visit(node)

        def visit_Subscript(self, node: ast.Subscript) -> ast.AST | None:
            # This function does not work with multiline commands within the function call
            if isinstance(node.value, ast.Constant) and isinstance(node.slice, ast.Constant) and regex.match(r"^\d*\.\d*\[\d+\]$", t := self.lines[node.lineno - 1][node.col_offset : node.end_col_offset]):
                return ast.Call(ast.Name(id="sympify", ctx=ast.Load()), [ast.Constant(t)], [ast.keyword("rational", ast.Constant(True))])
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 5)
        self.checker = AutoExact.CheckNumbers()

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "ax", "auto_exact", True)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the tree to apply the substitution
        self.checker.current_command = command
        command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
