# -*- coding: utf8 -*-
"""View module for pybossa-github-builder."""

import json
from flask import current_app as app
from flask import render_template, redirect, session, flash, url_for, request
from flask import Blueprint
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext
from pybossa.auth import ensure_authorized_to
from pybossa.model.project import Project
from pybossa.cache import categories as cached_cat
from pybossa.core import project_repo, auditlog_repo
from pybossa.auditlogger import AuditLogger
from . import github
from .forms import GitHubProjectForm
from .github_util import get_project_files


blueprint = Blueprint('github', __name__, template_folder='templates')
auditlogger = AuditLogger(auditlog_repo, caller='web')


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
    next_url = request.args.get('next') or url_for('.new_project')
    if oauth_token is None:
        flash("GitHub authorization failed.", "danger")
        return redirect(url_for('project.new'))
    session['github_token'] = oauth_token
    return redirect(next_url)


@blueprint.route('/new_project', methods=['GET', 'POST'])
@login_required
def new_project():
    """Create a new project based on a GitHub repo."""
    ensure_authorized_to('create', Project)
    form = GitHubProjectForm(request.form)

    if request.method == 'POST' and form.validate():
        project_files = get_project_files(form.github_url.data)
        project_json = json.loads(project_files['project.json'])
        name = project_json['name']
        short_name = project_json['short_name']
        description = project_json['description']
        long_description = project_files.get('long_description.md',
                                             description)

        info = {'github_url': form.github_url.data}
        template = project_files.get('template.html')
        results = project_files.get('results.html')
        tutorial = project_files.get('tutorial.html')
        if template:
            info['task_presenter'] = template.replace(short_name,
                                                      form.short_name.data)
        if results:
            info['results'] = results.replace(short_name, form.short_name.data)
        if tutorial:
            info['tutorial'] = tutorial.replace(short_name,
                                                form.short_name.data)

        default_category = cached_cat.get_all()[0]
        project = Project(name=form.name.data,
                          short_name=form.short_name.data,
                          description=description,
                          long_description=long_description,
                          owner_id=current_user.id,
                          category_id=default_category.id,
                          info=info)
        project_repo.save(project)
        flash(gettext('Project created!'), 'success')
        auditlogger.add_log_entry(None, project, current_user)
        return redirect(url_for('project.update',
                                short_name=project.short_name))

    elif request.method == 'POST':
        flash(gettext('Please correct the errors'), 'error')
    return render_template('/projects/new_github_project.html', form=form)


@blueprint.route('/sync', methods=['GET', 'POST'])
@login_required
def sync():
    pass


