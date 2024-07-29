import os
from github import Github

github_token = os.environ.get("GITHUB_TOKEN")
g = Github(github_token)
