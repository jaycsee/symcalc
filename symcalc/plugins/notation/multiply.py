# type: ignore
from __future__ import annotations

import ast
import code
import numbers
import re as regex

import sympy

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationMultiply(CalculatorPlugin):
    """Calculator plugin to allow for multiplication by juxtaposition with brackets or spaces

    .. code-block::

        Calculator >>> 2pi
        2⋅π
        Calculator >>> 2b(x+3)**2
           2        2
        2⋅b ⋅(x + 3)
        Calculator >>> 2 a b sin(x)cos(x)
        2⋅a⋅b⋅sin(x)⋅cos(x)
        Calculator >>> 2ab
        2⋅a⋅b

    .. note:: Be careful when juxtaposing function calls, denominators, or other Python syntax. It may produce unexpected parsing due to Python's evaluation precedence

        .. code-block::

            Calculator >>> 2x/y(x+1)
               2⋅x
            ─────────
            y⋅(x + 1)
            Calculator >>> 2x(y)**2
               2  2
            2⋅x ⋅y
    """

    class CheckResolutions(ast.NodeTransformer):
        """Checks all of the resolutions of the ast to see there are better resolutions then leaving them unknown"""

        def __init__(self, calc: Calculator):
            self.calc = calc
            self.ignored_types_not_last = set(
                [
                    type(sympy.Basic),
                    sympy.core.function.FunctionClass,
                    type(lambda x: x),
                    type(sympy.sympify),
                    type(type),
                    type(sympy),
                    sympy.printing.printer._PrintFunction,
                    type(ord),
                ]
            )

        def join_Mult(self, l: list[str]) -> ast.AST | None:
            r = ast.Name(id=l[0], ctx=ast.Load())
            for n in l[1:]:
                r = ast.BinOp(left=r, op=ast.Mult(), right=ast.Name(id=n, ctx=ast.Load()))
            return self.generic_visit(r)

        def visit_Name(self, node: ast.Name) -> ast.AST | None:
            if self.calc.chksym(node.id) or not isinstance(node.ctx, ast.Load):
                return self.generic_visit(node)
            resolved = self.resolve(node.id)
            if len(resolved) == 1:
                return self.generic_visit(node)
            return self.generic_visit(self.join_Mult(resolved))

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            f = node.func
            if not isinstance(f, ast.Name) or len(resolved := self.resolve(f.id)) == 1:
                return self.generic_visit(node)
            node.func = ast.Name(resolved[-1], ctx=ast.Load())
            newargs = []
            for n in node.args:
                newargs.append(self.visit(n))
            node.args = [x for x in newargs if x]
            return self.generic_visit(ast.BinOp(self.join_Mult(resolved[:-1]), ast.Mult(), node))

        def resolve(self, data: str) -> list[str]:
            if data.startswith("_"):
                return [data]
            original_data = data
            end = len(data)
            ret = []
            while end > 0:
                found = False
                for i in range(end):
                    if data[i:end] and self.calc.chksym(data[i:end]) or regex.match(r"^[a-zA-Z]+_?[0-9]+$", data[i:end]):
                        if (ret or end != len(data)) and self.calc.chksym(data[i:end]) and type(self.calc.getsym(data[i:end])) in self.ignored_types_not_last:
                            return [original_data]
                        if end != len(data):
                            ret.append(data[end:])
                        ret.append(data[i:end])
                        end = i
                        data = data[:i]
                        found = True
                if not found:
                    if end == 1:
                        ret.append(data)
                        break
                    end -= 1
            ret.reverse()
            return ret

    class CheckCalls(ast.NodeTransformer):
        """Checks the ast for using brackets to denote multiplication by juxtaposition"""

        def __init__(self, calc: Calculator):
            self.calc = calc

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            try:
                self.generic_visit(node)
                if len(node.args) == 1 and isinstance(eval(ast.unparse(node.func), self.calc.context.__dict__, self.calc.context.__dict__), numbers.Number | sympy.core.Expr):
                    return self.generic_visit(ast.BinOp(node.func, ast.Mult(), node.args[0]))
            except Exception:
                pass
            return self.generic_visit(node)

    class NotationMultiplyHelper(CalculatorPlugin):
        """Helper plugin for NotationMultiply"""

        def __init__(self, caller: NotationMultiply.CheckCalls):
            super().__init__(self.__class__.__name__, 24)
            self.caller = caller

        def handle_command(self, command: CalculatorCommand) -> None:
            """Check the ast for multiplication if two expressions are called"""
            if command.calc.settings["notation_multiply"] and command.calc.settings["notation_multiply_calls"]:
                command.command_ast = ast.fix_missing_locations(self.caller.visit(command.command_ast))

    def __init__(self):
        super().__init__(self.__class__.__name__, 21)
        self.check_resolutions = None

    def hook(self, calc: Calculator) -> None:
        # Register the helper and the toggles for this plugin
        self.register_toggle(calc, "nm", "notation_multiply", True)
        self.register_raw_toggle(calc, "nmn", "notation_multiply_numbers", True)
        self.register_raw_toggle(calc, "nmo", "notation_multiply_objects", True)
        self.register_raw_toggle(calc, "nmc", "notation_multiply_calls", True)
        self.check_resolutions = NotationMultiply.CheckResolutions(calc)
        self.check_calls = NotationMultiply.CheckCalls(calc)
        self.helper = NotationMultiply.NotationMultiplyHelper(self.check_calls)
        calc.register_plugin(self.helper)

    @CalculatorPlugin.if_external_enabled("notation_multiply", "notation_multiply_numbers")
    def handle_syntax_error_obj(self, command: CalculatorCommand, exc: SyntaxError) -> None:
        lines = command.command.split("\n")
        if regex.fullmatch(r"invalid (binary|octal|decimal|hexadecimal) literal", exc.msg) and lines[exc.lineno - 1][exc.offset - 1] != "_":
            lines[exc.lineno - 1] = lines[exc.lineno - 1][: exc.offset] + "*" + lines[exc.lineno - 1][exc.offset :]
            command.command = "\n".join(lines)
            command.resend_command = True
        elif exc.msg == "invalid imaginary literal" and lines[exc.lineno - 1][exc.offset - 1] != "_":
            print(lines[exc.lineno - 1][: exc.offset - 1], "*j", lines[exc.lineno - 1][exc.offset :])
            lines[exc.lineno - 1] = lines[exc.lineno - 1][: exc.offset - 1] + "j*" + lines[exc.lineno - 1][exc.offset :]
            command.command = "\n".join(lines)
            command.resend_command = True
        elif exc.msg == "invalid syntax":
            for i in range(exc.offset - 1):
                c = lines[exc.lineno - 1][:i] + "(" + lines[exc.lineno - 1][i:] + ")"
                t = lines[: exc.lineno - 1] + [c] + lines[exc.lineno :]
                try:
                    code.compile_command("\n".join(t))
                except SyntaxError as e:
                    if e.msg == "invalid syntax. Perhaps you forgot a comma?":
                        lines[exc.lineno - 1] = lines[exc.lineno - 1][: exc.offset - 1] + "*" + lines[exc.lineno - 1][exc.offset - 1 :]
                        command.command = "\n".join(lines)
                        command.resend_command = True
                        break
        elif exc.msg == "invalid syntax. Perhaps you forgot a comma?":
            pass

    @CalculatorPlugin.if_external_enabled("notation_multiply", "notation_multiply_objects")
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST to apply the substitution
        command.command_ast = ast.fix_missing_locations(self.check_resolutions.visit(command.command_ast))
