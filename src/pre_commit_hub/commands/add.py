import yaml
from pathlib import Path
from typing import Union, Optional, List, Tuple
from ..models import SearchIndex, Hook, Repository
from .search import load_cache
from ._github import g
from ..console import error


def find_hooks(search_index: SearchIndex, query: str) -> List[Tuple[Hook, Repository]]:
    parts = query.split(":")
    hook_id = parts[-1]

    def match_condition(repo: Repository, hook: Hook) -> bool:
        if len(parts) == 1:
            return True
        elif len(parts) == 2:
            project = parts[0]
            return repo.repository.endswith(f"/{project}") or repo.repository == project
        elif len(parts) == 3:
            user, project = parts[:2]
            return repo.repository == f"{user}/{project}"
        return False

    return [
        (hook, repo)
        for repo in search_index.repositories
        for hook in repo.hooks
        if hook.id == hook_id and match_condition(repo, hook)
    ]


def find_hook(
    query: str, search_index: SearchIndex
) -> Optional[Tuple[Hook, Repository]]:
    matches = find_hooks(search_index, query)
    if len(matches) == 0:
        error(f"No hooks found matching '{query}'")
        return None
    elif len(matches) > 1:
        error(f"Multiple hooks found matching '{query}':")
        for hook, repo in matches:
            print(f"  {repo.repository}:{hook.id}")
        return None
    return matches[0]


def add_hook_to_config(
    hook: Hook, repository: Repository, config_file: Union[str, Path]
) -> bool:
    config_path = Path(config_file)
    if not config_path.exists():
        create = input(f"No {config_path} file found. Create one? (y/n): ")
        if create.lower() != "y":
            print("Aborting.")
            return False

    yaml_content = config_path.read_text() if config_path.exists() else ""

    if hook_exists_in_config(yaml_content, hook, repository.repository):
        print(f"Hook '{hook.id}' from '{repository.repository}' is already in config")
        return False

    latest_rev = get_latest_revision(repository.repository)
    modified_yaml = modify_yaml_config(
        yaml_content, hook, repository.repository, latest_rev
    )

    config_path.write_text(modified_yaml)
    print(f"Added hook '{hook.id}' from '{repository.repository}' to config")
    return True


def hook_exists_in_config(yaml_content: str, hook: Hook, repository: str) -> bool:
    config = yaml.safe_load(yaml_content)
    repo_url = f"https://github.com/{repository}"

    for repo in config.get("repos", []):
        if repo["repo"] == repo_url:
            if any(h["id"] == hook.id for h in repo.get("hooks", [])):
                return True
    return False


def add_hook(query: str, config_file: str) -> int:
    search_index = load_cache()
    result = find_hook(query, search_index)
    if result:
        hook, repository = result
        return 0 if add_hook_to_config(hook, repository, config_file) else 1
    else:
        return 1


def modify_yaml_config(
    yaml_content: str, hook: Hook, repository: str, latest_rev: str
) -> str:
    config = yaml.safe_load(yaml_content) if yaml_content else {"repos": []}

    repo_url = f"https://github.com/{repository}"
    repo_entry = next(
        (repo for repo in config["repos"] if repo["repo"] == repo_url), None
    )

    if repo_entry is None:
        repo_entry = {"repo": repo_url, "hooks": []}
        config["repos"].append(repo_entry)

    # Check if the hook already exists
    existing_hook = next((h for h in repo_entry["hooks"] if h["id"] == hook.id), None)
    if existing_hook is None:
        new_hook = {"id": hook.id}
        if latest_rev:
            new_hook["rev"] = latest_rev
        repo_entry["hooks"].append(new_hook)

    return yaml.dump(config, default_flow_style=False, sort_keys=False)


def get_latest_revision(repository: str) -> str:
    repo = g.get_repo(repository)
    tags = list(repo.get_tags())
    if tags:
        first_tag = tags[0]

        same_commit_tags = [
            tag for tag in tags if tag.commit.sha == first_tag.commit.sha
        ]

        # Try to find a tag with a period in its name. This is the same criteria
        # pre-commit uses [^1].
        # [^1]: https://github.com/pre-commit/pre-commit/blob/d46423ffe14a37a06a0bcb6fe1b8294a27b6c289/pre_commit/git.py#L233
        for tag in same_commit_tags:
            if "." in tag.name:
                return tag.name

        return first_tag.name
    else:
        return repo.get_commits()[0].sha
