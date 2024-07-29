from pathlib import Path
from typing import Optional


def find_config_file(config_file: Optional[str] = None) -> Path:
    """
    Find the pre-commit config file.
    If a config_file is specified, use that.
    Otherwise, look for .pre-commit-config.yaml in the git root if in a git repo,
    or in the current working directory if not.
    """
    if config_file:
        return Path(config_file)

    cwd = Path.cwd()
    git_root = find_git_root(cwd)

    if git_root:
        return git_root / ".pre-commit-config.yaml"
    else:
        return cwd / ".pre-commit-config.yaml"


def find_git_root(path: Path) -> Optional[Path]:
    """
    Find the root directory of the git repository containing the given path.
    Returns None if not in a git repository.
    """
    current = path.absolute()
    while current != current.parent:
        if (current / ".git").is_dir():
            return current
        current = current.parent
    return None
