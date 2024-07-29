import argparse
from pathlib import Path
from .commands.build_index import build_cache
from .commands.search import search_hooks
from .commands.add import add_hook
from .commands.remove import remove_hook
from .console import error


def check_cache_exists():
    cache_file = Path.home() / ".pre-commit-hub" / "index.yaml"
    return cache_file.exists()


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Experimental pre-commit package manager."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser(
        "build-index", help="(Re)build the index of pre-commit hooks."
    )

    search_parser = subparsers.add_parser("search", help="Search for pre-commit hooks")
    search_parser.add_argument("query", help="Search query")

    add_parser = subparsers.add_parser(
        "add", help="Add a pre-commit hook to the config"
    )
    add_parser.add_argument("hook_name", help="Hook name to add")
    add_parser.add_argument(
        "-f",
        "--config-file",
        default=".pre-commit-config.yaml",
        help="Path to the config file (default: .pre-commit-config.yaml)",
    )

    remove_parser = subparsers.add_parser(
        "remove", help="Remove a pre-commit hook from the config"
    )
    remove_parser.add_argument("hook_id", help="Hook ID to remove")
    remove_parser.add_argument(
        "-f",
        "--config-file",
        default=".pre-commit-config.yaml",
        help="Path to the config file (default: .pre-commit-config.yaml)",
    )

    return parser


def main() -> int:
    parser = setup_parser()
    args = parser.parse_args()

    if args.command == "build-index":
        return build_cache()

    if not check_cache_exists():
        error("Cache does not exist. Please run 'build-index' first.")
        return 1

    if args.command == "search":
        return search_hooks(args.query)
    elif args.command == "add":
        return add_hook(args.hook_name, args.config_file)
    elif args.command == "remove":
        return remove_hook(args.hook_id, args.config_file)
    elif args.command is None:
        parser.print_help()
        return 1
    else:
        error(f"Unknown command: {args.command}")
        return 1
