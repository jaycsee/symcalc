from __future__ import annotations

import ast
import code
import numbers
import re as regex
from typing import Any

import sympy
from sympy import *

from ..calc import Calculator
from ..command import CalculatorCommand
from ..context import CalculatorContext
from ..plugin import CalculatorPlugin


class NotationConstants(CalculatorPlugin):
    """Calculator plugin to expand ``_x`` to ``constants['x']``, where the dictionary contains common physical constants

    .. code-block::

        Calculator >>> _c # Speed of light
        299792458
        Calculator >>> _g # Earth's gravity
        9.80665000000000
        Calculator >>> _Na # Avogadro's constant
        6.02214076000000e-23

    """

    class CheckNames(ast.NodeTransformer):
        """Checks the names of all the nodes in the ast to look for the target notation"""

        def __init__(self, context: CalculatorContext, table: dict[str, Any]):
            self.context = context
            self.table = table

        def visit_Name(self, node: ast.Name) -> ast.AST | None:
            if regex.match(r"_[a-zA-Z]\w*", node.id) and node.id[1:] in self.table:
                return ast.Subscript(value=ast.Name(id="constants", ctx=ast.Load()), slice=ast.Constant(value=node.id[1:]), ctx=ast.Load())
            return self.generic_visit(node)

    def __init__(self, table: dict[str, Any] = None):
        """Initializes the plugin with the lookup table

        Parameters
        ----------
        table : :class:`dict[str, Any]`
            The lookup table to use. Defaults to physical constants
        """
        super().__init__(self.__class__.__name__, 50)
        self.settings_name = "notation_constants"
        self.settings_toggle = "nc"
        self.table = (
            table
            if table is not None
            else {
                "c": sympify("299792458"),  # Speed of light
                "h": sympify("6.62607015") * 10 ** -34,  # Planck's constant
                "G": sympify("6.6743015") * 10 ** -11,  # Newtonian constant of gravitation
                "g": sympify("9.80665"),  # Earth's gravity
                "epsilon0": sympify("8.854187812813") * 10 ** -12,  # Vacuum electric permittivity
                "mu0": sympify("1.2566370621219") * 10 ** -6,  # Vacuum magnetic permittivity
                "e": sympify("1.602176634") * 10 ** -19,  # Elementary charge
                "Na": sympify("6.02214076") * 10 ** -23,  # Avogadro's constant
                "ke": sympify("8.987551792314") * 10 ** 9,  # Coulomb constant
                "mp": sympify("1.6726219236951") * 10 ** -27,  # Proton mass
                "mn": sympify("1.6749274980495") * 10 ** -27,  # Neutron mass
                "me": sympify("9.109383701528") * 10 ** -31,  # Electron mass
                "R": sympify("8.31446261815324"),  # Ideal gas constant
                "k": sympify("1.380649") * 10 ** -23,  # Boltzmann constant
                "a0": sympify("5.2917721090380") * 10 ** -11,  # Bohr radius
                "phi": (sympify("1") + sqrt(5)) / sympify("2"),  # Golden ratio
            }
        )
        self.checker = None  # type: NotationConstants.CheckNames

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.context.constants = self.table
        self.checker = NotationConstants.CheckNames(calc.context, self.table)

    def handle_command(self, command: CalculatorCommand) -> str | None:
        """Applies the substitution"""
        if command.calc.settings[self.settings_name]:
            command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))


