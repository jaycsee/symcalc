from __future__ import annotations

import ast
import copy

from symcalc.calc import Calculator
from symcalc.command import CalculatorCommand
from symcalc.plugin import CalculatorPlugin


class NotationSolve(CalculatorPlugin):
    """Calculator plugin to allow for natural input into the solve function

    .. code-block::

        Calculator >>> solve(x == 2)
        [2]
        Calculator >>> solve(a == b)
        [{a: b}]
        Calculator >>> solve(i == 4 and j == 6)
        {i: 4, j: 6}
        Calculator >>> solve(a == b and c == d and b == c and x==y==z==12)
        {a: d, b: d, c: d, x: 12, y: 12, z: 12}
        Calculator >>> solveset(sin(x)==1)
        ⎧        π │      ⎫
        ⎨2⋅n⋅π +  ─ │ n ∊ ℤ⎬
        ⎩        2 │      ⎭

    .. note::
        Unlike regular Python evaluation, a==f(x)==b will cause f to be evaluated twice, which may cause unintended side effects

    .. note::
        Only the boolean operator ``and`` is supported. All others may yield unexpected results

    """

    class EliminateOuterAnds(ast.NodeTransformer):
        """Eliminates the and operator from the first argument of the solve function"""

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            if isinstance(node.func, ast.Name) and node.func.id == "solve":
                args = node.args
                if args and isinstance(args[0], ast.BoolOp) and isinstance(args[0].op, ast.And):
                    node.args[0] = ast.List(elts=args[0].values, ctx=ast.Load())
            return self.generic_visit(node)

    class EliminateOpChaining(ast.NodeTransformer):
        """Eliminates operator chaining from the first argument of the solve function"""

        def __init__(self):
            self.checker = NotationSolve.EliminateOpChaining.CheckChains(self)
            self.found = False

        class CheckChains(ast.NodeTransformer):
            def __init__(self, eliminator: NotationSolve.EliminateOpChaining):
                self.eliminator = eliminator

            def visit_Compare(self, node: ast.Compare) -> ast.AST | None:
                if len(node.ops) > 1:
                    self.eliminator.found = True
                    boolop_values = []
                    left = node.left
                    for i, op in enumerate(node.ops):
                        boolop_values.append(ast.Compare(left=left, ops=[op], comparators=[node.comparators[i]]))
                        left = copy.deepcopy(node.comparators[i])
                    return ast.BoolOp(op=ast.And(), values=boolop_values)
                return self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            if isinstance(node.func, ast.Name) and node.func.id == "solve":
                args = node.args
                self.found = False
                if args and isinstance(args[0], ast.List):
                    args[0] = ast.fix_missing_locations(self.checker.visit(args[0]))
                elif args:
                    args[0] = ast.fix_missing_locations(self.checker.visit(args[0]))
                    if isinstance(args[0], ast.BoolOp):
                        node.args[0] = ast.List(elts=args[0].values, ctx=ast.Load())
            return self.generic_visit(node)

    class EliminateInnerAnds(ast.NodeTransformer):
        """Eliminates the and operator from the list elements of the first argument of the solve function"""

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            if isinstance(node.func, ast.Name) and node.func.id == "solve" and node.args and isinstance(node.args[0], ast.List):
                new_elts = []
                for elt in node.args[0].elts:
                    if isinstance(elt, ast.BoolOp):
                        if not isinstance(elt.op, ast.And):
                            raise ValueError("NotationSolve only supports the boolean operation 'and'")
                        new_elts.extend(elt.values)
                    else:
                        new_elts.append(elt)
                node.args[0].elts = new_elts
            return self.generic_visit(node)

    class EliminateEqualities(ast.NodeTransformer):
        """Transforms all equalities in the first argument of the solve and solveset function"""

        def __init__(self):
            self.checker = NotationSolve.EliminateEqualities.CheckCompares()

        class CheckCompares(ast.NodeTransformer):
            def visit_Compare(self, node: ast.Compare) -> ast.AST | None:
                if len(node.ops) == 1:
                    return ast.Call(
                        func=ast.Attribute(value=ast.Name(id="sympy", ctx=ast.Load()), attr="Eq", ctx=ast.Load()),
                        args=[node.left, node.comparators[0]],
                        keywords=[],
                    )
                return self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            if isinstance(node.func, ast.Name) and (node.func.id == "solve" or node.func.id == "solveset") and node.args:
                node.args[0] = ast.fix_missing_locations(self.checker.visit(node.args[0]))
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 80)

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "ns", "notation_solve", True)
        self.transform1 = NotationSolve.EliminateOuterAnds()
        self.transform2 = NotationSolve.EliminateOpChaining()
        self.transform3 = NotationSolve.EliminateInnerAnds()
        self.transform4 = NotationSolve.EliminateEqualities()

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> None:
        # Walk the AST to apply the substitutions
        new_ast = command.command_ast
        try:
            new_ast = ast.fix_missing_locations(self.transform1.visit(new_ast))
            new_ast = ast.fix_missing_locations(self.transform2.visit(new_ast))
            new_ast = ast.fix_missing_locations(self.transform3.visit(new_ast))
            new_ast = ast.fix_missing_locations(self.transform4.visit(new_ast))
        except ValueError as e:
            print(f"ERROR: {e}")
            command.abort = True
        command.command_ast = new_ast
