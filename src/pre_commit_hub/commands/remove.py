import yaml
from pathlib import Path
from typing import Union


def transform_yaml_remove_hook(yaml_content: str, hook_id: str) -> str:
    config = yaml.safe_load(yaml_content) or {"repos": []}
    repos = config["repos"]

    new_repos = []
    for repo in repos:
        hooks = repo.get("hooks", [])
        new_hooks = [h for h in hooks if h.get("id") != hook_id]
        if new_hooks:
            repo["hooks"] = new_hooks
            new_repos.append(repo)

    config["repos"] = new_repos

    return yaml.dump(config, default_flow_style=False, sort_keys=False)


def remove_hook_from_config(hook_id: str, config_file: Union[str, Path]) -> bool:
    config_path = Path(config_file)
    if not config_path.exists():
        print(f"Config file {config_path} not found.")
        return False

    yaml_content = config_path.read_text()
    new_yaml_content = transform_yaml_remove_hook(yaml_content, hook_id)

    if new_yaml_content != yaml_content:
        config_path.write_text(new_yaml_content)
        print(f"Removed hook '{hook_id}' from config")
        return True
    else:
        print(f"Hook '{hook_id}' not found in config")
        return False


def remove_hook(hook_id: str, config_file: str) -> int:
    return 0 if remove_hook_from_config(hook_id, config_file) else 1
