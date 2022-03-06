from __future__ import annotations
from typing import Any
import re as regex

import sympy
from sympy import *
from .calculator import Calculator, CalculatorCommand, CalculatorContext
from .plugin import CalculatorPlugin

class NotationConstants(CalculatorPlugin):
    """Calculator plugin to expand _x to constants['x'], where the dictionary contains common physical constants"""

    def __init__(self, table: dict[str, Any] = None) -> None:
        """Initializes the plugin with the lookup table. Defaults to physical constants"""
        super().__init__(self.__class__.__name__, 50)
        self.settings_name = "auto_constants"
        self.settings_toggle = "ac"
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
                "Na": sympify("6.02214076") * 10 ** -23,  # Avogadro constant
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

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.context.constants = self.table

    def handle_command(self, command: CalculatorCommand) -> str | None:
        """Applies the substitution"""
        if not command.calc.settings[self.settings_name]:
            return
        # Use a regex to apply the substitution
        command.command = regex.sub(r"(?<![a-zA-Z_\d])(_)([a-zA-Z0-9]+)", r"constants['\2']", command.command)


class NotationExponent(CalculatorPlugin):
    """Calculator plugin to expand _x to constants['x']"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 30)
        self.settings_name = "auto_exponent"
        self.settings_toggle = "ae"

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = False
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name

    def handle_command(self, command: CalculatorCommand) -> None:
        """Apply a simple substitution"""
        if not command.calc.settings[self.settings_name]:
            return
        command.command = command.command.replace("^", "**")


class NotationInterval(CalculatorPlugin):
    """Calculator plugin to allow for alternate interval notation, i[1,2] and i]-oo,oo["""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 61)
        self.settings_name = "auto_interval"
        self.settings_toggle = "ai"

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name

    def handle_command(self, command: CalculatorCommand) -> None:
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
    """Calculator plugin to allow for multiplication by juxtaposition with numbers, such as 2pi"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 20)
        self.settings_name = "auto_multiply"
        self.settings_toggle = "am"
        self.command_allowed_symbols = set()
        self.ignored_types_not_last = set([type(sympy.Basic), sympy.core.function.FunctionClass, type(lambda x: x), type(sympify), type(type), type(sympy), sympy.printing.printer._PrintFunction])

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.settings[self.settings_name + "_numbers"] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle + "n"] = self.settings_name + "_numbers"
        calc.settings[self.settings_name + "_objects"] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle + "o"] = self.settings_name + "_objects"

    def handle_command(self, command: CalculatorCommand) -> None:
        """Use a regex to apply the substitution"""
        if not command.calc.settings[self.settings_name]:
            return
        command.command = regex.sub(r"(?<![a-zA-Z_])(\d)([a-zA-Z])", r"\1*\2", command.command)
        self.command_allowed_symbols.clear()

    def handle_runtime_error(self, command: CalculatorCommand, data: str) -> None:
        if command.calc.settings[self.settings_name] and command.calc.settings[self.settings_name + "_objects"] and data.split("\n")[-2].startswith("NameError: ") and data.split("\n")[-2].split("'")[1] != "_":
            target = data.split("\n")[-2].split("'")[1]
            if target in self.command_allowed_symbols:
                return
            data = target
            definitions = command.calc.context.__dict__
            defined = definitions.keys()
            end = len(data)
            resolved = []
            while end > 0:
                found = False
                for i in range(end):
                    if data[i:end] in defined:
                        if (resolved or end != len(data)) and type(definitions[data[i:end]]) in self.ignored_types_not_last:
                            continue
                        if end != len(data):
                            resolved.append(data[end:])
                        resolved.append(data[i:end])
                        end = i
                        data = data[:i]
                        found = True
                if not found:
                    if end == 1:
                        resolved.append(data)
                        break
                    end -= 1
            if len(resolved) == 1:
                return
            resolved.reverse()
            for x in resolved:
                self.command_allowed_symbols.add(x)
            command.command = command.command.replace(target, "*".join(resolved))
            command.resend_command = True


class NotationVector(CalculatorPlugin):
    """Calculator plugin to allow for alternate vector and matrix notation, v[1,2,3] and m[1,2,3\\\\4,5,6]"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__, 60)
        self.settings_name = "auto_vector"
        self.settings_toggle = "av"

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = True
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name

    def handle_command(self, command: CalculatorCommand) -> None:
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
