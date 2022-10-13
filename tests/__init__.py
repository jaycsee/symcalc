from __future__ import annotations

import math
import random
import string

import sympy
from symcalc import Calculator, CalculatorPlugin


def random_str():
    return "".join(random.choice(string.ascii_letters) for i in range(16))


def random_int(a, b):
    return random.randint(a, b)


def expand_number(x, with_negatives=True):
    r = []
    if x >= 10000000:
        r.append(x // 10000000)  # Small Integers
    r.append(x)  # Medium Integers
    r.append(x * 10000000000)  # Big Integers
    r.append(x / 1000000)  # Decimals
    r.append(x / 10)  # Big Fractions
    r.append(x / 10000000000000000000000000000)  # Small Fractions
    r.append(x / 9999)  # Repeating decimals
    r.append(abs(x) ** random_int(-50, -16))  # Irrational numbers
    if with_negatives:
        n = []
        for x in r:
            n.append(-x)
        r += n
    return r


def random_ints(unique_size: int):
    r: list[int] = []
    s: set[int] = set()
    for i in range(unique_size):
        x = random_int(1, 1000000000)
        for y in expand_number(x):
            a = round(y)
            if a not in s:
                s.add(a)
                r.append(a)
    return r


def random_decimals(unique_size: int):
    r: list[int | float] = []
    s: set[int | float] = set()
    for i in range(unique_size):
        x = random_int(1, 1000000000)
        for a in expand_number(x):
            if a not in s:
                s.add(a)
                r.append(a)
    return r


def random_decimals_sympy(unique_size: int):
    r: list[sympy.Integer | sympy.Float] = []
    s: set[sympy.Integer | sympy.Float] = set()
    for i in range(unique_size):
        x = random_int(1, 1000000000)
        for a in expand_number(x):
            if a not in s:
                s.add(a)
                r.append(sympy.sympify(a))
    return r


def random_fractions(unique_size: int):
    r: list[int | float] = []
    s: set[int | float] = set()
    for i in range(unique_size):
        x = random_int(1, 100000000000000) / random_int(1, 1000000000)
        for a in expand_number(x):
            if a not in s:
                s.add(a)
                r.append(a)
    return r


def random_fractions_sympy(unique_size: int):
    r: list[sympy.Rational] = []
    s: set[sympy.Rational] = set()
    for i in range(unique_size):
        x = sympy.Rational(random_int(1, 100000000000000), sympy.sympify(random_int(1, 1000000000)))
        for a in expand_number(x):
            if a not in s:
                s.add(a)
                r.append(a)
    return r


def random_numbers(unique_size: int):
    xs = unique_size // 2
    ys = unique_size // 2 + unique_size % 2
    if xs == 0:
        xs = 1
    return random_decimals(xs) + random_fractions(ys)


def random_numbers_sympy(unique_size: int):
    xs = unique_size // 2
    ys = unique_size // 2 + unique_size % 2
    if xs == 0:
        xs = 1
    return random_decimals_sympy(xs) + random_fractions_sympy(ys)


def random_complexes(unique_size: int):
    r: list[complex] = []
    xs = unique_size // 2
    ys = unique_size // 2 + unique_size % 2
    if xs == 0:
        xs = 1
    x = random_numbers(xs)
    y = random_numbers(ys)
    for a in x:
        for b in y:
            r.append(a + b * 1j)
    return r


def random_complexes_sympy(unique_size: int):
    r: list[int | float | sympy.Integer | sympy.Float | sympy.Rational | sympy.Add] = []
    xs = unique_size // 2
    ys = unique_size // 2 + unique_size % 2
    if xs == 0:
        xs = 1
    x = random_numbers_sympy(xs)
    y = random_numbers_sympy(ys)
    for a in x:
        for b in y:
            r.append(a + b * sympy.I)
    return r


def generate_test_values(unique_size: int, sympy_objects: bool = False, real: bool = True, complex: bool = False, include_edge_cases: bool = True):
    r = []
    if not sympy_objects:
        if real:
            r.extend(random_numbers(unique_size))
            if include_edge_cases:
                r.extend([0, -0, 0.0, -0.0, 1, 1.0, -1, -1.0, math.pi, math.e, -math.pi, -math.e])
        if complex:
            r.extend(random_complexes(unique_size))
            if include_edge_cases:
                r.extend([0j, -0j, 0.0j, -0.0j, 1j, 1.0j, -1j, -1.0j, math.pi * 1j, math.e * 1j, math.pi * -1j, math.e * -1j])
    else:
        if real:
            r.extend(random_numbers_sympy(unique_size))
            if include_edge_cases:
                r.extend([sympy.sympify(0), sympy.sympify(-0), sympy.sympify(0.0), sympy.sympify(-0.0), sympy.sympify(1), sympy.sympify(1.0), sympy.sympify(-1), sympy.sympify(-1.0), sympy.pi, sympy.E, -sympy.pi, -sympy.E])
        if complex:
            r.extend(random_complexes_sympy(unique_size))
            if include_edge_cases:
                r.extend([sympy.sympify(0j), sympy.sympify(-0j), sympy.sympify(0.0j), sympy.sympify(-0.0j), sympy.sympify(1j), sympy.sympify(1.0j), sympy.sympify(-1j), sympy.sympify(-1.0j), sympy.pi * sympy.I, sympy.E * sympy.I, -sympy.pi * sympy.I, -sympy.E * sympy.I])
    return r


class DefaultPlugin(CalculatorPlugin):
    def __init__(self):
        super().__init__(random_str(), -1)


class TestCalculator(Calculator):
    __test__ = False

    class OutputCapture(CalculatorPlugin):
        def __init__(self):
            super().__init__(self.__class__.__name__, 999999)
            self.captured = None

        def hook(self, calc):
            calc.context.output_capture = self.output_capture  # type: ignore
            self.calc = calc

        def end_interaction(self, command):
            self.calc.interpret("try:\n\toutput_capture(_)\nexcept NameError:\n\tpass\n")

        def output_capture(self, value):
            self.captured = value

    def __init__(self):
        super().__init__()
        self.capture = TestCalculator.OutputCapture()
        self.register_plugin(self.capture)

    def register_plugin_and_enable(self, plugin: CalculatorPlugin) -> TestCalculator:
        s = set(self.settings.keys())
        super().register_plugin(plugin)
        for k in set(self.settings.keys()) - s:
            self.settings[k] = True
        return self

    def command(self, command):
        super().command(command)
        return self.capture.captured
