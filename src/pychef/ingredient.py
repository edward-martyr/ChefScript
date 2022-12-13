from __future__ import annotations

from copy import copy
from typing import overload

from quantities import Quantity as PQuantity

from .utils import Real

__all__ = ["Quantity", "Ingredient"]


class Quantity:
    """
    A simple quantity class to hold a value and a unit.

    It is intended to hold the weights and volumes of ingredients in cooking,
    so it doesn't support complex units (multiplication by another quantity),
    but it does support multiplication by bare numbers.
    """

    quantity: PQuantity

    def __init__(self, value: Real, unit: str) -> None:
        self.quantity = PQuantity(value, self._normalize_unit(unit))

    def __copy__(self) -> Quantity:
        return Quantity(self.value, self.unit)

    def __repr__(self) -> str:
        return f"{self.value:.3f} {self.unit}"

    def __add__(self, other) -> Quantity:
        if isinstance(other, Quantity):
            other_copy = copy(other)
            other_copy.rescale(self.unit)
            return Quantity(self.value + other_copy.value, self.unit)
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'"
            )

    def __sub__(self, other) -> Quantity:
        if isinstance(other, Quantity):
            other_copy = copy(other)
            other_copy.rescale(self.unit)
            return Quantity(self.value - other_copy.value, self.unit)
        else:
            raise TypeError(
                f"unsupported operand type(s) for -: '{type(self)}' and '{type(other)}'"
            )

    def __mul__(self, other) -> Quantity:
        if isinstance(other, Real):  # type: ignore[misc, arg-type]
            return Quantity(self.value * other, self.unit)
        else:
            raise TypeError(
                f"unsupported operand type(s) for *: '{type(self)}' and '{type(other)}'"
            )

    def __rmul__(self, other) -> Quantity:
        return self.__mul__(other)

    @overload
    def __truediv__(self, other: float) -> Quantity:
        ...

    @overload
    def __truediv__(self, other: Quantity) -> float:
        ...

    def __truediv__(self, other) -> Quantity | float:
        if isinstance(other, Real):  # type: ignore[misc, arg-type]
            return self.__mul__(1 / other)
        elif isinstance(other, Quantity):
            other_copy = copy(other)
            other_copy.rescale(self.unit)
            return self.value / other_copy.value
        else:
            raise TypeError(
                f"unsupported operand type(s) for /: '{type(self)}' and '{type(other)}'"
            )

    @staticmethod
    def _normalize_unit(unit: str) -> str:
        return unit.replace(".", "").replace(" ", "_").replace("^", "**")

    def rescale(self, unit: str) -> None:
        self.quantity = self.quantity.rescale(self._normalize_unit(unit))

    @property
    def value(self) -> float:
        return float(self.quantity.magnitude)

    @property
    def unit(self) -> str:
        return str(self.quantity.dimensionality).replace("_", " ")


class Ingredient:
    def __init__(self, name: str, quantity: Quantity) -> None:
        self.name = name
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"{self.quantity} of {self.name}"

    def __add__(self, other) -> Ingredient:
        if isinstance(other, Ingredient):
            if self.name != other.name:
                raise ValueError("Ingredients must have the same name")
            return Ingredient(self.name, self.quantity + other.quantity)
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'"
            )

    def __sub__(self, other) -> Ingredient:
        if isinstance(other, Ingredient):
            if self.name != other.name:
                raise ValueError("Ingredients must have the same name")
            return Ingredient(self.name, self.quantity - other.quantity)
        else:
            raise TypeError(
                f"unsupported operand type(s) for -: '{type(self)}' and '{type(other)}'"
            )

    def __mul__(self, other) -> Ingredient:
        if isinstance(other, Real):  # type: ignore[misc, arg-type]
            return Ingredient(self.name, self.quantity * other)
        else:
            raise TypeError(
                f"unsupported operand type(s) for *: '{type(self)}' and '{type(other)}'"
            )

    def __rmul__(self, other) -> Ingredient:
        return self.__mul__(other)

    def __truediv__(self, other) -> Ingredient:
        if isinstance(other, Real):  # type: ignore[misc, arg-type]
            return self.__mul__(1 / other)
        else:
            raise TypeError(
                f"unsupported operand type(s) for /: '{type(self)}' and '{type(other)}'"
            )
