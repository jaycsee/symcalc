from __future__ import annotations

import ast
import re as regex
from typing import Any

import sympy

from ...calc import Calculator
from ...command import CalculatorCommand
from ...context import CalculatorContext
from ...plugin import CalculatorPlugin


class NotationConstants(CalculatorPlugin):
    """Calculator plugin to expand ``_x`` to ``constants['x']``, where the dictionary contains common physical constants. Different constants may be defined on initialization.

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
                return self.generic_visit(ast.Subscript(value=ast.Name(id="constants", ctx=ast.Load()), slice=ast.Constant(value=node.id[1:]), ctx=ast.Load()))
            return self.generic_visit(node)

    def __init__(self, table: dict[str, Any] | None = None):
        """Initializes the plugin with the lookup table

        Parameters
        ----------
        table : :class:`dict[str, Any]`
            The lookup table to use. Defaults to physical constants
        """
        super().__init__(self.__class__.__name__, 50)
        self.table = (
            table
            if table is not None
            else {
                "c": sympy.sympify("299792458"),  # Speed of light
                "h": sympy.sympify("6.62607015") * 10**-34,  # Planck's constant
                "G": sympy.sympify("6.6743015") * 10**-11,  # Newtonian constant of gravitation
                "g": sympy.sympify("9.80665"),  # Earth's gravity
                "epsilon0": sympy.sympify("8.854187812813") * 10**-12,  # Vacuum electric permittivity
                "mu0": sympy.sympify("1.2566370621219") * 10**-6,  # Vacuum magnetic permittivity
                "e": sympy.sympify("1.602176634") * 10**-19,  # Elementary charge
                "Na": sympy.sympify("6.02214076") * 10**-23,  # Avogadro's constant
                "ke": sympy.sympify("8.987551792314") * 10**9,  # Coulomb constant
                "mp": sympy.sympify("1.6726219236951") * 10**-27,  # Proton mass
                "mn": sympy.sympify("1.6749274980495") * 10**-27,  # Neutron mass
                "me": sympy.sympify("9.109383701528") * 10**-31,  # Electron mass
                "R": sympy.sympify("8.31446261815324"),  # Ideal gas constant
                "k": sympy.sympify("1.380649") * 10**-23,  # Boltzmann constant
                "a0": sympy.sympify("5.2917721090380") * 10**-11,  # Bohr radius
                "phi": (sympy.sympify("1") + sympy.sqrt(5)) / sympy.sympify("2"),  # Golden ratio
            }
        )
        self.checker = None

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "nc", "notation_constants", True)
        setattr(calc.context, "constants", self.table)
        self.checker = NotationConstants.CheckNames(calc.context, self.table)

    @CalculatorPlugin.if_enabled
    def handle_command(self, command: CalculatorCommand) -> str | None:
        # Apply the substitution if enabled
        assert self.checker
        command.command_ast = ast.fix_missing_locations(self.checker.visit(command.command_ast))
