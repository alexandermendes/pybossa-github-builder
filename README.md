# pybossa-github-builder

[![Build Status](https://travis-ci.org/alexandermendes/pybossa-github-builder.svg?branch=master)]
(https://travis-ci.org/alexandermendes/pybossa-github-builder)
[![Coverage Status](https://coveralls.io/repos/alexandermendes/pybossa-github-builder/badge.svg)]
(https://coveralls.io/github/alexandermendes/pybossa-github-builder?branch=master)

A PyBossa plugin for creating projects directly from GitHub repositories.


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
to register new application, then add the following settings to your main PyBossa
configuration file.

``` Python
GITHUB_CLIENT_ID = 'your-client-id'
GITHUB_CLIENT_SECRET = 'your-client-secret'
```


## Theme integration

The plugin provides a single template,
[new_github_project.html](pybossa_github_builder/templates/projects/new_github_project.html),
which matches the [pybossa-default-theme](https://github.com/PyBossa/pybossa-default-theme).
To use a template that matches your PyBossa custom theme just add a file called
**new_github_project.html** to the root of your themes's
[/templates/projects](https://github.com/PyBossa/pybossa-default-theme/tree/master/templates/projects)
folder.

You might want to then add something like the following snippet to
[new.html](https://github.com/PyBossa/pybossa-default-theme/tree/master/templates/projects/new.html):

```HTML+Django
{% if 'pybossa_github_builder' in plugins %}
    <a href="{{ url_for('github.new_project') }}" class="btn btn-primary">Create From GitHub</a>
{% endif %}
```


## Usage

To create a project from a GitHub repository visit:

```
http://{pybossa-site-url}/github/new_project
```

Enter the project's name, short name and the URL of a GitHub repository. If the
URL is valid (that is, the repository contains a **project.json** file), then
a project will be created. See [project_schema.json](pybossa_github_builder/project_schema.json)
for the recognised required and optional keys.

If any of the following files are found in the root directory of the repository
they are used to update the project accordingly:

- template.html
- tutorial.html
- results.html
- long_description.md
