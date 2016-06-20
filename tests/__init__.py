# -*- coding: utf8 -*-

import sys
import os
import pybossa_github_builder as plugin
from mock import patch


# Use the PyBossa test suite
sys.path.append(os.path.abspath("./pybossa/test"))

from default import with_context
from helper import web
from pybossa.core import result_repo


def setUpPackage():
    """Setup the plugin."""
    from default import flask_app
    with flask_app.app_context():
        plugin_dir = os.path.dirname(plugin.__file__)
        plugin.PyBossaGitHubBuilder(plugin_dir).setup()


class TestPlugin(web.Helper):
	pass