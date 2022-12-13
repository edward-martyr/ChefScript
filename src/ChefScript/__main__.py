from argparse import ArgumentParser
from pathlib import Path
from sys import stderr

from .interpreter import ChefScriptInterpreter
from .utils import ChefScriptKeyboardInterrupt, __version__, pretty_str


def main():
    parser = ArgumentParser(
        description="Run a ChefScript programme. "
        "When no file is specified, ChefScript will run in interactive mode."
    )
    parser.add_argument(
        "filename",
        type=Path,
        help="Enter the ChefScript file to run",
        nargs="?",
        default=None,
    )
    args = parser.parse_args()

    interpreter = ChefScriptInterpreter()

    try:
        if args.filename is None or args.filename == "-":
            print(pretty_str(f"This is ChefScript {__version__}"))
            interpreter.interpret_stdin()
        else:
            try:
                interpreter.interpret_file(args.filename.resolve())
            except FileNotFoundError:
                print(
                    f"No such file or directory: '{args.filename}'",
                    file=stderr,
                )

    except KeyboardInterrupt:
        keyboard_interrupt = ChefScriptKeyboardInterrupt(
            "",
            interpreter.filename,
            interpreter.pos,
        )
        print(keyboard_interrupt, file=stderr)


if __name__ == "__main__":
    main()
