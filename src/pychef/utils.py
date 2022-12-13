from numbers import Real as NumbersReal

Real = (
    NumbersReal | int | float
)  # we should use numbers.Real, but it's not recognised by mypy yet

TAB = " " * 4
