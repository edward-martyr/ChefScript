# ChefScript: an esolang for storing, creating and using recipes

## Installation

```bash
pip install ChefScript
```

## Usage

```bash
ChefScript [-h] [<filename>]
```

## Example of usage

### ChefScript code

```text
seasoned steak
    2 lb of New York strip steak (pat dry)
    1 1/2 tsp of salt (apply onto both sides)
    1 tsp of black pepper (
        apply onto both sides,
        rub in
    )

cook seasoned steak with 1 lb of New York strip steak
```

### Output

```text
--------------------Cooking seasoned steak with scale 0.500 --------------------
Recipe for seasoned steak:
    Summary of ingredients:
        1.000 lb of New York strip steak
        0.500 tsp of black pepper
        0.750 tsp of salt
    Instructions:
        1.000 lb of New York strip steak (pat dry)
        0.750 tsp of salt (apply onto both sides)
        0.500 tsp of black pepper (
        apply onto both sides,
        rub in
    )
--------------------------------------------------------------------------------
```

## Components of ChefScript

### Number

A `number` in ChefScript is a list of whitespace-separated floats or quotients (fraction of two floats). Its value is the sum of all floats and quotients in the list.

```text
1/2 (this is 0.500)
1 1/2 (this is 1.500)
1.3e2 15 .5e1 (this is 150.000)
```

The purpose of this design is to make it possible to write `1 1/2` like a recipe book will do, instead of `1.5` which is less commonly used.

### Quantity

A `quantity` is a `number` followed by a `unit`. It is recommended to write a `unit` case-insensitively (`mL` is different from `ML`, but `mL` is the same as `ml`), and using spaces to separate words (`fl oz` or `fl. oz.` looks better than `fl_oz`). It is recommended but not mandatory to put a space between the `number` and the `unit`.

```text
1 cup
1 1/2 cups
50 fl oz
```

### Ingredient

An `ingredient` is a `quantity` followed by the keyword `of` and a `name`. It is recommended to write a `name` using spaces to separate words (`chicken breast` looks better than `chicken_breast`), but sometimes an underscore has to be used when a word is in conflict with a keyword.

```text
1 lb of chicken breast
```

### Recipe

A `recipe` is a `name` followed by a list of `ingredient`s or other `recipe`s, and optionally together with a list of `instruction`s. The `name` follows the same rules as an `ingredient`'s `name`. The `instruction` is a comment that starts on the same line as an `ingredient` or a `recipe` inside the `recipe`.

```text
seasoned steak
    2 lb of New York strip steak (pat dry)
    (
        you can put a comment here as well,
        but it won't be recognised as an instruction.
    )
    1 1/2 tsp of salt (apply onto both sides)
    1 tsp of black pepper (
        apply onto both sides,
        rub in
    )
```

When an `ingredient` is mentioned more than once in a `recipe`, it will be considered a new one each time, and the quantities will be added together. When a `recipe` is mentioned more than once in a `recipe`, it will be considered the same reused, and the quantities will not be added together.

### Comment

A `comment` starts with `(` and ends with `)`. It can be placed at the end of any line, and can run for multiple lines. When put at the end of a line with an `ingredient` or a `recipe`, it will be recognised as an `instruction`.

```text
(
    this is a comment
    that runs for multiple lines
)
```

### Function

Currently, there is only one built-in function in ChefScript, which is `cook`. It takes a `recipe` and an optional `scale` as arguments, and prints out the recipe with the scale applied to all quantities. The `scale` can be a `number` or an `ingredient`, recognised by different keywords used with `cook`.

```text
cook seasoned steak
cook seasoned steak for 2 times
cook seasoned steak with 1 lb of New York strip steak
```

### Keywords and delimiters

The keywords are

```text
of
cook
for
times
with
```

The delimiters are

```text
(
)
```

These should be avoided in `name`s.