class NotationExponent(CalculatorPlugin):
    """Calculator plugin to change ``^`` to ``**``, the Python syntax for powers

    .. code-block::

        Calculator >>> /ne
        Calculator >>> 3^3
        27

    .. note:: This is a implemented as a simple string substitution, and will not differentiate between notation and the contents of a string. For this reason, this plugin is opt-in with the ``/ne`` toggle
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 30)
        self.settings_name = "notation_exponent"
        self.settings_toggle = "ne"

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = False
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name

    def parse_command(self, command: CalculatorCommand) -> None:
        """Apply a simple substitution"""
        if not command.calc.settings[self.settings_name]:
            return
        command.command = command.command.replace("^", "**")


class NotationInterval(CalculatorPlugin):
    """Calculator plugin to allow for shortened interval notation

    .. code-block::

        Calculator >>> i[0,oo[
        [0, ∞)
        Result stored in out[6]
        Calculator >>> i[-3,3]
        [-3, 3]

    .. note:: The current implementation may collide with subscripting variables that end in ``i`` and produce unwanted behavior. Use the toggle ``/ni`` to opt-out

    .. note:: This plugin only understands the french notation for open intervals. eg. ``i]-oo,oo[``
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 61)
        self.settings_name = "notation_interval"
        self.settings_toggle = "ni"

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name

    def parse_command(self, command: CalculatorCommand) -> None:
        """Applies the interval expansion"""
        # Interval expansion
        while True:
            new_command = ""
            contents = ""
            state = None
            left_open = False
            for i, c in enumerate(command.command):
                if not state and new_command and new_command[-1] == "i" and (c == "[" or c == "]"):
                    left_open = c == "]"
                    new_command = new_command[:-1]
                    state = True
                elif state and (c == "[" or c == "]"):
                    new_command += f"Interval({contents}, {left_open=}, right_open={c == '['})"
                    contents = ""
                    state = False
                elif not state:
                    new_command += c
                elif state:
                    contents += c
            if state is None:
                break
            command.command = new_command


class NotationMultiply(CalculatorPlugin):
    """Calculator plugin to allow for multiplication by juxtaposition

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

    .. note:: Be careful with juxtaposing with variable denominators. It may produce unexpected parsing due to Python's call precedence

        .. code-block::

            Calculator >>> 2x/y(x+1)
               2⋅x
            ─────────
            y⋅(x + 1)
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
                    type(sympify),
                    type(type),
                    type(sympy),
                    sympy.printing.printer._PrintFunction,
                    type(ord),
                ]
            )

        def visit_Name(self, node: ast.Name) -> ast.AST | None:
            if self.calc.chksym(node.id) or not isinstance(node.ctx, ast.Load):
                return node
            resolved = self.resolve(node.id)
            if len(resolved) == 1:
                return self.generic_visit(node)
            return ast.parse("*".join(resolved), filename="<NotationMultiply>", mode="eval").body

        def visit_Call(self, node: ast.Call) -> ast.AST | None:
            f = node.func
            if type(f) == ast.Name:
                resolved = self.resolve(f.id)
                if len(resolved) == 1:
                    return self.generic_visit(node)
                node.func = ast.Name(resolved[-1], ctx=ast.Load())
                newargs = []
                for n in node.args:
                    newargs.append(self.visit(n))
                node.args = [x for x in newargs if x]
                return ast.BinOp(ast.parse("*".join(resolved[:-1]), filename="<NotationMultiply>", mode="eval").body, ast.Mult(), node)
            return self.generic_visit(node)

        def resolve(self, data: str) -> list[str]:
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
                if len(node.args) == 1 and isinstance(eval(ast.unparse(node.func), self.calc.context.__dict__, self.calc.context.__dict__), (numbers.Number, sympy.core.Expr)):
                    return ast.BinOp(node.func, ast.Mult(), node.args[0])
            except Exception:
                pass
            return node

    class NotationMultiplyHelper(CalculatorPlugin):
        """Helper plugin for NotationMultiply"""

        def __init__(self, settings_name: str, caller: NotationMultiply.CheckCalls):
            super().__init__(self.__class__.__name__, 22)
            self.settings_name = settings_name
            self.caller = caller

        def handle_command(self, command: CalculatorCommand) -> None:
            """Check the ast for multiplication if two expressions are called"""
            if command.calc.settings[self.settings_name] and command.calc.settings[self.settings_name + "_calls"]:
                command.command_ast = ast.fix_missing_locations(self.caller.visit(command.command_ast))

    def __init__(self):
        super().__init__(self.__class__.__name__, 20)
        self.settings_name = "notation_multiply"
        self.settings_toggle = "nm"
        self.resolver = None  # type: NotationMultiply.CheckResolutions

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.settings[self.settings_name + "_numbers"] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle + "n"] = self.settings_name + "_numbers"
        calc.settings[self.settings_name + "_objects"] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle + "o"] = self.settings_name + "_objects"
        calc.settings[self.settings_name + "_calls"] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle + "c"] = self.settings_name + "_calls"
        self.resolver = NotationMultiply.CheckResolutions(calc)
        self.caller = NotationMultiply.CheckCalls(calc)
        self.helper = NotationMultiply.NotationMultiplyHelper(self.settings_name, self.caller)
        calc.register_plugin(self.helper)

    def handle_syntax_error_obj(self, command: CalculatorCommand, exc: SyntaxError) -> None:
        if not command.calc.settings[self.settings_name]:
            return
        lines = command.command.split("\n")
        if regex.fullmatch(r"invalid (binary|octal|decimal|hexadecimal) literal", exc.msg) and lines[exc.lineno - 1][exc.offset - 1] != "_":
            command.command = lines[exc.lineno - 1][: exc.offset] + "*" + lines[exc.lineno - 1][exc.offset :]
            command.resend_command = True
        elif regex.fullmatch(r"invalid imaginary literal", exc.msg) and lines[exc.lineno - 1][exc.offset - 1] != "_":
            if regex.match(r"^j(?!\w)", lines[exc.lineno - 1][exc.offset :]):
                command.command = lines[exc.lineno - 1][: exc.offset] + "*" + lines[exc.lineno - 1][exc.offset :]
            else:
                command.command = lines[exc.lineno - 1][: exc.offset - 1] + "*j" + lines[exc.lineno - 1][exc.offset :]
            command.resend_command = True
        elif exc.msg == "invalid syntax. Perhaps you forgot a comma?":
            original = lines[exc.lineno - 1][exc.offset - 1 : exc.end_offset - 1]
            first = ""
            for i, c in enumerate(original):
                first += c
                try:
                    code.compile_command(first)
                except SyntaxError as e:
                    if e.msg == "invalid syntax. Perhaps you forgot a comma?" and (i != len(original) - 1 or regex.match(r"\w", c)):
                        n = lines
                        n[exc.lineno - 1] = n[exc.lineno - 1][: exc.offset - 1] + original[:i] + "*" + original[i:] + n[exc.lineno - 1][exc.end_offset - 1 :]
                        command.command = "\n".join(n)
                        command.resend_command = True
                        break

    def handle_command(self, command: CalculatorCommand) -> None:
        """Check the ast to see if there are better resolutions"""
        if command.calc.settings[self.settings_name] and command.calc.settings[self.settings_name + "_objects"]:
            command.command_ast = ast.fix_missing_locations(self.resolver.visit(command.command_ast))


class NotationVector(CalculatorPlugin):
    """Calculator plugin to allow for shortened vector and matrix notation

    .. code-block::

        Calculator >>> v[1,2,3]
        ⎡1⎤
        ⎢ ⎥
        ⎢2⎥
        ⎢ ⎥
        ⎣3⎦
        Calculator >>> m[1,2,3\\4,5,6]
        ⎡1  2  3⎤
        ⎢       ⎥
        ⎣4  5  6⎦

    .. note:: The current implementation may collide with subscripting variables that end in ``v`` and produce unwanted behavior. Use the toggle ``/ni`` to opt-out
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 60)
        self.settings_name = "notation_vector"
        self.settings_toggle = "nv"

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name

    def parse_command(self, command: CalculatorCommand) -> None:
        """Applies the vector and matrix expansion"""
        # Vector expansion
        while True:
            new_command = ""
            contents = ""
            count = -1
            state = None
            for i, c in enumerate(command.command):
                if not state and new_command and new_command[-1] == "v" and c == "[":
                    new_command = new_command[:-1]
                    state = True
                    count = 1
                elif state and (c == "[" or c == "]"):
                    count += 1 if c == "[" else -1
                    if count == 0:
                        new_command += f"Matrix([{contents.replace('&', ',')}])"
                        contents = ""
                        state = False
                    else:
                        contents += c
                elif not state:
                    new_command += c
                elif state:
                    contents += c
            if state is None:
                break
            command.command = new_command
        # Matrix expansion
        while True:
            new_command = ""
            contents = ""
            count = -1
            state = None
            for c in command.command:
                if not state and new_command and new_command[-1] == "m" and c == "[":
                    new_command = new_command[:-1]
                    state = True
                    count = 1
                elif state and (c == "[" or c == "]"):
                    count += 1 if c == "[" else -1
                    if count == 0:
                        contents = contents.replace("\\\\", "],[")
                        new_command += f"Matrix([[{contents.replace('&', ',').replace(',,', '],[')}]])"
                        contents = ""
                        state = False
                    else:
                        contents += c
                elif not state:
                    new_command += c
                elif state:
                    contents += c
            if state is None:
                break
            command.command = new_command
