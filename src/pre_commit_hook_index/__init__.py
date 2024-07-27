from typing import Optional, List, Dict
import yaml
import requests
from importlib import resources
from pydantic import BaseModel
from pathlib import Path


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
    return 0
