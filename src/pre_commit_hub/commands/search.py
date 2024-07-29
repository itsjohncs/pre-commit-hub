from typing import Tuple, cast
import yaml
from pathlib import Path
from thefuzz import fuzz, process
from ..models import SearchIndex


def load_cache() -> SearchIndex:
    cache_file = Path.home() / ".pre-commit-hub" / "index.yaml"
    with open(cache_file, "r") as f:
        data = yaml.safe_load(f)
        return SearchIndex.model_validate(data)


def search_hooks(query: str) -> int:
    search_index = load_cache()

    documents = [
        {"repository": repo.repository, "stars": repo.stars, **hook.model_dump()}
        for repo in search_index.repositories
        for hook in repo.hooks
    ]

    results = process.extract(query, documents, scorer=fuzz.partial_token_sort_ratio)

    if not results:
        print(f"No results found for query: {query}")
        return 1
    else:
        for hook, score in cast(list[Tuple[dict, int]], results):
            print(f"Match score: {score}")
            print(f"Repository: {hook['repository']}")
            print(f"Stars: {hook['stars']}")
            print(f"Hook ID: {hook['id']}")
            print(f"Hook Name: {hook['name']}")
            print(f"Description: {hook['description']}")
            print("---")
        return 0
