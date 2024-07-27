import argparse
from .commands.build_index import build_cache
from .commands.search import search_hooks


def setup_parser():
    parser = argparse.ArgumentParser(description="Pre-commit hook index tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser(
        "build-index", help="(Re)build the index of pre-commit hooks."
    )

    search_parser = subparsers.add_parser("search", help="Search for pre-commit hooks")
    search_parser.add_argument("query", help="Search query")

    return parser


def main() -> int:
    parser = setup_parser()
    args = parser.parse_args()

    if args.command == "build-index":
        build_cache()
    elif args.command == "search":
        search_hooks(args.query)
    elif args.command is None:
        parser.print_help()
        return 1
    else:
        print(f"Unknown command: {args.command}")
        return 1

    return 0
