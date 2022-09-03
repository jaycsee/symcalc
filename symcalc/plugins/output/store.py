# type: ignore
from __future__ import annotations

import sympy

from ...calc import Calculator
from ...command import CalculatorCommand
from ...plugin import CalculatorPlugin


class OutputStore(CalculatorPlugin):
    """Calculator plugin to automatically store the result in an array

    .. code-block::

        Calculator >>> 2*x
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
        self.last_found = None

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
                if type(o) not in self.ignore_types and str(type(o)) != "<class 'sympy.core.assumptions.ManagedProperties'>":
                    self.context.out.append(output)
                    print(f"Result stored in out[{len(self.context.out)-1}]")
                    break
            except AttributeError:
                continue
