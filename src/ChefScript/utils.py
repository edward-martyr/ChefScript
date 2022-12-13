from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ChefScript")
except PackageNotFoundError:
    __version__ = "0.0.0"

MAX_TERMINTAL_WIDTH = 80


def pretty_str(s: str) -> str:
    return s.center(MAX_TERMINTAL_WIDTH // 2).center(MAX_TERMINTAL_WIDTH, "-")


def index_to_position(s: str, index: int) -> Position:
    """
    Returns (line_number, col) of `index` in `s`.

    https://stackoverflow.com/a/66443805/11946514
    """
    if not len(s):
        return Position(-1, -1)
    sp = s[: index + 1].splitlines(keepends=True)
    return Position(len(sp), len(sp[-1]))


class Position:
    def __init__(self, line: int, col: int):
        self.line = line
        self.col = col

    def __str__(self):
        return f"{self.line}:{self.col}"

    def __repr__(self):
        return f"{self.__class__.__name__}(line={self.line}, col={self.col})"

    def __bool__(self):
        return self.line > 0 and self.col > 0


class ChefScriptException(BaseException):
    ...


class ChefScriptInternalError(ChefScriptException):
    def __init__(self, msg: str, fn: str):
        self.msg = msg
        self.fn = fn

    def __str__(self):
        return f"In {self.fn}: internal error: {self.msg}"


class ChefScriptErrorWithPosition(ChefScriptException):
    def __init__(self, msg: str, fn: str, pos: Position):
        self.msg = msg
        self.fn = fn
        self.pos = pos


class ChefScriptKeyboardInterrupt(ChefScriptErrorWithPosition):
    def __str__(self):
        if self.msg:
            return f"In {self.fn}:{self.pos}: keyboard interrupt: {self.msg}"
        elif self.pos:
            return f"In {self.fn}:{self.pos}: keyboard interrupt"
        else:
            return f"In {self.fn}: keyboard interrupt"


class ChefScriptSyntaxError(ChefScriptErrorWithPosition):
    def __str__(self):
        return f"In {self.fn}:{self.pos}: syntax error: {self.msg}"


class ChefScriptRuntimeError(ChefScriptErrorWithPosition):
    def __str__(self):
        return f"In {self.fn}:{self.pos}: runtime error: {self.msg}"
