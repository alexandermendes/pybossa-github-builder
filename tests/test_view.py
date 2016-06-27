# -*- coding: utf8 -*-

import json
import urllib
from functools import wraps
from mock import patch, MagicMock, PropertyMock
from flask import Response, session, url_for, redirect
from default import flask_app, with_context
from helper import web
from pybossa_github_builder.view import _populate_form
from pybossa_github_builder.forms import GitHubProjectForm


class TestView(web.Helper):

    def setUp(self):
        super(TestView, self).setUp()
        with self.flask_app.app_context():
            self.create()
        self.contents = {
            'project.json': {'name': 'project.json', 'download_url': 'url'},
            'results.html': {'name': 'results.html', 'download_url': 'url'},
            'template.html': {'name': 'template.html', 'download_url': 'url'},
            'tutorial.html': {'name': 'tutorial.html', 'download_url': 'url'},
            'thumbnail.png': {'name': 'thumbnail.png', 'download_url': 'url'},
            'long_description.md': {'name': 'long_description.md',
                                    'download_url': 'url'},
        }

    def github_login(self):
        with self.app.session_transaction() as sess:
            sess['github_token'] = 'fake_token'
        self.signin(email=self.root_addr, password=self.root_password)

    def test_get_new_github_project(self):
        self.github_login()
        res = self.app.get('/github/project/new')
        assert res.status_code == 200

    @with_context
    @patch('pybossa_github_builder.view.github.authorize')
    def test_github_login_specifies_full_url_as_callback(self, mock_authorize):
        mock_authorize.return_value = Response(302)
        redirect_uri = url_for('github.oauth_authorized', _external=True)
        self.app.get('/github/login')
        mock_authorize.assert_called_with(redirect_uri=redirect_uri)

    @with_context
    @patch('pybossa_github_builder.view.redirect', wraps=redirect)
    def test_new_redirects_to_import_with_valid_github_url(self, redirect):
        self.github_login()
        data = dict(github_url='https://github.com/me/repo')
        encoded_data = urllib.urlencode(data)
        url = '/github/project/import_repo?{0}'.format(encoded_data)
        self.app.post('/github/project/new', data=data)
        redirect.assert_called_with(url)

    @patch('pybossa_github_builder.view.GitHubRepo')
    @patch('pybossa_github_builder.view.json')
    def test_valid_project_imported(self, mock_json, mock_gh_repo):
        mock_gh_repo = MagicMock()
        mock_json = MagicMock()
        self.github_login()
        args = urllib.urlencode(dict(github_url='https://github.com/me/repo'))
        url = '/github/project/import_repo?{0}'.format(args)
        res = self.app.get(url)
        assert res.status_code == 200, res.data

    @with_context
    def test_populate_form(self):
        f = GitHubProjectForm()
        _populate_form(f, self.contents, self.contents['project.json'])
        html_choices = [('', 'None'), ('url', 'results.html'),
                        ('url', 'template.html'), ('url', 'tutorial.html')]
        assert f.tutorial.choices == html_choices
        assert f.task_presenter.choices == html_choices
        assert f.results.choices == html_choices
        assert f.thumbnail.choices == [('', 'None'), ('url', 'thumbnail.png')]
        assert f.long_description.choices == [('', 'None'),
                                              ('url', 'long_description.md')]
