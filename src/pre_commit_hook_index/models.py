from typing import List
from pydantic import BaseModel


class Hook(BaseModel):
    id: str
    name: str
    description: str | None = None


class Repository(BaseModel):
    repository: str
    stars: int
    hooks: List[Hook]


class SearchIndex(BaseModel):
    repositories: List[Repository]
