import ast
import symtable

from .calc import Calculator


class CalculatorCommand:
    """Data for a single calculator command"""

    def __init__(self, calc: Calculator, command: str):
        self.calc = calc
        self._command = command
        self._command_ast = None
        self._command_symtable = None
        self._valid_syntax = False
        self.multiline_command = False
        """Whether the command is a multi-line command."""
        self.buffer: list[str] | None = None
        """The line buffer for a multi-line command"""
        self.abort = False
        self.resend_command = False
        self.print_error = False
        self.success = False

    @property
    def command(self) -> str:
        """The plaintext command. Setting this with :attr:`CalculatorCommand.valid_syntax` ``True`` updates the symbol table and the AST

        Raises
        ------
        :class:`SyntaxError`
            When setting the command to one with invalid Python syntax when  :attr:`CalculatorCommand.valid_syntax` is ``True``
        """
        return self._command

    @command.setter
    def command(self, value: str) -> None:
        if self.valid_syntax and self._command != value:
            self._command_ast = ast.parse(value, filename="<input>", mode="single")
            self._command_symtable = symtable.symtable(value, filename="<input>", compile_type="single")
        self._command = value

    @property
    def valid_syntax(self) -> bool:
        """Whether the plaintext command is valid syntax. Setting this to ``True`` updates the symbol table and the AST

        Raises
        ------
        :class:`SyntaxError`
            If :attr:`CalculatorCommand.command` is not valid Python syntax when setting to `True`
        """
        return self._valid_syntax

    @valid_syntax.setter
    def valid_syntax(self, value: bool) -> None:
        self._valid_syntax = value
        if value:
            self._command_ast = ast.parse(self._command, filename="<input>", mode="single")
            self._command_symtable = symtable.symtable(self._command, filename="<input>", compile_type="single")

    @property
    def command_ast(self) -> ast.AST:
        """The AST of the command. Setting this implies :attr:`CalculatorCommand.valid_syntax` and updates the plaintext command

        Raises
        ------
        ValueError
            If :attr:`CalculatorCommand.valid_syntax` is ``False`` during read attempt
        """
        if not self._valid_syntax:
            raise ValueError("Attempted to get the AST of a command without valid syntax")
        return self._command_ast  # type: ignore

    @command_ast.setter
    def command_ast(self, value: ast.AST) -> None:
        self._valid_syntax = True
        self.command = ast.unparse(value)

    @property
    def command_symtable(self) -> symtable.SymbolTable:
        """The symbol table of the command.

        Raises
        ------
        ValueError
            If :attr:`CalculatorCommand.valid_syntax` is ``False`` during read attempt
        """
        if not self._valid_syntax:
            raise ValueError("Attempted to get the AST of a command without valid syntax")
        return self._command_symtable  # type: ignore

    def __str__(self) -> str:
        return self.command

    def __repr__(self) -> str:
        return f"CalculatorCommand({self.command})"
