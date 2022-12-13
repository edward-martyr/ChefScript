from __future__ import annotations

from collections import OrderedDict, deque
from typing import Optional, Sequence

from .ingredient import Ingredient, Quantity
from .utils import TAB, Real

__all__ = ["Recipe"]


class Recipe:
    def __init__(
        self,
        name: str,
        instructions: Sequence[tuple[Ingredient | Recipe, Optional[str]]],
    ) -> None:
        self.name = name
        self.instructions = instructions

    def __repr__(self) -> str:
        str_builder = [f"{self.name}"]
        for instruction in self.instructions:
            ingredient_or_recipe = instruction[0]
            if isinstance(ingredient_or_recipe, Ingredient):
                item = str(ingredient_or_recipe)
            else:
                item = ingredient_or_recipe.name
            str_builder.append(
                f"{TAB}{item}{'' if instruction[1] is None else f' ({instruction[1]})'}"
            )
        return "\n".join(str_builder)

    def __mul__(self, other) -> Recipe:
        if isinstance(other, Real):  # type: ignore[misc, arg-type]
            return Recipe(self.name, [(i[0] * other, i[1]) for i in self.instructions])
        else:
            raise TypeError(
                f"unsupported operand type(s) for *: '{type(self)}' and '{type(other)}'"
            )

    def __rmul__(self, other) -> Recipe:
        return self.__mul__(other)

    def __truediv__(self, other) -> Recipe:
        if isinstance(other, Real):  # type: ignore[misc, arg-type]
            return self.__mul__(1 / other)
        else:
            raise TypeError(
                f"unsupported operand type(s) for /: '{type(self)}' and '{type(other)}'"
            )

    @property
    def ingredients(self) -> list[Ingredient]:
        ingredients: list[tuple[str, Quantity]] = []
        referenced_recipe_names: set[str] = set()
        for instruction in self.instructions:
            ingredient_or_recipe = instruction[0]
            if isinstance(ingredient_or_recipe, Ingredient):
                ingredient = ingredient_or_recipe
                ingredients.append((ingredient.name, ingredient.quantity))
            else:
                recipe = ingredient_or_recipe
                if recipe.name not in referenced_recipe_names:
                    referenced_recipe_names.add(recipe.name)
                    for ingredient in recipe.ingredients:
                        ingredients.append((ingredient.name, ingredient.quantity))
        ingredients_dict: dict[str, Quantity] = {}
        for name, quantity in ingredients:
            if name in ingredients_dict:
                ingredients_dict[name] += quantity
            else:
                ingredients_dict[name] = quantity
        return sorted(
            (Ingredient(name, quantity) for name, quantity in ingredients_dict.items()),
            key=lambda i: i.name,
        )

    @property
    def pretty_str(self) -> str:
        str_builder = deque([f"Recipe for {self.name}:"])
        referenced_recipes: OrderedDict[str, Recipe] = OrderedDict()

        str_builder.append(f"{TAB}Summary of ingredients:")
        for ingredient in self.ingredients:
            str_builder.append(f"{TAB*2}{ingredient}")

        str_builder.append(f"{TAB}Instructions:")
        for instruction in self.instructions:
            ingredient_or_recipe = instruction[0]
            if isinstance(ingredient_or_recipe, Ingredient):
                item = str(ingredient_or_recipe)
            else:
                referenced_recipes.update(
                    {ingredient_or_recipe.name: ingredient_or_recipe}
                )
                item = ingredient_or_recipe.name
            str_builder.append(
                f"{TAB*2}{item}"
                f"{'' if instruction[1] is None else f' ({instruction[1]})'}"
            )

        for name, recipe in referenced_recipes.items():
            str_builder.appendleft(recipe.pretty_str)

        return "\n".join(str_builder)
