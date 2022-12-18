from __future__ import annotations

import ast
from collections import defaultdict

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationExponent(CalculatorPlugin):
    """Calculator plugin to change ``^`` to ``**``, the Python syntax for powers. This plugin must run early to ensure full functionality.

    .. code-block::

        Calculator >>> 3^3
        27
        Calculator >>> solve(x^2-4)
        [-2, 2]

    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 3)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "ne", "notation_exponent", True)
        self.checker = NotationExponent.CheckPows(self)

    class CheckPows(ast.NodeVisitor):
        """Checks the names of all the nodes in the ast to look for the target notation"""

        def __init__(self, plugin: NotationExponent):
            self.plugin = plugin

        def visit_BinOp(self, node: ast.BinOp):
            if isinstance(node.op, ast.BitXor) and node.left.end_lineno is not None and node.left.end_col_offset is not None:
                line = node.left.end_lineno
                start = node.left.end_col_offset
                for i in range(start, len(self.plugin.current_lines[line - 1])):
                    if self.plugin.current_lines[line - 1][i] == "^":
                        self.plugin.breaks[line - 1].add(i)
            return self.generic_visit(node)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> str | None:
        # Find all the bit xors
        self.breaks: defaultdict[int, set[int]] = defaultdict(set)
        self.current_lines = command.command.split("\n")
        self.checker.visit(command.command_ast)
        for k, v in self.breaks.items():
            v = list(v)
            v.sort()
            l = ""
            for i in range(len(self.current_lines[k]) - 1, -1, -1):
                if v and i == v[-1]:
                    v.pop()
                    l += "**"
                else:
                    l += self.current_lines[k][i]
            self.current_lines[k] = l[::-1]
        command.command = "\n".join(self.current_lines)
