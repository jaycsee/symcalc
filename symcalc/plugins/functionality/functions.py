from __future__ import annotations

import ast
from typing import Any

import sympy

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class AutoFunction(CalculatorPlugin):
    """Calculator plugin to automatically assume that undefined function calls are undefined functions

    .. code-block::

        Calculator >>> f(x)
        New function: f
        f(x)
        Calculator >>> g(2)
        New function: g
        g(2)
        Calculator >>> h(a,b,c)
        New function: h
        h(a, b, c)

    """

    class CheckCalls(ast.NodeTransformer):
        """Checks the names of all the nodes in the ast to look for the undefined function calls"""

        def __init__(self, calc: Calculator):
            self.calc = calc

        def visit_Call(self, node: ast.Call) -> ast.AST | Any:
            if isinstance(node.func, ast.Name) and not self.calc.chksym(node.func.id):
                print(f"New function: {node.func.id}")
                setattr(self.calc.context, node.func.id, sympy.Function(node.func.id))
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 22)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "af", "auto_function", True)
        self.checker = AutoFunction.CheckCalls(calc)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST and check for undefined functions
        command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
