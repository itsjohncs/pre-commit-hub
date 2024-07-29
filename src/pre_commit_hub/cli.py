import argparse
import os
from pathlib import Path
from .commands.build_index import build_cache
from .commands.search import search_hooks
from .commands.add import add_hook
from .commands.remove import remove_hook
from .console import error, warning


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

    add_parser = subparsers.add_parser("add", help="Add pre-commit hooks to the config")
    add_parser.add_argument("hook_ids", nargs="+", help="Hook IDs to add")
    add_parser.add_argument(
        "-f",
        "--config-file",
        help="Path to the config file (default: .pre-commit-config.yaml)",
    )

    remove_parser = subparsers.add_parser(
        "remove", help="Remove pre-commit hooks from the config"
    )
    remove_parser.add_argument("hook_ids", nargs="+", help="Hook IDs to remove")
    remove_parser.add_argument(
        "-f",
        "--config-file",
        help="Path to the config file (default: .pre-commit-config.yaml)",
    )

    return parser


def main() -> int:
    parser = setup_parser()
    args = parser.parse_args()

    if not os.environ.get("GITHUB_TOKEN"):
        warning("No `GITHUB_TOKEN` in env. GitHub API rate limits may be very low.")

    if args.command == "build-index":
        return build_cache()

    if not check_cache_exists():
        error("Cache does not exist. Please run 'build-index' first.")
        return 1

    if args.command == "search":
        return search_hooks(args.query)
    elif args.command == "add":
        return max(add_hook(hook_id, args.config_file) for hook_id in args.hook_ids)
    elif args.command == "remove":
        return max(remove_hook(hook_id, args.config_file) for hook_id in args.hook_ids)
    elif args.command is None:
        parser.print_help()
        return 1
    else:
        error(f"Unknown command: {args.command}")
        return 1
