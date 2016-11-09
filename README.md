# pybossa-github-builder

[![Build Status](https://travis-ci.org/alexandermendes/pybossa-github-builder.svg?branch=master)]
(https://travis-ci.org/alexandermendes/pybossa-github-builder)
[![Coverage Status](https://coveralls.io/repos/github/alexandermendes/pybossa-github-builder/badge.svg?branch=master)]
(https://coveralls.io/github/alexandermendes/pybossa-github-builder?branch=master)

A PyBossa plugin for creating projects via the web interface by directly importing content from GitHub repositories. Essentially, 
the plugin enables the creation of fully configured projects in just a few clicks, which could be especially useful for users who are 
not comfortable with command line tools, such as [pbs](https://github.com/PyBossa/pbs). It also means that templates for the tutorial 
and results pages can be loaded via the web interface.


## Installation and configuration

Run the following commands (modified according to your PyBossa installation directory):

```
source /home/pybossa/pybossa/env/bin/activate
cd /home/pybossa/pybossa/pybossa/plugins
git clone https://github.com/alexandermendes/pybossa-github-builder
pip install -r pybossa-github-builder/requirements.txt
mv pybossa-github-builder/pybossa_github_builder pybossa_github_builder
rm -r pybossa-github-builder
```

Now visit [https://github.com/settings/applications](https://github.com/settings/applications) to register a new application (i.e. your 
PyBossa application), entering `http://{your-pybossa-domain}/github/oauth-authorized`  in the **Authorization Callback URL** field.

Once the application is registered copy your **Client ID** and **Client Secret** into your main PyBossa configuration file, as follows:

``` Python
GITHUB_CLIENT_ID = 'your-client-id'
GITHUB_CLIENT_SECRET = 'your-client-secret'
```

The plugin will be available after you restart the server.


## Theme integration

The plugin provides [templates](pybossa_github_builder/templates) that match the PyBossa default theme. To use templates that match 
your PyBossa custom theme just copy the [/templates/projects/github](pybossa_github_builder/templates/projects/github) directory into your 
theme's [/templates/projects](https://github.com/PyBossa/pybossa-default-theme/tree/master/templates/projects) directory and modify.

You might also want to add a link to
[tasks.html](https://github.com/PyBossa/pybossa-default-theme/tree/master/templates/projects/tasks.html):

```HTML+Django
{% if 'pybossa_github_builder' in plugins %}
    <a href="{{ url_for('github.sync', short_name=project.short_name) }}">Sync with GitHub</a>
{% endif %}
```


## Usage

Create a project then visit:

```
http://{pybossa-site-url}/github/sync/{project-short-name}
```

Enter a valid GitHub URL. A GitHub URL is considered valid if it points to a GitHub repository containing a **project.json** file that 
validates against [project_schema.json](pybossa_github_builder/project_schema.json). Check the schema file for further details of the 
available keys.

If a valid repository is found you will be taken to a form containing the details found in **project.json** and fields to select the 
project's task presenter, tutorial, results, long description, thumbnail and so on.

Note that the project's short name, as it's written throughout the GitHub repository, will be replaced in the project's task presenter, 
tutorial and results (if any of these files are imported) with the short name of the actual project.

### Example

See [project-convert-a-card](https://github.com/LibCrowds/project-convert-a-card) for an example of a project that can be loaded using 
this plugin.
