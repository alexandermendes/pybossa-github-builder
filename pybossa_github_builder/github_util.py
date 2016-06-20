# -*- coding: utf8 -*-
"""GitHub utility module for pybossa-github-builder."""

import re
from flask.ext.github import GitHubError
from . import github

def extract_github_user_and_repo(url):
    """Extract the user and repo from a GitHub URL and return."""
    pattern = r'github\.[^\/:]+[\/|:]([^\/]+)\/([^\/|\s|\)]+)[.git|\/]?'
    match = re.search(pattern, url)
    if not match:
        return None
    parts = match.group(0).split('/')
    (user, repo) = parts[1], parts[2]
    url = 'https://api.github.com/repos/{0}/{1}'.format(user, repo)
    try:
        resp = github.get(url)
    except GitHubError:
        return None
    return (user, repo)