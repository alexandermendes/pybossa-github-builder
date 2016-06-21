# -*- coding: utf8 -*-
"""GitHub utility module for pybossa-github-builder."""

import re
import json
import os
import jsonschema
from flask.ext.github import GitHubError
from . import github


BASE_URL = 'https://api.github.com'


def _get_contents(user, repo):
    """Return the contents of a GitHub repo."""
    url = '{0}/repos/{1}/{2}/contents'.format(BASE_URL, user, repo)
    try:
        return github.get(url)
    except GitHubError:
        return None


def _get_raw_file(user, repo, fn):
    """Return a raw file from a GitHub repo."""
    url = '{0}/repos/{1}/{2}/contents/{3}'.format(BASE_URL, user, repo, fn)
    try:
        resp = github.get(url)
    except GitHubError:
        return None
    raw_url = resp.get('download_url')
    try:
        return github.get(raw_url).text
    except GitHubError:
        return None


def _extract_repo_details(url):
    """Extract the user and repo from a GitHub URL."""
    pattern = r'github\.[^\/:]+[\/|:]([^\/]+)\/([^\/|\s|\)]+)[.git|\/]?'
    match = re.search(pattern, url)
    if not match:
        return None
    parts = match.group(0).split('/')
    return parts[1], parts[2]


def validate(url):
    """Validate PyBossa project GitHub repo."""
    details = _extract_repo_details(url)
    if not details:
        return False
    project_json = _get_raw_file(details[0], details[1], 'project.json')
    if not project_json:
        return False
    path = os.path.join(os.path.dirname(__file__), 'project_schema.json')
    project_schema = json.load(open(path))
    try:
        jsonschema.validate(json.loads(project_json), project_schema)
    except jsonschema.exceptions.ValidationError as e:
        return False
    return True


def get_project_files(url):
    """Get the raw files associated with a PyBossa project."""
    (user, repo) = _extract_repo_details(url)
    contents = _get_contents(user, repo)
    accepted = ['project.json', 'long_description.md', 'template.html',
                'results.html', 'tutorial.html']
    proj_files = [f for f in contents if f['name'] in accepted]
    return {f['name']: github.get(f['download_url']).text for f in proj_files}
