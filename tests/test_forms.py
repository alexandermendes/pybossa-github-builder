# -*- coding: utf8 -*-

from default import Test, with_context
from nose.tools import raises
from wtforms import ValidationError
from pybossa_github_builder.forms import GitHubURLForm, GitHubProjectForm
from pybossa_github_builder.forms import GitHubURLValidator, JSONValidator


class TestValidator(Test):

    def setUp(self):
        super(TestValidator, self).setUp()
        with self.flask_app.app_context():
            self.create()

    @raises(ValidationError)
    def test_github_repo_validator(self):
        with self.flask_app.test_request_context('/'):
            f = GitHubURLForm()
            f.github_url.data = 'http://www.example.com'
            u = GitHubURLValidator()
            u.__call__(f, f.github_url)

    @raises(ValidationError)
    def test_json_validator(self):
        with self.flask_app.test_request_context('/'):
            f = GitHubURLForm()
            f.github_url.data = '{'
            u = JSONValidator()
            u.__call__(f, f.github_url)


class TestForms(Test):

    def setUp(self):
        super(TestForms, self).setUp()
        self.form_data = {}

    @with_context
    def test_github_url_form_with_valid_fields(self):
        f = GitHubURLForm(github_url='https://www.github.com/PyBossa/pybossa')
        assert f.validate(), f.errors

    @with_context
    def test_github_project_form_with_valid_fields(self):
        f = GitHubProjectForm(name='name', short_name='short_name',
                              additional_properties="{}", category_id=0,
                              tutorial='', task_presenter='', results='',
                              thumbnail='', long_description='')
        f.category_id.choices = [(0, '')]
        f.tutorial.choices = [('', 'None')]
        f.task_presenter.choices = [('', 'None')]
        f.results.choices = [('', 'None')]
        f.thumbnail.choices = [('', 'None')]
        f.long_description.choices = [('', 'None')]
        assert f.validate(), f.errors
