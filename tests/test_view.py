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
from factories import ProjectFactory, UserFactory


class TestView(web.Helper):

    def setUp(self):
        super(TestView, self).setUp()
        self.contents = {
            'project.json': {'name': 'project.json', 'download_url': 'url'},
            'results.html': {'name': 'results.html', 'download_url': 'url'},
            'template.html': {'name': 'template.html', 'download_url': 'url'},
            'tutorial.html': {'name': 'tutorial.html', 'download_url': 'url'},
            'thumbnail.png': {'name': 'thumbnail.png', 'download_url': 'url'},
            'long_description.md': {'name': 'long_description.md',
                                    'download_url': 'url'},
        }
        self.owner = UserFactory.create(email_addr='a@a.com')
        self.owner.set_password('1234')
        self.signin(email='a@a.com', password='1234')
        self.project = ProjectFactory.create(short_name="github_project",
                                             owner=self.owner)

    def github_login(self):
        with self.app.session_transaction() as sess:
            sess['github_token'] = 'fake_token'
        self.signin(email=self.root_addr, password=self.root_password)

    @with_context
    def test_sync_github_project(self):
        self.github_login()
        url = '/github/sync/{0}'.format(self.project.short_name)
        res = self.app.get(url)
        assert res.status_code == 200

    @with_context
    @patch('pybossa_github_builder.view.github.authorize')
    def test_login_redirects_to_full_callback_url(self, mock_authorize):
        mock_authorize.return_value = Response(302)
        redirect_uri = url_for('github.oauth_authorized', _external=True)
        self.app.get('/github/login')
        mock_authorize.assert_called_with(redirect_uri=redirect_uri)

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
