# -*- coding: utf8 -*-

import os
import json
import jsonschema
from default import Test, with_context
from nose.tools import assert_raises
import pybossa_github_builder
from pybossa_github_builder.github_repo import GitHubRepo, GitHubURLError
from mock import MagicMock, patch


class TestGitHubRepo(Test):

    def setUp(self):
        super(TestGitHubRepo, self).setUp()
        self.gh_repo = GitHubRepo('http://www.github.com/me/repo')
        self.api_contents = [[self.create_api_item('project.json', 'file'),
                              self.create_api_item('img', 'dir')],
                             [self.create_api_item('thumbnail.png', 'file')]]

    def create_api_item(self, path, typ, **kwargs):
        return dict({'path': path, 'download_url': 'u', 'type': typ}, **kwargs)

    def test_initialisation_with_valid_urls(self):
        urls = ['github.com/me/repo',
                'http://www.github.com/me/repo',
                'https://github.com/me/repo.git',
                'git://github.com/me/repo.git#v0.1.0',
                'git@github.com:me/repo.git']
        for url in urls:
            github_repo = GitHubRepo(url)
            assert github_repo.user == 'me'
            assert github_repo.repo == 'repo'

    def test_initialisation_with_invalid_urls(self):
        urls = ['github.com/me',
                'http://www.example.com/me/repo',
                'example.com/me/repo.git',
                'git://github.com/repo.git#v0.1.0']
        for url in urls:
            assert_raises(GitHubURLError, GitHubRepo, url)

    @patch('pybossa_github_builder.github_repo.github')
    def test_contents_loaded(self, client):
        client.get.side_effect = (self.api_contents[0], self.api_contents[1])
        contents = self.gh_repo.load_contents()
        expected = {self.api_contents[0][0]['path']: self.api_contents[0][0],
                    self.api_contents[1][0]['path']: self.api_contents[1][0]}
        assert self.gh_repo.contents == expected

    @patch('pybossa_github_builder.github_repo.github')
    def test_file_downloaded(self, client):
        mock_response = MagicMock(content=True)
        client.get.return_value = mock_response
        self.gh_repo.contents = {'project.json': {'download_url': 'test.com'}}
        downloaded_file = self.gh_repo.download_file('project.json')
        assert downloaded_file == True
        assert client.get.called_with('test.com')
