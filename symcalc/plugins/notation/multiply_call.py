from __future__ import annotations

import ast
import code
import inspect
import numbers
import re as regex
from collections import defaultdict

import sympy
import sympy.printing.printer

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class NotationMultiplyCall(CalculatorPlugin):
    """Calculator plugin to allow for multiplication by juxtaposition with brackets or spaces. Also intelligently infers whether spaces are an implicit single-variable function call or multiplication by juxtaposition.

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
        Calculator >>> sin x cos x + a b
        a⋅b + sin(x)⋅cos(x)

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

        def __init__(self, plugin: NotationMultiplyCall, calc: Calculator):
            self.plugin = plugin
            self.calc = calc

        def join_Mult(self, l: list[str]) -> ast.AST | None:
            r = ast.Name(id=l[0], ctx=ast.Load())
            for n in l[1:]:
                r = ast.BinOp(left=r, op=ast.Mult(), right=ast.Name(id=n, ctx=ast.Load()))
            return self.generic_visit(r)

        def visit_Name(self, node: ast.Name) -> ast.AST | None:
            if self.calc.chksym(node.id) or not isinstance(node.ctx, ast.Load):
                return self.generic_visit(node)
            resolved = self.plugin.resolve(node.id)
            if len(resolved) == 1:
                return self.generic_visit(node)
            r = self.join_Mult(resolved)
            if r is None:
                return r
            return self.generic_visit(r)

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            f = node.func
            if not isinstance(f, ast.Name) or len(resolved := self.plugin.resolve(f.id)) == 1:
                return self.generic_visit(node)
            node.func = ast.Name(resolved[-1], ctx=ast.Load())
            newargs = []
            for n in node.args:
                newargs.append(self.visit(n))
            node.args = [x for x in newargs if x]
            return self.generic_visit(ast.BinOp(self.join_Mult(resolved[:-1]), ast.Mult(), node))

    class RearrangeCalls(ast.NodeTransformer):
        """Rearrange left-associative chained calls to be nested calls of its one-variable arguments"""

        def __init__(self, plugin: NotationMultiplyCall, calc: Calculator):
            self.plugin = plugin
            self.calc = calc

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            new_node = None
            if len(node.args) == 1 and not node.keywords:
                if isinstance(node.func, ast.Call) and len(node.func.args) == 1 and not node.func.keywords and isinstance(node.func.args[0], ast.Name):
                    resolved = self.plugin.resolve(node.func.args[0].id)
                    f = self.calc.getsym(resolved[-1]) if self.calc.chksym(resolved[-1]) else None
                    fas = inspect.getfullargspec(f) if callable(f) else None
                    if isinstance(f, sympy.core.function.FunctionClass) or fas is not None and (len(fas.args) == 1 or (not fas.args and fas.varargs is not None)):
                        parent = node.func
                        child = node
                        child.func = node.func.args[0]
                        parent.args[0] = child
                        node = parent
                        new_node = self.visit(node)
            if new_node is None:
                new_node = self.generic_visit(node)
            return new_node

    class CheckCalls(ast.NodeTransformer):
        """Checks the ast for using brackets to denote multiplication by juxtaposition if the function is not normally callable"""

        def __init__(self, plugin: NotationMultiplyCall, calc: Calculator):
            self.plugin = plugin
            self.calc = calc

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            new_node = self.generic_visit(node)
            try:
                if isinstance(new_node, ast.Call) and len(new_node.args) == 1 and isinstance(eval(ast.unparse(new_node.func), self.calc.context.__dict__, self.calc.context.__dict__), numbers.Number | sympy.core.Expr):
                    return self.generic_visit(ast.BinOp(new_node.func, ast.Mult(), new_node.args[0]))
            except Exception:
                pass
            return new_node

    class NotationMultiplyHelper(CalculatorPlugin):
        """Helper plugin for NotationMultiply"""

        def __init__(self, caller: ast.NodeTransformer):
            super().__init__(self.__class__.__name__, 25)
            self.transformer = caller

        def handle_command(self, command: CalculatorCommand) -> None:
            """Check the ast for multiplication if two expressions are called"""
            command.command_ast = ast.fix_missing_locations(self.transformer.visit(command.command_ast))

    def __init__(self):
        super().__init__(self.__class__.__name__, 21)
        self.check_resolutions = None
        self.resolutions_ignored_types_not_last = set(
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

    def resolve(self, data: str) -> list[str]:
        data = data.strip()
        if data.startswith("_"):
            return [data]
        original_data = data
        end = len(data)
        ret = []
        while end > 0:
            found = False
            for i in range(end):
                if data[i:end] and self.calc.chksym(data[i:end]) or regex.match(r"^[a-zA-Z]+_?[0-9]+$", data[i:end]):
                    if (ret or end != len(data)) and self.calc.chksym(data[i:end]) and type(self.calc.getsym(data[i:end])) in self.resolutions_ignored_types_not_last:
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

    def hook(self, calc: Calculator) -> None:
        # Register the helper and the toggles for this plugin
        self.register_toggle(calc, "nm", "notation_multiply", True)
        self.calc = calc
        self.transform1 = NotationMultiplyCall.RearrangeCalls(self, calc)
        self.transform2 = NotationMultiplyCall.CheckResolutions(self, calc)
        self.transform3 = NotationMultiplyCall.CheckCalls(self, calc)
        self.helper = NotationMultiplyCall.NotationMultiplyHelper(self.transform3)  # priority 25
        calc.register_plugin(self.helper)

    def parse_command(self, command: CalculatorCommand) -> None:
        self.try_mult = True
        self.try_mult_prevent: defaultdict[int, set[int]] = defaultdict(set)

    @CalculatorPlugin.if_enabled
    def handle_syntax_error_obj(self, command: CalculatorCommand, exc: SyntaxError) -> None:
        if exc.lineno is None or exc.end_lineno is None or exc.offset is None or exc.end_offset is None:
            return
        lines = command.command.split("\n")
        if regex.fullmatch(r"invalid (binary|octal|decimal|hexadecimal) literal", exc.msg) and lines[exc.lineno - 1][exc.offset - 1] != "_":
            lines[exc.lineno - 1] = lines[exc.lineno - 1][: exc.offset] + "*" + lines[exc.lineno - 1][exc.offset :]
            command.command = "\n".join(lines)
            command.resend_command = True
        elif exc.msg == "invalid imaginary literal" and lines[exc.lineno - 1][exc.offset - 1] != "_":
            lines[exc.lineno - 1] = lines[exc.lineno - 1][: exc.offset - 1] + "j*" + lines[exc.lineno - 1][exc.offset :]
            command.command = "\n".join(lines)
            command.resend_command = True
        elif exc.msg == "invalid syntax":
            before = lines[exc.lineno - 1][: exc.offset - 1]
            problem = lines[exc.lineno - 1][exc.offset - 1 : exc.end_offset - 1]
            after = lines[exc.lineno - 1][exc.end_offset - 1 :]
            if self.try_mult:
                try:
                    use_brackets = False
                    self.try_mult = False
                    attempt = lines.copy()
                    attempt[exc.lineno - 1] = f"{before}*{problem}{after}"
                    attempt = "\n".join(attempt)
                    code.compile_command(attempt)
                    try:
                        resolved = self.resolve(before)
                        left = self.calc.getsym(resolved[-1]) if self.calc.chksym(resolved[-1]) else None
                        fas = inspect.getfullargspec(left) if callable(left) else None
                        if isinstance(left, sympy.core.function.FunctionClass) or (fas is not None and (len(fas.args) == 1 or (fas.args is not None and fas.varargs is not None))):
                            use_brackets = True
                    except Exception:
                        pass
                    if use_brackets:
                        raise SyntaxError()
                    command.command = attempt
                    command.resend_command = True
                    return
                except SyntaxError:
                    pass
            lines[exc.lineno - 1] = f"{before}({problem}){after}"
            try:
                code.compile_command("\n".join(lines))
            except SyntaxError as e:
                if e.lineno is None or e.offset is None or e.end_offset is None or (e.msg == exc.msg and problem == lines[e.lineno - 1][e.offset - 1 : e.end_offset - 1] and abs(exc.offset - e.offset) < 2):
                    return
            command.command = "\n".join(lines)
            command.resend_command = True
        elif exc.msg == "invalid syntax. Perhaps you forgot a comma?":
            before = lines[exc.lineno - 1][: exc.offset - 1]
            problem = lines[exc.lineno - 1][exc.offset - 1 : exc.end_offset - 1]
            after = lines[exc.lineno - 1][exc.end_offset - 1 :]
            try:
                code.compile_command(problem)
                return
            except SyntaxError as e:
                if e.offset is None or e.end_offset is None:
                    return
                use_brackets = False
                try:
                    resolved = self.resolve(problem[: e.offset - 1])
                    left = self.calc.getsym(resolved[-1]) if self.calc.chksym(resolved[-1]) else None
                    fas = inspect.getfullargspec(left) if callable(left) else None
                    if isinstance(left, sympy.core.function.FunctionClass) or (fas is not None and (len(fas.args) == 1 or (fas.args is not None and fas.varargs is not None))):
                        use_brackets = True
                except Exception:
                    pass
                if not use_brackets and exc.offset not in self.try_mult_prevent[exc.lineno - 1]:
                    try:
                        attempt = lines.copy()
                        attempt[exc.lineno - 1] = f"{before}{problem[: e.offset - 1]}*{problem[e.offset - 1:]}{after}"
                        attempt = "\n".join(attempt)
                        code.compile_command(attempt)
                        command.command = attempt
                        command.resend_command = True
                        return
                    except Exception:
                        self.try_mult_prevent[exc.lineno - 1].add(exc.offset)
                n = f"{problem[: e.offset - 1]}({problem[e.offset - 1 : e.end_offset - 1]}){problem[e.end_offset - 1 :]}"
            lines[exc.lineno - 1] = f"{before}{n}{after}"
            try:
                code.compile_command("\n".join(lines))
            except SyntaxError as e:
                if e.lineno is None or e.offset is None or e.end_offset is None or (e.msg == exc.msg and problem == lines[e.lineno - 1][e.offset - 1 : e.end_offset - 1] and abs(exc.offset - e.offset) < 2):
                    return
            command.command = "\n".join(lines)
            command.resend_command = True

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST to apply the substitution
        new_ast = command.command_ast
        new_ast = ast.fix_missing_locations(self.transform1.visit(new_ast))
        new_ast = ast.fix_missing_locations(self.transform2.visit(new_ast))
        command.command_ast = new_ast
