import ast
import symtable

from .calc import Calculator


class CalculatorCommand:
    """Data for a single calculator command"""

    def __init__(self, calc: Calculator, command: str) -> None:
        self.calc = calc
        self._command = command
        self._command_ast = None
        self._command_symtable = None
        self._valid_syntax = False
        self.command_original = command
        self.multiline_command = False
        self.abort = False
        self.resend_command = False
        self.print_error = False
        self.success = False
        self.buffer = None

    @property
    def command(self) -> str:
        return self._command

    @command.setter
    def command(self, value: str) -> None:
        if self.valid_syntax and self._command != value:
            self._command_ast = ast.parse(value, filename="<input>", mode="single")
            self._command_symtable = symtable.symtable(value, filename="<input>", compile_type="single")
        self._command = value

    @property
    def valid_syntax(self) -> bool:
        return self._valid_syntax

    @valid_syntax.setter
    def valid_syntax(self, value: bool) -> None:
        self._valid_syntax = value
        if value:
            self._command_ast = ast.parse(self._command, filename="<input>", mode="single")
            self._command_symtable = symtable.symtable(self._command, filename="<input>", compile_type="single")

    @property
    def command_ast(self) -> ast.AST | None:
        if not self._valid_syntax:
            raise ValueError("Attempted to get the AST of a command without valid syntax")
        return self._command_ast

    @command_ast.setter
    def command_ast(self, value: ast.AST) -> None:
        self._valid_syntax = True
        self.command = ast.unparse(value)

    def ast_update(self) -> None:
        """Tells the command to update if the AST was modified in place"""
        self._command = ast.unparse(self._command_ast)

    @property
    def command_symtable(self) -> symtable.SymbolTable | None:
        return self._command_symtable

    def __str__(self) -> str:
        return self.command

    def __repr__(self) -> str:
        return f"CalculatorCommand({self.command})"
