from typing import Optional
import yaml
import requests
from importlib import resources
from pydantic import BaseModel


class Hook(BaseModel):
    id: str
    name: str
    description: Optional[str]


def load_repositories():
    with resources.open_text("pre_commit_hook_index", "repositories.yaml") as f:
        return yaml.safe_load(f)


def fetch_repo_info(repo):
    url = f"https://api.github.com/repos/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def fetch_hooks(repo):
    url = f"https://raw.githubusercontent.com/{repo}/main/.pre-commit-hooks.yaml"
    response = requests.get(url)
    if response.status_code == 200:
        hooks = yaml.safe_load(response.text)
        return [
            Hook(
                id=hook["id"],
                name=hook.get("name", hook["id"]),
                description=hook.get("description", "No description provided"),
            )
            for hook in hooks
            if "id" in hook
        ]
    return None


def main() -> int:
    repos = load_repositories()
    for repo in repos:
        info = fetch_repo_info(repo)
        hooks = fetch_hooks(repo)
        if info and hooks:
            print(f"Repository: {repo}")
            print(f"Stars: {info['stargazers_count']}")
            print("Hooks:")
            for hook in hooks:
                print(f"  - ID: {hook.id}")
                print(f"    Name: {hook.name}")
                print(f"    Description: {hook.description}")
            print("---")
    return 0
