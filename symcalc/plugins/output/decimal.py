from __future__ import annotations

import ast
import numbers
import re as regex
from typing import Any

import sympy
from symcalc.calc import Calculator
from symcalc.command import CalculatorCommand
from symcalc.plugin import CalculatorPlugin


class OutputDecimal(CalculatorPlugin):
    """Calculator plugin to automatically display the decimal representation of the result

    .. code-block::

        Calculator >>> 3+3.2j
        3 + 3⋅ⅈ
        Decimal: 3.0 + 3.2*I
        Calculator >>> sympify('123/321',rational=True)
        41
        ───
        107
        Decimal: 0.383177570093458
        Calculator >>> x=sympify('123/321',rational=True)
        Decimal: 2.60975609756098

    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 200)
        self.ignore_types = set([sympy.core.numbers.One, sympy.core.numbers.Zero, sympy.core.numbers.Integer, sympy.core.numbers.Float, int, float])
        self.last_result = None

    def hook(self, calc: Calculator) -> None:
        # Register the toggles for this plugin
        self.register_toggle(calc, "od", "output_decimal", True)
        calc.context.output_decimal = self.output_decimal
        calc.context.check_number = self.check_number

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

    def check_number(self, s: str | None) -> str | None:
        """Returns if the given string if it is a valid representation of a number

        Parameters
        ---------
        s : :class:`str` | None
            The string to check

        Returns
        -------
        :class:`string` | None
            ``s`` if it is a valid decimal representation, otherwise ``None``"""
        if s is None:
            return None
        if regex.match(r"^\(-?\d+(\.\d*)?(e[-\+]?\d+)?\s?[-\+]\s?\d+(\.\d*)?(e[-\+]?\d+)?((\*I)|j)\)$", s):
            return s[1:-1]
        return s if (regex.match(r"^-?\d+(\.\d*)?(e[-\+]?\d+)?((\*I)|j)?$", s) or regex.match(r"^-?\d+(\.\d*)?(e[-\+]?\d+)?\s?[-\+]\s?\d+(\.\d*)?(e[-\+]?\d+)?((\*I)|j)$", s)) else None

    def check_type(self, obj: Any) -> bool:
        """Returns whether an object is not an instance of any of the types in ``self.ignored_types``

        Parameters
        ----------
        obj : Any
            The object to check

        Returns
        -------
        :class:`bool`
            Whether the object is not an instance of an ignored type
        """
        for t in self.ignore_types:
            if isinstance(obj, t):
                return False
        return True

    def output_decimal(self, output: Any) -> None:
        """Prints the decimal of the given output. Available in the calculator context

        Parameters
        ----------
        output : :class:`Any`
            The output to be printed, if it is a valid decimal
        """
        if isinstance(output, sympy.matrices.dense.MutableDenseMatrix) and output.shape[1] == 1:
            output = list(output)
        if isinstance(output, list):
            out_list = []
            should_print = False
            for o in output:
                try:
                    s = str(o.evalf(n=5)) if isinstance(o, sympy.core.evalf.EvalfMixin) else str(o)
                    if self.check_number(s):
                        out_list.append(s)
                        if not self.check_type(o):
                            continue
                        elif isinstance(o, numbers.Complex):
                            r = sympy.re(o)
                            i = sympy.im(o)
                            if r != int(r) or i != int(i):
                                should_print = True
                        elif "is_complex" in o.__dir__() and o.is_complex:
                            r = sympy.re(o)
                            i = sympy.im(o)
                            if self.check_number(str(r.evalf())) and self.check_number(str(i.evalf())) and (type(r) not in self.ignore_types or type(i) not in self.ignore_types):
                                should_print = True
                except (TypeError, AttributeError, ValueError):
                    raise
                    out_list.append(None)
            if should_print and out_list != [None] * len(out_list):
                if not isinstance(self.last_result, list) or len(self.last_result) != len(out_list) or (True for i in range(len(out_list)) if self.last_result[i] == out_list[i]):
                    print(f"Decimals: ", end="")
                    sympy.pretty_print(out_list)
                    self.last_result = out_list
            return
        elif self.check_type(output):
            d = str(output.evalf()) if isinstance(output, sympy.core.evalf.EvalfMixin) else str(output)
            if self.check_number(str(d)) and d != self.last_result:
                should_print = True
                if "is_complex" in output.__dir__() and output.is_complex:
                    r = sympy.re(output)
                    i = sympy.im(output)
                    if not (self.check_number(str(r.evalf())) and self.check_number(str(i.evalf())) and (self.check_type(r) or self.check_type(i))):
                        should_print = False
                elif isinstance(output, numbers.Complex):
                    if output.real == int(output.real) and output.imag == int(output.imag):
                        should_print = False
                if should_print:
                    print(f"Decimal: ", end="")
                    sympy.pretty_print(d)
            self.last_result = d
