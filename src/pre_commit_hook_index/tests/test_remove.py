import yaml
from pre_commit_hook_index.commands.remove import transform_yaml_remove_hook


def test_transform_yaml_remove_hook_empty():
    yaml_content = ""
    result = transform_yaml_remove_hook(yaml_content, "test-hook")
    assert yaml.safe_load(result) == {"repos": []}


def test_transform_yaml_remove_hook_no_match():
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
    result = transform_yaml_remove_hook(yaml_content, "test-hook")
    assert result == yaml_content


def test_transform_yaml_remove_hook_single_hook():
    yaml_content = yaml.dump(
        {
            "repos": [
                {
                    "repo": "https://github.com/user/repo",
                    "hooks": [{"id": "test-hook"}],
                }
            ]
        }
    )
    result = transform_yaml_remove_hook(yaml_content, "test-hook")
    expected = {"repos": []}
    assert yaml.safe_load(result) == expected


def test_transform_yaml_remove_hook_multiple_hooks():
    yaml_content = yaml.dump(
        {
            "repos": [
                {
                    "repo": "https://github.com/user/repo",
                    "hooks": [{"id": "test-hook"}, {"id": "other-hook"}],
                }
            ]
        }
    )
    result = transform_yaml_remove_hook(yaml_content, "test-hook")
    expected = {
        "repos": [
            {
                "repo": "https://github.com/user/repo",
                "hooks": [{"id": "other-hook"}],
            }
        ]
    }
    assert yaml.safe_load(result) == expected


def test_transform_yaml_remove_hook_multiple_repos():
    yaml_content = yaml.dump(
        {
            "repos": [
                {
                    "repo": "https://github.com/user/repo1",
                    "hooks": [{"id": "test-hook"}, {"id": "other-hook"}],
                },
                {
                    "repo": "https://github.com/user/repo2",
                    "hooks": [{"id": "test-hook"}],
                },
            ]
        }
    )
    result = transform_yaml_remove_hook(yaml_content, "test-hook")
    expected = {
        "repos": [
            {
                "repo": "https://github.com/user/repo1",
                "hooks": [{"id": "other-hook"}],
            }
        ]
    }
    assert yaml.safe_load(result) == expected
