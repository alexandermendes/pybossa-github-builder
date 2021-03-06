# -*- coding: utf8 -*-
"""Forms module for pybossa-github-builder."""

import re
import json
from wtforms import validators, ValidationError
from wtforms import SelectField, TextAreaField, TextField
from flask_wtf import Form
from flask_wtf.html5 import URLField
from .github_repo import GitHubRepo, GitHubURLError
from pybossa.forms import validator as pb_validator


class GitHubURLValidator(object):
    """Validator to check for a valid GitHub repository."""

    def __init__(self, message=None):
        if not message:  # pragma: no cover
            message = 'Not a valid GitHub repository.'
        self.message = message

    def __call__(self, form, field):
        patn = r'github\.[^\/:]+[\/|:]([^\/]+)\/([^\/|\s|\)]+)[.git|\/]?'
        match = re.search(patn, field.data)
        if not match:
            raise ValidationError(self.message)


class JSONValidator(object):
    """Validator that checks for valid JSON."""

    def __init__(self):
        self.message = 'Invalid JSON.'

    def __call__(self, _form, field):
        try:
            json.loads(field.data)
        except (ValueError, TypeError):
            raise ValidationError(self.message)


class GitHubURLForm(Form):
    """Form for creating a new project from GitHub."""
    github_url = URLField('GitHub URL', [validators.Required(),
                                         GitHubURLValidator()])


class GitHubProjectForm(Form):
    """Form for creating a new project from GitHub."""
    description = TextAreaField('Description', [validators.Length(max=255)])
    task_presenter = SelectField('Task Presenter', coerce=str)
    tutorial = SelectField('Tutorial', coerce=str)
    results = SelectField('Results', coerce=str)
    thumbnail = SelectField('Thumbnail', coerce=str)
    webhook = TextField('Webhook', [pb_validator.Webhook()])
    category_id = SelectField('Category', coerce=int)
    additional_properties = TextAreaField('Additional Properties',
                                          validators=[JSONValidator()])
    # Override to allow non default choice
    long_description = SelectField('Long Description', choices=[('', 'None')])
