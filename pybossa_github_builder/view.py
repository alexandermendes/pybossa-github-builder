# -*- coding: utf8 -*-
"""View module for pybossa-github-builder."""

import json
import time
import uuid
import StringIO
import sqlalchemy
from functools import wraps
from flask import current_app as app
from flask import render_template, redirect, session, flash, url_for, request
from flask import Blueprint, abort
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext
from flask.ext.github import GitHubError
from pybossa.auth import ensure_authorized_to
from pybossa.model.project import Project
from pybossa.cache import categories as cached_cat
from pybossa.cache import projects as cached_projects
from pybossa.core import project_repo, auditlog_repo, uploader
from pybossa.auditlogger import AuditLogger
from . import github
from .forms import GitHubProjectForm, GitHubURLForm
from .github_repo import GitHubRepo


blueprint = Blueprint('github', __name__, template_folder='templates')
auditlogger = AuditLogger(auditlog_repo, caller='web')


def github_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if token_getter() is None:
            return redirect(url_for('.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@github.access_token_getter
def token_getter():
    return session.get('github_token')


@blueprint.route('/login')
def login():
    """Login to GitHub."""
    redirect_uri = url_for('.oauth_authorized', _external=True,
                           next=request.args.get('next'))
    return github.authorize(redirect_uri=redirect_uri)


@blueprint.route('/oauth-authorized')
@github.authorized_handler
def oauth_authorized(oauth_token):
    """Authorize GitHub login."""
    next_url = request.args.get('next') or url_for('home.home')
    if oauth_token is None:
        flash("GitHub authorization failed", "danger")
        return redirect(url_for('home.home'))
    session['github_token'] = oauth_token
    return redirect(next_url)


@blueprint.route('/sync/<short_name>', methods=['GET', 'POST'])
@login_required
@github_login_required
def sync(short_name):
    """Sync a project with a GitHub repo."""
    project = project_repo.get_by_shortname(short_name)
    if not project:  # pragma: no cover
        abort(404)
    ensure_authorized_to('update', project)
    form = GitHubURLForm(request.form)
    if request.method == 'POST' and form.validate():
        github_url = form.github_url.data
        return redirect(url_for('.import_repo', github_url=github_url,
                                short_name=project.short_name))
    elif request.method == 'POST':  # pragma: no cover
        flash(gettext('Please correct the errors'), 'error')
    return render_template('projects/github/sync.html', form=form,
                           project=project)


def _populate_form(form, repo_contents, project_json):
    """Populate the import form using data from a GitHub repo."""
    def add_choices(field, exts, default):
        field.choices = [('', 'None')]
        valid = {k: v for k, v in repo_contents.items()
                 if any(k.endswith(ext) for ext in exts)}
        for k, v in valid.items():
            field.choices.append((v['download_url'], k))
            if v['name'] == default:
                field.default = v['download_url']

    categories = cached_cat.get_all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    form.category_id.default = project_json.get('category_id',
                                                categories[0].id)
    add_choices(form.tutorial, ['.html'], 'tutorial.html')
    add_choices(form.task_presenter, ['.html'], 'template.html')
    add_choices(form.results, ['.html'], 'results.html')
    add_choices(form.long_description, ['.md'], 'long_description.md')
    add_choices(form.thumbnail, ['.png', '.jpg', 'jpeg'], 'thumbnail.png')


@blueprint.route('/import/<short_name>', methods=['GET', 'POST'])
@github_login_required
@login_required
def import_repo(short_name):
    """Import a project from a GitHub repo."""
    project = project_repo.get_by_shortname(short_name)
    if not project:  # pragma: no cover
        abort(404)
    ensure_authorized_to('update', project)

    github_url = request.args.get('github_url')
    gh_repo = GitHubRepo(github_url)
    try:
        gh_repo.load_contents()
    except GitHubError as e:  # pragma: no cover
        flash(str(e), 'error')
        return redirect(url_for('.sync', short_name=project.short_name))
    if not gh_repo.validate():  # pragma: no cover
        flash('That is not a valid PyBossa project', 'error')
        return redirect(url_for('.sync', short_name=project.short_name))

    form = GitHubProjectForm(request.form)
    project_json = gh_repo.get_project_json()
    _populate_form(form, gh_repo.contents, project_json)
    categories = project_repo.get_all_categories()

    if request.method == 'POST' and form.validate():
        info = json.loads(form.additional_properties.data)
        original_short_name = project_json['short_name']
        if form.tutorial.data:
            resp = github.get(form.tutorial.data)
            info['tutorial'] = resp.content.replace(original_short_name,
                                                    project.short_name)
        if form.task_presenter.data:
            resp = github.get(form.task_presenter.data)
            info['task_presenter'] = resp.content.replace(original_short_name,
                                                          project.short_name)
        if form.results.data:
            resp = github.get(form.results.data)
            info['results'] = resp.content.replace(original_short_name,
                                                   project.short_name)
        long_description = None
        if form.long_description.data:
            resp = github.get(form.long_description.data)
            long_description = resp.content

        old_project = Project(**project.dictize())
        project.description = form.description.data
        project.long_description = long_description
        project.category_id = form.category_id.data
        project.webhook = form.webhook.data
        project.info = info
        print project.info

        if form.thumbnail.data:
            f = StringIO.StringIO(github.get(form.thumbnail.data).content)
            prefix = time.time()
            f.filename = "project_%s_thumbnail_%i.png" % (project.id, prefix)
            container = "user_%s" % current_user.id
            uploader.upload_file(f, container=container)
        try:
            project_repo.update(project)
        except sqlalchemy.exc.DataError as e:  # pragma: no cover
            flash('''DataError: {0} <br><br>Please check the files being
                  imported from GitHub'''.format(e.orig), 'danger')
            return redirect(url_for('.sync', short_name=project.short_name))
        auditlogger.add_log_entry(old_project, project, current_user)
        cached_cat.reset()
        cached_projects.get_project(project.short_name)
        flash(gettext('Project updated!'), 'success')
        return redirect(url_for('project.details',
                                short_name=project.short_name))

    elif request.method == 'POST':  # pragma: no cover
        flash(gettext('Please correct the errors'), 'error')

    else:
        form.process()
        form.description.data = project_json.get('description', '')
        form.webhook.data = project_json.get('webhook', '')

        reserved_keys = ['name', 'short_name', 'description', 'webhook',
                         'category_id']
        for k in reserved_keys:
            project_json.pop(k, None)
        form.additional_properties.data = json.dumps(project_json)

    return render_template('projects/github/import.html', form=form,
                           github_url=github_url, project=project)
