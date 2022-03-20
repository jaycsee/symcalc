from __future__ import annotations

import ast
import numbers
from typing import Any

from sympy import *

from ..calc import Calculator
from ..command import CalculatorCommand
from ..plugin import CalculatorPlugin


class AutoExact(CalculatorPlugin):
    """Calculator plugin to convert numbers to their SymPy exact form

    .. code-block::

        Calculator >>> 1.2
        6/5
        Calculator >>> 324.12
        8103
        ────
         25

    """

    class CheckConstants(ast.NodeTransformer):
        """Checks the ast for constants and automatically converts them to sympy objects"""

        def __init__(self):
            self._current_command = None

        @property
        def current_command(self) -> CalculatorCommand:
            return self._current_command

        @current_command.setter
        def current_command(self, command: CalculatorCommand) -> None:
            self._current_command = command
            self.lines = command.command.split("\n")

        def visit_Constant(self, node: ast.Constant) -> Any:
            if isinstance(node.value, numbers.Number):
                return ast.Call(ast.Name(id="sympify", ctx=ast.Load()), [ast.Constant(self.lines[node.lineno - 1][node.col_offset : node.end_col_offset])], [ast.keyword("rational", ast.Constant(True))])
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 40)
        self.settings_name = "auto_exact"
        self.settings_toggle = "ax"
        self.checker = AutoExact.CheckConstants()

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name

    def handle_command(self, command: CalculatorCommand) -> None:
        """Walk the tree to apply the substitution"""
        if not command.calc.settings[self.settings_name]:
            return
        self.checker.current_command = command
        command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))


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
        super().__init__(self.__class__.__name__, 21)
        self.settings_name = "auto_symbol"
        self.settings_toggle = "as"

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings[self.settings_name + "_char"] = False
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.settings_toggle[calc.command_prefix + self.settings_toggle + "c"] = self.settings_name + "_char"

    def handle_command(self, command: CalculatorCommand) -> None:
        if not command.calc.settings[self.settings_name]:
            return
        # Walk the AST and check for undefined symbols
        for n in ast.walk(command.command_ast):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and not command.calc.chksym(n.id) and not n.id.startswith("_"):
                if command.calc.settings[self.settings_name + "_char"]:
                    command.calc.mksym(",".join(list(n.id)))
                else:
                    print(f"New symbol: {n.id}")
                    command.calc.mksym(n.id)
