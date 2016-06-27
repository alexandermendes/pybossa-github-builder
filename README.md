# pybossa-github-builder

[![Build Status](https://travis-ci.org/alexandermendes/pybossa-github-builder.svg?branch=master)]
(https://travis-ci.org/alexandermendes/pybossa-github-builder)
[![Coverage Status](https://coveralls.io/repos/alexandermendes/pybossa-github-builder/badge.svg)]
(https://coveralls.io/github/alexandermendes/pybossa-github-builder?branch=master)

A PyBossa plugin for creating projects via the web interface by directly
importing content from GitHub repositories. Essentially, the plugin enables the
creation of fully configured projects in just a few clicks, which could be
especially useful for users who are not comfortable with command line tools,
such as [pbs](https://github.com/PyBossa/pbs). It also means that templates for
the tutorial and results pages can be loaded via the web interface.


## Installation

Run the following commands (modified according to your PyBossa installation directory):

```
source /home/pybossa/pybossa/env/bin/activate
cd /home/pybossa/pybossa/pybossa/plugins
git clone https://github.com/alexandermendes/pybossa-github-builder
pip install -r pybossa-github-builder/requirements.txt
mv pybossa-github-builder/pybossa_github_builder pybossa_github_builder
rm -r pybossa-github-builder
```

The plugin will be available after you restart the server.


## Configuration

Go to [https://github.com/settings/applications](https://github.com/settings/applications)
to register a new application, then add the following settings to your main PyBossa
configuration file.

``` Python
GITHUB_CLIENT_ID = 'your-client-id'
GITHUB_CLIENT_SECRET = 'your-client-secret'
```


## Theme integration

The plugin provides [templates](pybossa_github_builder/templates) that match
the [pybossa-default-theme](https://github.com/PyBossa/pybossa-default-theme).
To use templates that matche your PyBossa custom theme just copy the
[github](pybossa_github_builder/templates/projects/github)
directory into your theme's
[/templates/projects](https://github.com/PyBossa/pybossa-default-theme/tree/master/templates/projects)
directory and modify.

You might want to then add something like the following snippet to
[new.html](https://github.com/PyBossa/pybossa-default-theme/tree/master/templates/projects/new.html):

```HTML+Django
{% if 'pybossa_github_builder' in plugins %}
    <a href="{{ url_for('github.new') }}" class="btn btn-primary">Import From GitHub</a>
{% endif %}
```


## Usage

To create a project, search for a GitHub repository using the form available at:

```
http://{pybossa-site-url}/github/project/new
```

A GitHub URL is considered valid if it points to a GitHub repository containing
a **project.json** file that validates against
[project_schema.json](pybossa_github_builder/project_schema.json). Check the
schema file for further details of the available keys.

If a valid repository is found you will be taken to a form containing the details
found in **project.json** and fields to select the project's task presenter,
tutorial, results, long description and thumbnail. On submitting this form a
new project will be created.

Note that the project's short name, as it's written throughout the repository,
will be replaced in the project's task presenter, tutorial and results
(if any of these files are imported) with the short name entered in the form.
