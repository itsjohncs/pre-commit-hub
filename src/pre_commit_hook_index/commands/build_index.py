import yaml
import requests
from importlib import resources
from pathlib import Path
from ..models import Hook, Repository, SearchIndex


def load_repositories():
    with resources.open_text("pre_commit_hook_index", "repositories.yaml") as f:
        return yaml.safe_load(f)


def fetch_repo_info(repo):
    url = f"https://api.github.com/repos/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def save_to_cache(data: SearchIndex):
    cache_dir = Path.home() / ".pre-commit-hook-index"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "index.yaml"

    with open(cache_file, "w") as f:
        yaml.dump(data.model_dump(), f, default_flow_style=False)


def fetch_hooks(repo):
    url = f"https://raw.githubusercontent.com/{repo}/main/.pre-commit-hooks.yaml"
    response = requests.get(url)
    if response.status_code == 200:
        hooks = yaml.safe_load(response.text)
        return [Hook.model_validate(hook) for hook in hooks]
    return None


def build_cache():
    repos = load_repositories()
    cache_data = []
    for repo in repos:
        info = fetch_repo_info(repo)
        hooks = fetch_hooks(repo)
        if info and hooks:
            repo_data = Repository(
                repository=repo, stars=info["stargazers_count"], hooks=hooks
            )
            cache_data.append(repo_data)

    search_index = SearchIndex(repositories=cache_data)
    save_to_cache(search_index)
    print("Data saved to ~/.pre-commit-hook-index/index.yaml")
