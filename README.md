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
