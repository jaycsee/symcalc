# type: ignore
from __future__ import annotations

import ast
from typing import Any

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationFunctionExponent(CalculatorPlugin):
    """Calculator plugin to allow for exponents on functions

    .. code-block::

        Calculator >>> sin**2(x)
           2
        sin (x)
        Result stored in out[1]
        Calculator >>> sin**2(x) == sin(x)**2
        True
        Calculator >>> (tan**2)(x)
           2
        tan (x)
        Calculator >>> cos**-1(x)
        acos(x)

    """

    class CheckPows(ast.NodeTransformer):
        """Checks the ast for subscripts to convert them to factorial calls"""

        def __init__(self, calc: Calculator) -> None:
            self.calc = calc

        def visit_BinOp(self, node: ast.BinOp) -> ast.AST | None:
            if isinstance(node.op, ast.Pow) and isinstance(node.left, ast.Name) and self.calc.chksym(node.left.id) and callable(self.calc.getsym(node.left.id)) and ((isinstance(node.right, ast.Call) and not (isinstance(node.right.func, ast.Name) and node.right.func.id == "sympify")) or (isinstance(node.right, ast.UnaryOp) and isinstance(node.right.operand, ast.Call))):
                # sin^2(x)
                base_func = node.left
                if isinstance(node.right, ast.Call):
                    exponent = node.right.func
                    base_call = node.right
                    base_call.func = base_func
                    node.left = base_call
                    node.right = self.generic_visit(exponent)
                else:
                    exponent = node.right
                    exponent_value = node.right.operand.func
                    base_call = node.right.operand
                    base_call.func = base_func
                    exponent.operand = exponent_value
                    if isinstance(exponent.op, ast.USub):
                        exponent.op = ast.UAdd()
                        base_call.func.id = "a" + base_call.func.id
                    node.left = base_call
                    node.right = self.generic_visit(exponent)
            return self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> ast.Call | Any:
            if isinstance(node.func, ast.BinOp) and isinstance(node.func.op, ast.Pow) and isinstance(node.func.left, ast.Name) and self.calc.chksym(node.func.left.id) and callable(self.calc.getsym(node.func.left.id)):
                # (sin^2)(x)
                base_func = node.func.left
                base_call = node
                exponent = node.func.right
                power = node.func
                base_call.func = self.generic_visit(base_func)
                power.left = self.generic_visit(base_call)
                power.right = self.generic_visit(exponent)
                return power
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 24)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "nfe", "notation_function_exponent", True)
        self.checker = NotationFunctionExponent.CheckPows(calc)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        pass
        # print(command.command)
        # Walk the AST to apply the substitutions
        # command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
