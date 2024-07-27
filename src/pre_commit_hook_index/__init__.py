import yaml
import requests
from importlib import resources


def load_repositories():
    with resources.open_text("pre_commit_hook_index", "repositories.yaml") as f:
        return yaml.safe_load(f)


def fetch_repo_info(repo):
    url = f"https://api.github.com/repos/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def main() -> int:
    repos = load_repositories()
    for repo in repos:
        info = fetch_repo_info(repo)
        if info:
            print(f"Repository: {repo}")
            print(f"Stars: {info['stargazers_count']}")
            print("---")
    return 0
