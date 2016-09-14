# -*- coding: utf8 -*-
"""GitHubRepo module for pybossa-github-builder."""

import re
import json
import os
import jsonschema
from . import github


class InvalidPybossaProjectError(Exception):
    """Raied if a repo is not for a vaild PyBossa project."""

    def __init__(self, msg=None):
        if msg is None:
            msg = 'that is not a valid PyBossa project'
        super(Exception, self).__init__(msg)


class GitHubURLError(Exception):
    """Raised if a GitHub URL is invalid."""

    def __init__(self):
        super(Exception, self).__init__('that is not a valid GitHub URL')


class GitHubRepo(object):
    """A class for interacting with a GitHub repo for a PyBossa project."""

    root_endpoint = 'https://api.github.com'

    def __init__(self, url):
        self.user, self.repo = self.get_user_and_repo(url)
        self.load_contents()
        self.validate()

    def get_user_and_repo(self, url):
        """Return the GitHub user and repo."""
        patn = r'github\.[^\/:]+[\/|:]([^\/]+)\/([^\/|\s|\)]+)[.git|\/]?'
        match = re.search(patn, url)
        if not match:
            raise GitHubURLError()
        parts = re.split('/|:', match.group(0))
        user = parts[1]
        repo = parts[2].split('.git')[0]
        return user, repo

    def get_project_json(self):
        """Download and return the project details."""
        url = self.contents['project.json']['download_url']
        resp = github.get(url)
        try:
            project_json = json.loads(resp.content)
        except ValueError as e:
            raise InvalidPybossaProjectError(str(e))
        return project_json

    def load_contents(self):
        """Load the contents of a GitHub repo."""
        base_url = '{0}/repos/{1}/{2}/contents'.format(self.root_endpoint,
                                                       self.user, self.repo)
        self.contents = {}

        def get_dir_contents(path=''):
            url = '{0}/{1}'.format(base_url, path)
            resp = github.get(url)
            for item in resp:
                if item['type'] == 'dir':
                    get_dir_contents(item['path'])
                elif item['type'] == 'file':
                    self.contents[item['path']] = item
        get_dir_contents()

    def validate(self):
        """Validate a PyBossa project GitHub repo."""
        if 'project.json' not in self.contents:  # pragma: no cover
            raise InvalidPybossaProjectError('no project.json file found')
        project_json = self.get_project_json()
        path = os.path.join(os.path.dirname(__file__), 'project_schema.json')
        project_schema = json.load(open(path))
        try:
            jsonschema.validate(project_json, project_schema)
        except jsonschema.exceptions.ValidationError as e:  # pragma: no cover
            err_msg = 'project.json does not validate against the schema'
            raise InvalidPybossaProjectError(err_msg)
