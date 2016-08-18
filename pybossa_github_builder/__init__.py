# -*- coding: utf8 -*-
"""
pybossa-github-builder
-------------

A PyBossa plugin for creating projects directly from GitHub repositories.
"""

import os
import json
from flask import current_app as app
from flask.ext.plugins import Plugin
from .extensions import github

__plugin__ = "PyBossaGitHubBuilder"
__version__ = json.load(open(os.path.join(os.path.dirname(__file__),
                                          'info.json')))['version']

REQUIRED_SETTINGS = ('GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET')


class PyBossaGitHubBuilder(Plugin):
    """PyBossa GitHub Builder plugin class."""

    def setup(self):
        """Setup the plugin."""
        try:
            for setting in REQUIRED_SETTINGS:
                app.config[setting]
            github.init_app(app)
        except Exception as inst:  # pragma: no cover
            print type(inst)
            print inst.args
            print inst
            msg = "pybossa-github-builder disabled"
            print msg
            log_message = '{0}: {1}'.format(msg, str(inst))
            app.logger.info(log_message)
            return
        self.setup_blueprint()

    def setup_blueprint(self):
        """Setup blueprint."""
        from .view import blueprint
        app.register_blueprint(blueprint, url_prefix="/github")
