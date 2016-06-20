# -*- coding: utf8 -*-
"""View module for pybossa-github-builder."""

from flask import current_app as app
from flask import render_template, Blueprint, request, session, flash, url_for
from . import github

blueprint = Blueprint('github', __name__)


@blueprint.route('/login')
def login():
    """Login to GitHub."""
    return github.authorize()


@blueprint.route('/oauth-authorized')
@github.authorized_handler
def oauth_authorized(oauth_token):
    """Authorize GitHub login."""
    if oauth_token is None:
        flash("Authorization failed.", "danger")
        return redirect(next_url)
    session['github_token'] = oauth_token
    return redirect('.new_project')
