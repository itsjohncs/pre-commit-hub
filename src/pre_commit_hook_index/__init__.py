from typing import Optional, List, Dict
import yaml
import requests
from importlib import resources
from pydantic import BaseModel
from pathlib import Path
import argparse


class Hook(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


def load_repositories():
    with resources.open_text("pre_commit_hook_index", "repositories.yaml") as f:
        return yaml.safe_load(f)


def fetch_repo_info(repo):
    url = f"https://api.github.com/repos/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def save_to_cache(data: List[Dict]):
    cache_dir = Path.home() / ".pre-commit-hook-index"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "index.yaml"

    with open(cache_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


def fetch_hooks(repo):
    url = f"https://raw.githubusercontent.com/{repo}/main/.pre-commit-hooks.yaml"
    response = requests.get(url)
    if response.status_code == 200:
        hooks = yaml.safe_load(response.text)
        return [Hook.model_validate(hook) for hook in hooks]
    return None


def setup_parser():
    parser = argparse.ArgumentParser(description="Pre-commit hook index tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser(
        "build-index", help="(Re)build the index of pre-commit hooks."
    )

    return parser


def build_cache():
    repos = load_repositories()
    cache_data = []
    for repo in repos:
        info = fetch_repo_info(repo)
        hooks = fetch_hooks(repo)
        if info and hooks:
            repo_data = {
                "repository": repo,
                "stars": info["stargazers_count"],
                "hooks": [hook.model_dump() for hook in hooks],
            }
            cache_data.append(repo_data)

    save_to_cache(cache_data)
    print("Data saved to ~/.pre-commit-hook-index/index.yaml")


def main() -> int:
    parser = setup_parser()
    args = parser.parse_args()

    if args.command == "build-index":
        build_cache()
    else:
        parser.print_help()
        return 1

    return 0
