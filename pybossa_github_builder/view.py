# -*- coding: utf8 -*-
"""View module for pybossa-github-builder."""

import json
import time
import StringIO
import sqlalchemy
from functools import wraps
from flask import current_app as app
from flask import render_template, redirect, session, flash, url_for, request
from flask import Blueprint
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext
from pybossa.auth import ensure_authorized_to
from pybossa.model.project import Project
from pybossa.cache import categories as cached_cat
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
    next_url = request.args.get('next') or url_for('.new')
    if oauth_token is None:
        flash("GitHub authorization failed.", "danger")
        return redirect(url_for('project.new'))
    session['github_token'] = oauth_token
    return redirect(next_url)


@blueprint.route('/project/new', methods=['GET', 'POST'])
@login_required
@github_login_required
def new():
    """Search for a GitHub repo by URL."""
    ensure_authorized_to('create', Project)
    form = GitHubURLForm(request.form)
    if request.method == 'POST' and form.validate():
        github_url = form.github_url.data
        return redirect(url_for('.import_repo', github_url=github_url))
    elif request.method == 'POST':  # pragma: no cover
        flash(gettext('Please correct the errors'), 'error')
    return render_template('/projects/github/new.html', form=form)


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


@blueprint.route('/project/import_repo', methods=['GET', 'POST'])
@github_login_required
@login_required
def import_repo():
    """Create a new project based on a GitHub repo."""
    ensure_authorized_to('create', Project)
    form = GitHubProjectForm(request.form)
    github_url = request.args.get('github_url')
    if not github_url:  # pragma: no cover
        return redirect(url_for('.new'))

    gh_repo = GitHubRepo(github_url)
    gh_repo.load_contents()
    if not gh_repo.validate():  # pragma: no cover
        flash('Not a valid PyBossa project.', 'error')
        return redirect(url_for('.new'))

    details = gh_repo.get_project_json()
    _populate_form(form, gh_repo.contents, details)
    categories = project_repo.get_all_categories()

    if request.method == 'POST' and form.validate():
        info = json.loads(form.additional_properties.data)
        if form.tutorial.data:
            resp = github.get(form.tutorial.data)
            info['tutorial'] = resp.content.replace(details['short_name'],
                                                    form.short_name.data)
        if form.task_presenter.data:
            resp = github.get(form.task_presenter.data)
            info['task_presenter'] = resp.content.replace(details['short_name'],
                                                          form.short_name.data)
        if form.results.data:
            resp = github.get(form.results.data)
            info['results'] = resp.content.replace(details['short_name'],
                                                   form.short_name.data)
        long_description = None
        if form.long_description.data:
            resp = github.get(form.long_description.data)
            long_description = resp.content
        project = Project(name=form.name.data,
                          short_name=form.short_name.data,
                          description=form.description.data,
                          long_description=long_description,
                          owner_id=current_user.id,
                          category_id=form.category_id.data,
                          webhook=form.webhook.data,
                          info=info)
        if form.thumbnail.data:
            f = StringIO.StringIO(github.get(form.thumbnail.data).content)
            prefix = time.time()
            f.filename = "project_%s_thumbnail_%i.png" % (project.id, prefix)
            container = "user_%s" % current_user.id
            uploader.upload_file(f, container=container)
        try:
            project_repo.save(project)
        except sqlalchemy.exc.DataError as e:  # pragma: no cover
            flash('''DataError: {0} <br><br>Please check the files being
                  imported from GitHub'''.format(e.orig), 'danger')
            return redirect(url_for('.new'))
        flash(gettext('Project created!'), 'success')
        auditlogger.add_log_entry(project, None, current_user)
        return redirect(url_for('project.update',
                                short_name=project.short_name))

    elif request.method == 'POST':  # pragma: no cover
        flash(gettext('Please correct the errors'), 'error')

    else:
        form.process()
        form.name.data = details.get('name', '')
        form.short_name.data = details.get('short_name', '')
        form.description.data = details.get('description', '')
        form.webhook.data = details.get('webhook', '')

        reserved_keys = ['name', 'short_name', 'description', 'webhook',
                         'category_id']
        for k in reserved_keys:
            details.pop(k, None)
        form.additional_properties.data = json.dumps(details)

    return render_template('/projects/github/import_repo.html', form=form,
                           github_url=github_url)
