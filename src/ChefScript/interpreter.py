from collections import OrderedDict
from pathlib import Path
from sys import stderr, stdin

from pyparsing.exceptions import ParseBaseException

from pychef import Recipe as PychefRecipe

from .parser import ChefScriptParser, Cook
from .utils import (
    MAX_TERMINTAL_WIDTH,
    ChefScriptException,
    ChefScriptInternalError,
    ChefScriptRuntimeError,
    ChefScriptSyntaxError,
    Position,
    index_to_position,
    pretty_str,
)


class ChefScriptInterpreter:
    recipes: OrderedDict[str, PychefRecipe]
    pos: Position
    filename: str
    code: str

    def __init__(self) -> None:
        self.recipes = OrderedDict()
        self.pos = Position(-1, -1)

    def interpret_file(self, filename: str):
        self.filename = filename
        self.code = Path(filename).resolve().read_text(encoding="utf-8")
        self._interpret(self.code)

    def interpret_stdin(self):
        self.filename = "<stdin>"
        self.code = stdin.read()
        self._interpret(self.code)

    def _interpret(self, code: str):
        if not code.strip():
            return
        elif not code.endswith("\n"):
            code += "\n"
        try:
            try:
                parse_result = ChefScriptParser.parse(code)
            except ParseBaseException as e:
                raise ChefScriptSyntaxError(
                    e.msg,
                    self.filename,
                    Position(e.lineno, e.col),
                )

            for stmt in parse_result:
                if len(stmt) == 1:
                    if isinstance(stmt[0], PychefRecipe):
                        self._add_recipe(stmt[0])
                    elif isinstance(stmt[0], Cook):
                        self._cook(stmt[0])
                    else:
                        raise ChefScriptInternalError("Parser error", self.filename)
                elif len(stmt) >= 2:
                    raise ChefScriptInternalError("Parser error", self.filename)

        except ChefScriptException as e:
            print(e, file=stderr)

        except Exception as e:
            new_e = ChefScriptInternalError(f"Internal error: {e}", self.filename)
            print(new_e, file=stderr)

    def _add_recipe(self, recipe: PychefRecipe):
        self.pos = index_to_position(self.code, recipe.idx)  # type: ignore

        for instruction in recipe.instructions:
            if isinstance(instruction[0], PychefRecipe):
                if instruction[0].name in self.recipes:
                    instruction[0].instructions = self.recipes[
                        instruction[0].name
                    ].instructions
                else:
                    raise ChefScriptRuntimeError(
                        f"Recipe '{instruction[0].name}' "
                        f"used in '{recipe.name}' is not defined yet",
                        self.filename,
                        self.pos,
                    )
        self.recipes[recipe.name] = recipe

    def _cook(self, cook: Cook):
        self.pos = index_to_position(self.code, cook.idx)  # type: ignore

        recipe_name = cook.recipe_name
        if recipe_name not in self.recipes:
            raise ChefScriptRuntimeError(
                f"Recipe '{recipe_name}' is not defined yet", self.filename, self.pos
            )
        recipe: PychefRecipe = self.recipes[recipe_name]

        scale: float = 1

        if cook.scale is not None:
            if not isinstance(cook.scale, float):
                if cook.scale.name not in [i.name for i in recipe.ingredients]:
                    raise ChefScriptRuntimeError(
                        f"Ingredient '{cook.scale.name}' "
                        "is not in recipe '{recipe_name}'",
                        self.filename,
                        index_to_position(self.code, cook.idx),  # type: ignore
                    )
                for i in recipe.ingredients:
                    if i.name == cook.scale.name:
                        scale = cook.scale.quantity / i.quantity
                        break
            else:
                scale = cook.scale

        print(pretty_str(f"Cooking {recipe_name} with scale {scale:.3f}"))
        print((recipe * scale).pretty_str)
        print("-" * MAX_TERMINTAL_WIDTH)
