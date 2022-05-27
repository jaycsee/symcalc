from __future__ import annotations

import ast
from typing import Any

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationFactorial(CalculatorPlugin):
    """Calculator plugin to allow for factorial notation

    .. code-block::

        Calculator >>> 6!
        720
        Calculator >>> 2.3!
        ⎛23⎞
        ⎜──⎟!
        ⎝10⎠
        Calculator >>> -5!
        -120

    .. note:: This plugin was designed with NotationMultiply dependency. Undesired errors may occur if NotationMultiply is disabled.
    """

    class CheckSubscripts(ast.NodeTransformer):
        """Checks the ast for subscripts to convert them to factorial calls"""

        def visit_Subscript(self, node: ast.Subscript) -> ast.Call | Any:
            if isinstance(node.ctx, ast.Load) and isinstance(node.slice, ast.Name) and node.slice.id == "__factorial__":
                return self.generic_visit(ast.Call(ast.Name(id="factorial", ctx=ast.Load()), [node.value], []))
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 20)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "na", "notation_factorial", True)
        self.checker = NotationFactorial.CheckSubscripts()

    @CalculatorPlugin.if_enabled
    def handle_syntax_error_obj(self, command: CalculatorCommand, exc: SyntaxError) -> None:
        # Find exclamation mark using syntax errors
        lines = command.command.split("\n")
        if exc.msg == "invalid syntax" and exc.offset + 1 == exc.end_offset and lines[exc.lineno - 1][exc.offset - 1] == "!" and exc.offset != 1:
            lines[exc.lineno - 1] = lines[exc.lineno - 1][: exc.offset - 1] + "[__factorial__] " + lines[exc.lineno - 1][exc.offset :]
            command.command = "\n".join(lines)
            command.resend_command = True

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST to apply the substitutions
        command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
