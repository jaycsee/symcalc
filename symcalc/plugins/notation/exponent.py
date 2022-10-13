from __future__ import annotations

import ast

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
            if isinstance(node.op, ast.BitXor):
                self.plugin.breaks.append((node.left.end_lineno, node.left.end_col_offset, node.left.end_lineno, node.left.end_col_offset + 1))  # type: ignore
            return self.generic_visit(node)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> str | None:
        # Find all the bit xors
        self.breaks: list[tuple[int, int, int, int]] = []
        self.checker.visit(command.command_ast)
        # Sort by line number and then column number
        lines = command.command.split("\n")
        max_line = max([len(l) for l in lines])
        self.breaks.sort(key=lambda x: x[0] * max_line + x[1])
        # Reconstruct the command
        c = ""
        last = (1, 0, 1, 0)
        for cur in self.breaks:
            left_end_lineno, left_end_col, *_ = cur
            if last[2] == left_end_lineno:
                c += (lines[left_end_lineno - 1][last[3] : left_end_col]) + "**"
            else:
                c += "\n".join([lines[last[2] - 1][last[3] :]] + lines[last[2] - 1 : left_end_lineno - 1] + [lines[left_end_lineno - 1][:left_end_col]])
            last = cur
        left_end_lineno = len(lines)
        left_end_col = len(lines[-1])
        if last[2] == left_end_lineno:
            c += lines[last[2] - 1][last[3] : left_end_col]
        else:
            c += "\n".join([lines[last[2] - 1][last[3] :]] + lines[last[2] - 1 : left_end_lineno - 1] + [lines[left_end_lineno - 1][:left_end_col]])
        command.command = c
