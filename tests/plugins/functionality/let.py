from __future__ import annotations

import ast
import re as regex
from collections import defaultdict
from typing import Any

import sympy
from symcalc.calc import Calculator
from symcalc.command import CalculatorCommand
from symcalc.plugin import CalculatorPlugin


class LetStatements(CalculatorPlugin):
    """Calculator plugin to support let statements, allowing a variable to be a symbol but also having an equivalent value

    .. code-block::

        Calculator >>> let b = a
        Calculator >>> b
        b
        ----- which evaluates to:
        a
        Calculator >>> let c = a
        Calculator >>> let d = b*c
        Calculator >>> d^2
         2
        d
        ----- which evaluates to:
         4
        a
        Calculator >>> let a = 3
        Calculator >>> d^3
         3
        d
        ----- which evaluates to:
        729

    """

    class CheckNames(ast.NodeTransformer):
        """Checks the names of all the nodes in the ast to look for the undefined function calls"""

        def __init__(self, plugin: LetStatements):
            self.plugin = plugin

        def visit_Assign(self, node: ast.Assign) -> ast.AST | None:
            for t in node.targets:
                if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
                    self.plugin.letting_symbols.append(t)
            return self.generic_visit(node)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AST | None:
            if isinstance(node.target, ast.Name) and isinstance(node.target.ctx, ast.Store):
                self.plugin.letting_symbols.append(node.target)
            return self.generic_visit(node)

    def __init__(self):
        super().__init__(self.__class__.__name__, 900)
        self.let_symbols: dict[sympy.Symbol, Any] = {}
        self.letting = False
        self.letting_symbols: list[ast.Name] = []
        self.current_command_found_symbols = False
        self.last_result = None
        self.subs_occured = False
        self.subs_dict: dict[sympy.Symbol, Any] = {}

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "ls", "let_statements", True)
        self.calc = calc
        self.checker = LetStatements.CheckNames(self)
        setattr(calc.context, "let_check_symbols", self.let_check_symbols)

    @CalculatorPlugin.if_enabled
    def parse_command(self, command: CalculatorCommand) -> None:
        self.letting = bool(regex.fullmatch(r"^let\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=.*$", command.command))
        self.letting_symbols = []
        command.command = command.command.removeprefix("let ").lstrip()

    @CalculatorPlugin.if_enabled
    def command_success(self, command: CalculatorCommand) -> None:
        if self.letting:
            self.letting_symbols = []
            command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
            for sym in self.letting_symbols:
                value = command.calc.getsym(sym.id)
                self.let_symbols[command.calc.mksym(sym.id)] = value  # type: ignore
        if isinstance(command.command_ast, ast.Module | ast.Interactive) and isinstance(command.command_ast.body[-1], ast.Assign):
            self.last_result = None
        elif not self.letting:
            command.calc.interpret("try:\n\tlet_check_symbols(_)\nexcept NameError: pass\n")
            if self.current_command_found_symbols:
                try:
                    output = self.last_result
                    if isinstance(output, sympy.matrices.dense.MutableDenseMatrix) and output.shape[1] == 1:
                        output = list(output.values())
                    if isinstance(output, list):
                        lse = []
                        for o in output:
                            lse.append(o.subs(self.subs_dict))
                    else:
                        lse = sympy.simplify(self.last_result.subs(self.subs_dict))
                    setattr(command.calc.context, "__let_statement_eval", lse)
                    if not self.subs_occured:
                        self.subs_occured = True
                        print("----- which evaluates to:")
                        command.calc.queue_command("__let_statement_eval")
                except AttributeError:
                    pass

    def let_check_symbols(self, output) -> None:
        self.current_command_found_symbols = False
        if output == self.last_result or self.subs_occured:
            return
        let_symbols = set(self.let_symbols.keys())
        if isinstance(output, sympy.matrices.dense.MutableDenseMatrix) and output.shape[1] == 1:
            output = list(output.values())
        if isinstance(output, list):
            try:
                for o in output:
                    for s in o.free_symbols:
                        if isinstance(s, sympy.Symbol) and s in let_symbols:
                            if not isinstance(self.calc.getsym(s.name), sympy.Symbol):
                                del self.let_symbols[s]
                                let_symbols.discard(s)
                                continue
                            self.last_result = output
                            self.current_command_found_symbols = True
                            return
            except (NameError, AttributeError, TypeError):
                pass
            return
        try:
            for s in output.free_symbols:
                if isinstance(s, sympy.Symbol) and s in let_symbols:
                    if not isinstance(self.calc.getsym(s.name), sympy.Symbol):
                        del self.let_symbols[s]
                        let_symbols.discard(s)
                        continue
                    self.last_result = output
                    self.current_command_found_symbols = True
                    return
        except (NameError, AttributeError, TypeError):
            pass
        self.last_result = output

    def end_interaction(self, command: CalculatorCommand) -> None:
        if self.letting:
            # Update substitution table
            depends: defaultdict[sympy.Symbol, set[sympy.Symbol]] = defaultdict(set)
            update: defaultdict[sympy.Symbol, set[sympy.Symbol]] = defaultdict(set)
            present_symbols: set[sympy.Symbol] = set()
            substitutable: set[sympy.Symbol] = set()
            for s, v in self.let_symbols.items():
                if not isinstance(v, sympy.Basic):
                    substitutable.add(s)
                else:
                    fss: set[sympy.Symbol] = set()
                    for fs in v.free_symbols:
                        if isinstance(fs, sympy.Symbol):
                            fss.add(fs)
                    if not len(fss):
                        substitutable.add(s)
                    depends[s] = fss
                    for fs in fss:
                        present_symbols.add(fs)
                        update[fs].add(s)

            def explore(sym: sympy.Symbol):
                if sym not in substitutable:
                    return
                for u in update[sym]:
                    depends[u].discard(sym)
                    if not len(depends[u]):
                        substitutable.add(u)
                        explore(u)

            let_symbol_keys = set(self.let_symbols.keys())
            for s in present_symbols:
                if s not in let_symbol_keys:
                    substitutable.add(s)  # Symbol is atomic wrt let statements
            for s in substitutable.copy():
                explore(s)
            self.subs_dict = {}
            for s in substitutable:
                if s in let_symbol_keys:
                    self.subs_dict[s] = self.let_symbols[s]
            for s, e in self.subs_dict.items():
                if isinstance(e, sympy.Basic):
                    l = e
                    for i in range(10):
                        e = e.subs(self.subs_dict)
                        if l == e:
                            break
                    self.subs_dict[s] = e
        self.letting = False
        self.letting_symbols = []
        self.subs_occured = False
