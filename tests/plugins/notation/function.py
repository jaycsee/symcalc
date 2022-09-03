from __future__ import annotations

import ast
import code
from typing import Any

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationFunction(CalculatorPlugin):
    """Calculator plugin to allow for natural function notation

    .. code-block::

        Calculator >>> f(x)=2x+2
        Calculator >>> print(g(x):=exp(x)+2*x+1)
        MathFunction((x) -> exp(x) + 2 * x + 1)
        Calculator >>> f(g(x))
                 x
        4⋅x + 2⋅ℯ  + 4
        Result stored in out[2]
        Calculator >>> diff(g)
         x
        ℯ  + 2

    .. note::
        The special variable ``_`` does not work with the function definitions.

    .. note::
        This syntax only works for top level variables. This will not parse functions for attributes.

    """

    class MathFunction:
        """A function representing a user-defined function using natural function notation."""

        def __init__(self, args: str, expr, expr_str, func) -> None:
            self.args = args
            self.expr = expr
            self.expr_str = expr_str
            self.func = func

        def _sympy_(self):
            return self.expr

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return self.func(*args, **kwargs)

        def __repr__(self) -> str:
            return f"MathFunction({self.args} -> {self.expr_str})"

    class CheckNames(ast.NodeTransformer):
        """Checks the names of all the nodes in the ast to look for references to the function tags"""

        def __init__(self, plugin: NotationFunction) -> None:
            self.plugin = plugin

        def visit_Assign(self, node: ast.Assign) -> ast.AST | None:
            index = None
            for i, name in enumerate(node.targets):
                if name.id in self.plugin.functions:
                    index = i
            if index is None:
                return self.generic_visit(node)
            stored = self.plugin.functions[name.id]
            node.targets[index] = ast.Name(id=stored[0], ctx=ast.Load())
            node.value = ast.Call(ast.Name(id="MathFunction", ctx=ast.Load()), [ast.Constant(f"({stored[1]})"), node.value, ast.Constant(ast.unparse(node.value)), ast.parse(f"lambda {stored[1]}:{ast.unparse(node.value)}")], [])
            return self.generic_visit(node)

        def visit_NamedExpr(self, node: ast.NamedExpr) -> ast.AST | None:
            if node.target.id not in self.plugin.functions:
                return self.generic_visit(node)
            stored = self.plugin.functions[node.target.id]
            node.target = ast.Name(id=stored[0], ctx=ast.Load())
            node.value = ast.Call(ast.Name(id="MathFunction", ctx=ast.Load()), [ast.Constant(f"({stored[1]})"), node.value, ast.Constant(ast.unparse(node.value)), ast.parse(f"lambda {stored[1]}:{ast.unparse(node.value)}")], [])
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 70)
        self.functions = {}

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "nf", "notation_function", True)
        self.checker = NotationFunction.CheckNames(self)
        calc.context.MathFunction = self.MathFunction

    @CalculatorPlugin.if_enabled
    def parse_command(self, command: CalculatorCommand) -> None:
        self.functions = {}

    @CalculatorPlugin.if_enabled
    def handle_syntax_error_obj(self, command: CalculatorCommand, exc: SyntaxError) -> None:
        lines = command.command.split("\n")
        # This function does not work with multiline commands within the function call
        if exc.msg.startswith("cannot assign to function call here.") or exc.msg == "cannot use assignment expressions with function call":
            placeholder = self.found_function(lines[exc.lineno - 1][exc.offset - 1 : exc.end_offset - 1])
            if placeholder is None:
                return
            lines[exc.lineno - 1] = lines[exc.lineno - 1][: exc.offset - 1] + placeholder + lines[exc.lineno - 1][exc.end_offset - 1 :]
            command.command = "\n".join(lines)
            command.resend_command = True
        if exc.msg == "invalid syntax" and lines[exc.lineno - 1][exc.offset - 1 : exc.end_offset - 1] == ":=":
            c = lines[exc.lineno - 1][: exc.offset - 1] + lines[exc.lineno - 1][exc.offset :]
            t = lines[: exc.lineno - 1] + [c] + lines[exc.lineno :]
            try:
                code.compile_command("\n".join(t))
            except SyntaxError as e:
                if e.msg == 'expression cannot contain assignment, perhaps you meant "=="?':
                    placeholder = self.found_function(c[e.offset - 1 : e.end_offset - 2])
                    if placeholder is None:
                        return
                    c = c[: e.offset - 1] + placeholder + ":=" + lines[exc.lineno - 1][exc.offset + 1 :]
                    command.command = "\n".join(lines[: exc.lineno - 1] + [c] + lines[exc.lineno :])
                    command.resend_command = True

    def found_function(self, call_str: str) -> str | None:
        placeholder = f"__func{len(self.functions) + 1}__"
        call = ast.parse(call_str, "interactive").body[0].value
        if not isinstance(call.func, ast.Name):
            return None
        for arg in call.args:
            if not isinstance(arg, ast.Name):
                return None
        self.functions[placeholder] = (call.func.id, ast.unparse(call.args))
        return placeholder

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST to apply the substitutions
        command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
