from __future__ import annotations
import ast
from typing import Any

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
        Calculator >>> m[[1,2,3],[4,5,6]]
        ⎡1  2  3⎤
        ⎢       ⎥
        ⎣4  5  6⎦

    """

    class CheckSubscripts(ast.NodeTransformer):
        """Checks the ast for subscripts to convert them to vector or matrix calls"""

        def __init__(self, calc: Calculator) -> None:
            self.calc = calc

        def visit_Subscript(self, node: ast.Subscript) -> ast.Subscript | Any:
            if not (isinstance(node.ctx, ast.Load) and isinstance(node.value, ast.Name) and (node.value.id == "v" or node.value.id == "m") and isinstance(node.slice, ast.Tuple | ast.List)) or self.calc.chksym(node.value.id):
                return self.generic_visit(node)
            if node.value.id == "m" and isinstance(node.slice, ast.List):
                node.slice = ast.Tuple([node.slice], ctx=ast.Load())
            return ast.Call(ast.Name(id="Matrix", ctx=ast.Load()), [ast.List(node.slice.elts, ctx=ast.Load())], [])

    def __init__(self):
        super().__init__(self.__class__.__name__, 20)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "nv", "notation_vector", True)
        self.checker = NotationVector.CheckSubscripts(calc)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST to apply the substitutions
        command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
