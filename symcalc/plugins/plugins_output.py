from __future__ import annotations
import ast

import re as regex
from typing import Any

import sympy
from sympy import *

from ..calc import Calculator
from ..command import CalculatorCommand
from ..plugin import CalculatorPlugin


class OutputDecimal(CalculatorPlugin):
    """Calculator plugin to automatically display the decimal representation of the result

    .. code-block::

        Calculator >>> 3+3j
        3 + 3⋅ⅈ
        Decimal: 3.0 + 3.0⋅ⅈ
        Calculator >>> 123/321
        41
        ───
        107
        Decimal: 0.383177570093458
        Calculator >>> x=321/123
        Decimal: 2.60975609756098

    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 200)
        self.ignore_types = set([sympy.core.numbers.One, sympy.core.numbers.Zero, sympy.core.numbers.Integer, sympy.core.numbers.Float])
        self.last_result = None

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "od", "output_decimal", True)
        calc.context.output_decimal = self.output_decimal

    @CalculatorPlugin.if_enabled
    def command_success(self, command: CalculatorCommand) -> None:
        # Send the command to the interpreter to output the decimal represent

        command.calc.interpret("try:\n\tdel _\nexcept NameError: pass\n")
        if isinstance(b := command.command_ast.body[0], ast.Assign):
            c = self.last_result
            self.last_result = None
            command.calc.interpret("output_decimal(" + ast.unparse(b.targets[0]) + ")")
            self.last_result = c
        else:
            command.calc.interpret("try:\n\toutput_decimal(_)\nexcept NameError: pass\n")

    def check_decimal(self, s: str) -> str:
        """Returns if the given string if it is a valid decimal representation of a number

        Parameters
        ----------
        s : :class:`str`
            The string to check

        Returns
        -------
        :class:`string` | None
            ``s`` if it is a valid decimal representation, otherwise ``None``"""
        return s if (regex.match(r"^-?\d+(\.\d+)?(e-?\d+)?(\*I)?$", s) or regex.match(r"^-?\d+(\.\d+)(e-?\d+)?\s?[-\+]\s?\d+(\.\d+)?(e-?\d+)?\*I$", s)) else None

    def output_decimal(self, output: Any) -> None:
        """Prints the decimal of the given output. Available in the calculator context

        Parameters
        ----------
        output : :class:`Any`
            The output to be printed, if it is a valid decimal
        """
        try:
            if isinstance(output, sympy.matrices.dense.MutableDenseMatrix) and output.shape[1] == 1:
                output = list(output)
            if isinstance(output, list):
                out_list = []
                print_valid = False
                print_out = False
                for o in output:
                    try:
                        if type(o) not in self.ignore_types:
                            print_out = True
                        if not o.free_symbols:
                            s = self.check_decimal(str(o.evalf(n=5)))
                            out_list.append(s)
                            if s is not None:
                                print_valid = True
                        else:
                            out_list.append(None)
                    except (TypeError, AttributeError, ValueError):
                        out_list.append(None)
                if print_out and print_valid:
                    if not isinstance(self.last_result, list) or len(self.last_result) != len(out_list) or (True for i in range(len(out_list)) if self.last_result[i] == out_list[i]):
                        print(f"Decimals: ", end="")
                        pretty_print(out_list)
                        self.last_result = out_list
                return
            elif type(output) not in self.ignore_types and not output.free_symbols and self.check_decimal(str(output.evalf())):
                d = output.evalf()
                if d != self.last_result:
                    print(f"Decimal: ", end="")
                    pretty_print(d)
                    self.last_result = d
        except ValueError as e:
            print(f"Could not find the decimal representation: {e}")
            self.last_result = None
        except (TypeError, AttributeError):
            self.last_result = None


class OutputStore(CalculatorPlugin):
    """Calculator plugin to automatically store the result in an array

    .. code-block::

        Calculator >>> 2x
        2⋅x
        Result stored in out[1]
        Calculator >>> out[1]
        2⋅x
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 210)
        self.ignore_types = set([sympy.core.symbol.Symbol, sympy.core.numbers.One, sympy.core.numbers.Zero])

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.context = calc.context
        self.register_toggle(calc, "os", "output_store", True)
        calc.context.out = [None]
        calc.context.output_store = self.output_store
        self.last_found = None  # type: int

    @CalculatorPlugin.if_enabled
    def command_success(self, command: CalculatorCommand) -> None:
        # Send the command to the interpreter to store the output
        command.calc.interpret("try:\n\tdel _\nexcept NameError: pass\n")
        if not command.calc.chksym("out"):
            command.calc.context.out = [None]
            return
        command.calc.interpret("try:\n\toutput_store(_)\nexcept NameError: pass\n")

    def output_store(self, output) -> None:
        """Decide whether to store the output in the ``out`` variable if it is not already present. Available in the calculator context

        Parameters
        ----------
        output : :class:`Any`
            The output to store
        """
        if output is self.context.out or output is None:
            return
        if output in self.context.out and (n := self.context.out.index(output)):
            if n != len(self.context.out) - 1 and n != self.last_found:
                print(f"Result in out[{n}]")
            self.last_found = n
            return
        if "__iter__" in dir(output):
            checks = []
            try:
                for i, c in enumerate(output):
                    checks.append(c)
                    if i == 10:
                        break
            except TypeError:
                checks = [output]
        else:
            checks = [output]
        for o in checks:
            try:
                if o.__class__.__module__.startswith("sympy.") and type(o) not in self.ignore_types and str(type(o)) != "<class 'sympy.core.assumptions.ManagedProperties'>":
                    self.context.out.append(output)
                    print(f"Result stored in out[{len(self.context.out)-1}]")
                    break
            except AttributeError:
                continue
