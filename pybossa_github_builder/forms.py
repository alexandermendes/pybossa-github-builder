# -*- coding: utf8 -*-
"""Forms module for pybossa-github-builder."""

import re
from pybossa.forms.forms import ProjectForm
from wtforms import validators, ValidationError
from flask_wtf.html5 import URLField
from .github_util import extract_github_user_and_repo


class GitHubRepo(object):
    """Validator to check for a valid GitHub repository."""

    def __init__(self, message=None):
        if not message:  # pragma: no cover
            message = 'Not a valid GitHub repository.'
        self.message = message
        self.patn = r'github\.[^\/:]+[\/|:]([^\/]+)\/([^\/|\s|\)]+)[.git|\/]?'

    def __call__(self, form, field):
        if not extract_github_user_and_repo(field.data):
            raise ValidationError(self.message)


class GitHubProjectForm(ProjectForm):
    """Form for creating a new project from GitHub."""
    github_url = URLField('GitHub URL', [validators.Required(), GitHubRepo()])