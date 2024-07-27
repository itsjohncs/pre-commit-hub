import yaml
from importlib import resources
from pathlib import Path
from ..models import Hook, Repository, SearchIndex
from github import Github
import os

# Initialize Github client
github_token = os.environ.get("GITHUB_TOKEN")
g = Github(github_token)


def load_repositories():
    with resources.open_text("pre_commit_hub", "repositories.yaml") as f:
        return yaml.safe_load(f)


def fetch_repo_info(repo):
    try:
        github_repo = g.get_repo(repo)
        return {
            "stargazers_count": github_repo.stargazers_count,
            "description": github_repo.description,
            "homepage": github_repo.homepage,
        }
    except Exception as e:
        raise RuntimeError(f"Got error fetching repo info for {repo}") from e


def save_to_cache(data: SearchIndex):
    cache_dir = Path.home() / ".pre-commit-hub"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "index.yaml"

    with open(cache_file, "w") as f:
        yaml.dump(data.model_dump(), f, default_flow_style=False)


def fetch_hooks(repo):
    try:
        github_repo = g.get_repo(repo)
        contents = github_repo.get_contents(".pre-commit-hooks.yaml")
        if isinstance(contents, list):
            content = contents[0]
        else:
            content = contents
        hooks = yaml.safe_load(content.decoded_content)
        return [Hook.model_validate(hook) for hook in hooks]
    except Exception as e:
        raise RuntimeError(f"Got error fetching hooks in repo {repo}") from e


def build_cache() -> int:
    repos = load_repositories()
    cache_data = []
    for repo in repos:
        info = fetch_repo_info(repo)
        if not info:
            continue

        hooks = fetch_hooks(repo)
        if not hooks:
            continue

        repo_data = Repository(
            repository=repo, stars=info["stargazers_count"], hooks=hooks
        )
        cache_data.append(repo_data)

    search_index = SearchIndex(repositories=cache_data)
    save_to_cache(search_index)
    print("Data saved to ~/.pre-commit-hub/index.yaml")
    return 0
