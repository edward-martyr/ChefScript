from __future__ import annotations

from typing import NamedTuple

from pyparsing import (
    Group,
    IndentedBlock,
    Keyword,
    OneOrMore,
    Optional,
    ParserElement,
    Regex,
    Suppress,
    ZeroOrMore,
    pyparsing_common,
)
from regex import compile as regex_compile

from pychef import (
    Ingredient as PychefIngredient,
    Quantity as PychefQuantity,
    Recipe as PychefRecipe,
)

ParserElement.set_default_whitespace_chars(" \t")


class Comment(str):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class Cook(NamedTuple):
    recipe_name: str
    scale: float | PychefIngredient | None
    idx: int  # traceback information


class Parser:
    parser: ParserElement

    @classmethod
    def parse(cls, string):
        return cls.parser.parse_string(string, parse_all=True)


class Keywords(Parser):
    NEWLINE = Suppress("\n")
    COMMENT_START = Suppress("(")
    COMMENT_END = Suppress(")")
    OF = Suppress(Keyword("of"))
    COOK = Suppress(Keyword("cook"))
    FOR = Suppress(Keyword("for"))
    TIMES = Suppress(Keyword("times"))
    WITH = Suppress(Keyword("with"))

    parser = NEWLINE | COMMENT_START | COMMENT_END | OF | COOK | FOR | TIMES | WITH


class NumberParser(Parser):
    r"""
    ``<number> ::= <single_number> | <single_number> <number>``

    ``<single_number> ::= <fraction> | <signed_float>``

    ``<fraction> ::= <signed_float>"/"<signed_float>`` (no spaces)

    ``<signed_float>`` is defined by the Regex ``[+-]?\d+\.?\d*([eE][+-]?\d+)?``
    """

    signed_float = pyparsing_common.fnumber.copy()

    fraction = signed_float + "/" + signed_float
    fraction.add_condition(
        lambda t: float(t[2]) != 0, message="Denominator must not be zero", fatal=True
    )
    fraction.add_parse_action(lambda loc, t: float(t[0]) / float(t[2]))

    single_number = fraction | signed_float
    single_number.leave_whitespace(recursive=False)

    number = OneOrMore(single_number)
    number.ignore_whitespace(recursive=False)
    number.add_parse_action(lambda loc, t: sum(t))

    parser = number
    """Returns the float"""


class VariableNameParser(Parser):
    r"""
    ``<variable_name> ::= <word> | <word> <variable_name>``

    ``<word>`` is a string any character except control characters and whitespace,
    defined by the Regex ``[^\p{C}\p{Z}]+``
    """

    word = Regex(regex_compile(r"[^\p{C}\p{Z}]+"))

    variable_name = OneOrMore(word, stop_on=Keywords.parser)
    variable_name.add_parse_action(lambda loc, t: " ".join(t))

    parser = variable_name
    """Returns the variable, normalised by removing duplicate whitespaces"""


class QuantityParser(Parser):
    """
    ``<quantity> ::= <number> <unit>`` (optional space)

    ``<unit> ::= <variable_name>``
    """

    @staticmethod
    def quantity_condition(t):
        try:
            PychefQuantity(t[0], t[1])
        except Exception:
            return False
        return True

    @staticmethod
    def quantity_parse_action(loc, t):
        return PychefQuantity(t[0], t[1])

    unit = VariableNameParser.parser.copy()
    unit.add_parse_action(lambda loc, t: t[0])

    quantity = NumberParser.parser + unit
    quantity.add_condition(quantity_condition, message="Invalid quantity", fatal=True)
    quantity.add_parse_action(quantity_parse_action)

    parser = quantity
    """Returns the quantity"""


class CommentParser(Parser):
    """
    ``<comment> ::= <comment_start> <comment_text> <comment_end>``

    ``<comment_start> ::= "("``

    ``<comment_end> ::= ")"``

    ``<comment_text>`` is string of any character except ``)``,
    defined by the Regex ``[^)]+``
    """

    comment_text = Regex(regex_compile(r"[^)]+"))

    comment = Keywords.COMMENT_START + comment_text + Keywords.COMMENT_END

    suppressed_comment = Suppress(comment)

    parser = comment
    """Returns the string of the comment text"""


class IngredientParser(Parser):
    """
    ``<ingredient> ::= <quantity> "of" <variable_name>``
    """

    ingredient = (
        QuantityParser.parser + Suppress(Keyword("of")) + VariableNameParser.parser
    )
    ingredient.add_parse_action(lambda loc, t: PychefIngredient(t[1], t[0]))

    parser = ingredient
    """Returns the ingredient"""


class RecipeParser(Parser):
    """
    ``<recipe> ::= <recipe_name> NEWLINE INDENT <recipe_body>``

    ``<recipe_name> ::= <variable_name>``

    ``<recipe_body> ::= <recipe_line> NEWLINE | <recipe_line> NEWLINE <recipe_body>``

    ``<recipe_line> ::= <comment> | <ingredient> <comment> | ``

    (``NEWLINE`` is allowed to be repeated)
    """

    @staticmethod
    def recipe_parse_action(loc, t):
        name = t[0]
        instructions = t[1]

        for i, instruction in enumerate(instructions):
            if isinstance(instruction[0], str):
                instructions[i][0] = PychefRecipe(instructions[i][0], [])
            if len(instruction) != 2:
                instruction.append(None)

        recipe = PychefRecipe(name, instructions)
        recipe.idx = loc  # type: ignore
        return recipe

    recipe_line = CommentParser.suppressed_comment | Group(
        Optional(IngredientParser.parser | VariableNameParser.parser)
        + Optional(CommentParser.parser)
    )

    recipe_body = IndentedBlock(
        ZeroOrMore(Keywords.NEWLINE) + recipe_line + OneOrMore(Keywords.NEWLINE)
    )

    recipe = (
        VariableNameParser.parser
        + Optional(CommentParser.suppressed_comment)
        + OneOrMore(Keywords.NEWLINE)
        + recipe_body
    )
    recipe.add_parse_action(recipe_parse_action)

    parser = recipe


class CookStatementParser(Parser):
    """
    ``<cook_statement> ::= "cook" <recipe_name>
                         | "cook" <recipe_name> <times>
                         | "cook" <recipe_name> <with>``

    ``<times> ::= "for" <number> "times"``

    ``<with> ::= "with" <ingredient>``
    """

    times = Keywords.FOR + NumberParser.parser + Keywords.TIMES

    with_ = Keywords.WITH + IngredientParser.parser

    cook_statement = Keywords.COOK + VariableNameParser.parser + Optional(times | with_)
    cook_statement.add_parse_action(
        lambda loc, t: Cook(t[0], t[1], loc) if len(t) == 2 else Cook(t[0], None, loc)
    )

    parser = cook_statement


class ChefScriptParser(Parser):
    """
    ``<chef_script> ::= <stmt> | <stmt> NEWLINE <chef_script>``

    ``<stmt> ::= <recipe> | <cook_statement>``

    (NEWLINE is allowed to be repeated)
    """

    stmt = CommentParser.suppressed_comment | Group(
        (RecipeParser.parser | CookStatementParser.parser)
        + Optional(CommentParser.suppressed_comment)
    )

    chef_script = (
        ZeroOrMore(Keywords.NEWLINE)
        + OneOrMore(stmt + ZeroOrMore(Keywords.NEWLINE))
        + ZeroOrMore(Keywords.NEWLINE)
    )

    parser = chef_script
