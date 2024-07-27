import pytest
from pre_commit_hook_index.commands.add import find_hooks
from pre_commit_hook_index.models import SearchIndex, Repository, Hook


@pytest.fixture
def sample_search_index():
    return SearchIndex(
        repositories=[
            Repository(
                repository="user1/project1",
                stars=100,
                hooks=[
                    Hook(id="hook1", name="Hook 1", description="Description 1"),
                    Hook(id="hook2", name="Hook 2", description="Description 2"),
                ],
            ),
            Repository(
                repository="user2/project2",
                stars=200,
                hooks=[
                    Hook(id="hook1", name="Hook 1", description="Description 1"),
                    Hook(id="hook3", name="Hook 3", description="Description 3"),
                ],
            ),
        ]
    )


def test_find_hooks_by_id(sample_search_index):
    results = find_hooks(sample_search_index, "hook1")
    assert len(results) == 2
    assert results[0][0].id == "hook1"
    assert results[0][1].repository == "user1/project1"
    assert results[1][0].id == "hook1"
    assert results[1][1].repository == "user2/project2"


def test_find_hooks_by_project_and_id(sample_search_index):
    results = find_hooks(sample_search_index, "project1:hook1")
    assert len(results) == 1
    assert results[0][0].id == "hook1"
    assert results[0][1].repository == "user1/project1"


def test_find_hooks_by_user_project_and_id(sample_search_index):
    results = find_hooks(sample_search_index, "user2/project2:hook3")
    assert len(results) == 1
    assert results[0][0].id == "hook3"
    assert results[0][1].repository == "user2/project2"


def test_find_hooks_no_match(sample_search_index):
    results = find_hooks(sample_search_index, "nonexistent")
    assert len(results) == 0


def test_find_hooks_invalid_query(sample_search_index):
    results = find_hooks(sample_search_index, "invalid:query:format")
    assert len(results) == 0
