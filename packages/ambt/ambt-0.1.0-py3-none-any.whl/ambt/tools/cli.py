from ambt.tools.template import template_generator
from ambt.tools.patcher import binary_patcher
import argparse

def main():
    parser = argparse.ArgumentParser(description="a1mb0t CLI")
    subparser = parser.add_subparsers()

    template_parser = subparser.add_parser("template", help="Generate template")
    template_parser.add_argument("binary")
    template_parser.add_argument("--libc", "-l")
    template_parser.add_argument("--remote", "-r")
    template_parser.add_argument("--uri", "-u")
    template_parser.set_defaults(func=template_generator)

    patcher_parser = subparser.add_parser("patch", help="Fetch libraries & patch binary")
    patcher_parser.add_argument("binary")
    patcher_parser.add_argument("--libc", "-l")
    patcher_parser.add_argument("--libc-version", "-v")
    patcher_parser.set_defaults(func=binary_patcher)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
