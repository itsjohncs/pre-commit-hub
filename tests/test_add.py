import pytest
import yaml
from pre_commit_hub.commands.add import find_hooks, modify_yaml_config
from pre_commit_hub.models import SearchIndex, Repository, Hook


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


def test_modify_yaml_config_empty():
    yaml_content = ""
    hook = Hook(id="test-hook", name="Test Hook", description="A test hook")
    repository = Repository(repository="user/repo", stars=100, hooks=[hook])

    result = modify_yaml_config(
        yaml_content, hook, repository.repository, "abcdef1234567890"
    )
    expected = {
        "repos": [
            {
                "repo": "https://github.com/user/repo",
                "hooks": [{"id": "test-hook", "rev": "abcdef1234567890"}],
            }
        ]
    }

    assert yaml.safe_load(result) == expected


def test_modify_yaml_config_existing_repo():
    yaml_content = yaml.dump(
        {
            "repos": [
                {
                    "repo": "https://github.com/user/repo",
                    "hooks": [{"id": "existing-hook"}],
                }
            ]
        }
    )
    hook = Hook(id="test-hook", name="Test Hook", description="A test hook")
    repository = Repository(repository="user/repo", stars=100, hooks=[hook])

    result = modify_yaml_config(yaml_content, hook, repository.repository, "v1.0.0")
    expected = {
        "repos": [
            {
                "repo": "https://github.com/user/repo",
                "hooks": [
                    {"id": "existing-hook"},
                    {"id": "test-hook", "rev": "v1.0.0"},
                ],
            }
        ]
    }
    assert yaml.safe_load(result) == expected


def test_modify_yaml_config_existing_hook():
    yaml_content = yaml.dump(
        {
            "repos": [
                {"repo": "https://github.com/user/repo", "hooks": [{"id": "test-hook"}]}
            ]
        }
    )
    hook = Hook(id="test-hook", name="Test Hook", description="A test hook")
    repository = Repository(repository="user/repo", stars=100, hooks=[hook])

    result = modify_yaml_config(yaml_content, hook, repository.repository, "v1.0.0")

    assert yaml.safe_load(result) == yaml.safe_load(yaml_content)


def test_modify_yaml_config_new_repo():
    yaml_content = yaml.dump(
        {
            "repos": [
                {
                    "repo": "https://github.com/other/repo",
                    "hooks": [{"id": "other-hook"}],
                }
            ]
        }
    )
    hook = Hook(id="test-hook", name="Test Hook", description="A test hook")
    repository = Repository(repository="user/repo", stars=100, hooks=[hook])

    result = modify_yaml_config(
        yaml_content, hook, repository.repository, "abcdef1234567890"
    )
    expected = {
        "repos": [
            {
                "repo": "https://github.com/other/repo",
                "hooks": [{"id": "other-hook"}],
            },
            {
                "repo": "https://github.com/user/repo",
                "hooks": [{"id": "test-hook", "rev": "abcdef1234567890"}],
            },
        ]
    }

    assert yaml.safe_load(result) == expected
