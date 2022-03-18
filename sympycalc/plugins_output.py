from __future__ import annotations

import sympy
import re as regex
from sympy import *
from .calc import Calculator, CalculatorCommand, CalculatorContext
from .plugin import CalculatorPlugin


class OutputDecimal(CalculatorPlugin):
    """Calculator plugin to automatically display the decimal representation of the result"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 200)
        self.settings_name = "output_decimal"
        self.settings_toggle = "od"
        self.ignore_types = set([sympy.core.numbers.One, sympy.core.numbers.Zero, sympy.core.numbers.Integer, sympy.core.numbers.Float])

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.context.output_decimal = self.output_decimal

    def command_success(self, command: CalculatorCommand) -> None:
        """Send the command to the interpreter to output the decimal represent"""
        if not command.calc.settings[self.settings_name]:
            return
        command.calc.interpret("try:\n\tdel _\nexcept NameError: pass\n")
        command.calc.interpret("try:\n\toutput_decimal(_)\nexcept NameError: pass\n")

    def check_decimal(self, s: str) -> str:
        """Returns if the given string if it is a valid decimal representation of a number, otherwise None"""
        return s if (regex.match(r"^-?\d+(\.\d+)?(e-?\d+)?(\*I)?$", s) or regex.match(r"^-?\d+(\.\d+)(e-?\d+)?\s?[-\+]\s?\d+(\.\d+)?(e-?\d+)?\*I$", s)) else None

    def output_decimal(self, output) -> None:
        """Prints the decimal of the given output"""
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
                    print(f"Decimals: ", end="")
                    pretty_print(out_list)
                return
            if type(output) not in self.ignore_types and not output.free_symbols and self.check_decimal(str(output.evalf())):
                print(f"Decimal: ", end="")
                pretty_print(output.evalf())
        except (TypeError, AttributeError, ValueError):
            pass


class OutputStore(CalculatorPlugin):
    """Calculator plugin to automatically display the decimal representation of the result"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 210)
        self.settings_name = "output_store"
        self.settings_toggle = "os"
        self.ignore_types = set([sympy.core.symbol.Symbol, sympy.core.numbers.One, sympy.core.numbers.Zero])

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        self.context = calc.context
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.context.out = [None]
        calc.context.output_store = self.output_store

    def command_success(self, command: CalculatorCommand) -> None:
        """Send the command to the interpreter to store the output"""
        if not command.calc.settings[self.settings_name]:
            return
        command.calc.interpret("try:\n\tdel _\nexcept NameError: pass\n")
        if not command.calc.chksym("out"):
            command.calc.context.out = [None]
            return
        command.calc.interpret("try:\n\toutput_store(_)\nexcept NameError: pass\n")

    def output_store(self, output) -> None:
        if output is self.context.out or output is None:
            return
        if output in self.context.out and (n := self.context.out.index(output)):
            print(f"Result in out[{n}]")
            return
        if "__iter__" in dir(output):
            checks = list(output)
        else:
            checks = [output]
        for o in checks:
            if o.__class__.__module__.startswith("sympy.") and type(o) not in self.ignore_types and str(type(o)) != "<class 'sympy.core.assumptions.ManagedProperties'>":
                self.context.out.append(output)
                print(f"Result stored in out[{len(self.context.out)-1}]")
                break
