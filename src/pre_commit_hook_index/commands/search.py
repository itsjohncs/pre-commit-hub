from typing import Tuple, cast
import yaml
from pathlib import Path
from thefuzz import fuzz, process
from .build_index import build_cache
from ..models import SearchIndex


def search_hooks(query: str):
    cache_file = Path.home() / ".pre-commit-hook-index" / "index.yaml"
    if not cache_file.exists():
        print("Cache file does not exist. Building cache...")
        build_cache()
        print("Cache built. Proceeding with search.")

    with open(cache_file, "r") as f:
        data = yaml.safe_load(f)
        search_index = SearchIndex.model_validate(data)

    all_hooks = []
    for repo_data in search_index.repositories:
        repo = repo_data.repository
        for hook in repo_data.hooks:
            all_hooks.append(
                {
                    "repo": repo,
                    "hook_id": hook.id,
                    "hook_name": hook.name,
                    "hook_description": hook.description or "",
                }
            )

    # Perform the fuzzy search
    results = process.extract(query, all_hooks, scorer=fuzz.partial_token_sort_ratio)

    if not results:
        print(f"No results found for query: {query}")
    else:
        for hook, score in cast(list[Tuple[dict, int]], results):
            print(f"Match score: {score}")
            print(f"Repository: {hook['repo']}")
            print(f"Hook ID: {hook['hook_id']}")
            print(f"Hook Name: {hook['hook_name']}")
            print(f"Description: {hook['hook_description']}")
            print("---")
