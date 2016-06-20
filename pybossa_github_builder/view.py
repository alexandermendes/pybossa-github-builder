# -*- coding: utf8 -*-
"""View module for pybossa-github-builder."""

from flask import current_app as app
from flask import render_template, redirect, session, flash, url_for, request
from flask import Blueprint
from flask.ext.babel import gettext
from pybossa.auth import ensure_authorized_to
from pybossa.model.project import Project
from . import github
from .forms import GitHubProjectForm

blueprint = Blueprint('github', __name__, template_folder='templates')


@github.access_token_getter
def token_getter():
    return session.get('github_token')


@blueprint.route('/login')
def login():
    """Login to GitHub."""
    redirect_uri = url_for('.oauth_authorized', next=request.args.get('next'))
    return github.authorize(redirect_uri=redirect_uri)


@blueprint.route('/oauth-authorized')
@github.authorized_handler
def oauth_authorized(oauth_token):
    """Authorize GitHub login."""
    if oauth_token is None:
        flash("GitHub authorization failed.", "danger")
        return redirect(url_for('project.new'))
    session['github_token'] = oauth_token
    return redirect(url_for('.new_project'))


@blueprint.route('/new_project', methods=['GET', 'POST'])
def new_project():
    """Create a new project based on a GitHub repo."""
    ensure_authorized_to('create', Project)
    form = GitHubProjectForm(request.form)
    if request.method == 'POST' and form.validate():
        pass
    elif request.method == 'POST':
        flash(gettext('Please correct the errors'), 'error')
    return render_template('/new_github_project.html', form=form)
