import yaml
from pathlib import Path
from typing import Union, Optional, List, Tuple
from ..models import SearchIndex, Hook, Repository
from .search import load_cache


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
        print(f"No hooks found matching '{query}'")
        return None
    elif len(matches) > 1:
        print(f"Multiple hooks found matching '{query}':")
        for hook, repo in matches:
            print(f"  {repo.repository}:{hook.id}")
        return None
    return matches[0]


def add_hook_to_config(
    hook: Hook, repository: Repository, config_file: Union[str, Path]
):
    config_path = Path(config_file)
    if not config_path.exists():
        create = input(f"No {config_path} file found. Create one? (y/n): ")
        if create.lower() != "y":
            print("Aborting.")
            return

    yaml_content = config_path.read_text() if config_path.exists() else ""
    modified_yaml = modify_yaml_config(yaml_content, hook, repository)

    if modified_yaml != yaml_content:
        config_path.write_text(modified_yaml)
        print(f"Added hook '{hook.id}' from '{repository.repository}' to config")
    else:
        print(f"Hook '{hook.id}' from '{repository.repository}' is already in config")


def add_hook(query: str, config_file: Union[str, Path]):
    search_index = load_cache()
    result = find_hook(query, search_index)
    if result:
        hook, repository = result
        add_hook_to_config(hook, repository, config_file)


def modify_yaml_config(yaml_content: str, hook: Hook, repository: Repository) -> str:
    config = yaml.safe_load(yaml_content) if yaml_content else {"repos": []}

    # Check if the repository is already in the config
    repo_url = f"https://github.com/{repository.repository}"
    repo_entry = next(
        (repo for repo in config["repos"] if repo["repo"] == repo_url), None
    )

    if repo_entry is None:
        repo_entry = {"repo": repo_url, "hooks": []}
        config["repos"].append(repo_entry)

    # Check if the hook is already in the repository entry
    if not any(h["id"] == hook.id for h in repo_entry["hooks"]):
        repo_entry["hooks"].append({"id": hook.id})
        return yaml.dump(config, default_flow_style=False)

    return yaml_content
