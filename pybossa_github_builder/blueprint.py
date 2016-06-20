# -*- coding: utf8 -*-
"""Blueprint module for pybossa-github-builder."""

from flask import Blueprint
from .view import index, oauth_authorized, signout


class GitHubBlueprint(Blueprint):
    """Blueprint to support additional views.

    :param ``**kwargs``: Arbitrary keyword arguments.
    """

    def __init__(self, **kwargs):
        defaults = {'name': 'github', 'import_name': __name__}
        defaults.update(kwargs)
        super(GitHubBlueprint, self).__init__(**defaults)
        self.add_url_rule('/index', view_func=index)
