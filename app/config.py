import os
from flask import Blueprint, send_from_directory, make_response
from app.util import gzipped


# Define the blueprint: 'config'
config = Blueprint('config', __name__)


"""
Set Headers for static content: enable compression and vary-encoding
"""


# Template for serving static resources
def _response_path(static_path):
    return make_response(send_from_directory(os.path.join(config.root_path, 'static'), static_path))


# Send favicon image from static folder
@config.route('/favicon.ico')
@gzipped
def favicon():
    return _response_path('images/favicon-16x16.png')


# Optimize static content delivery for CSS & JS & Images


""" CSS """


@config.route('/static/css/sea-green.min.css')
@gzipped
def css_seagreen():
    return _response_path('css/sea-green.min.css')


@config.route('/static/css/fresh-bootstrap-table.min.css')
@gzipped
def css_bootstrap_table():
    return _response_path('css/fresh-bootstrap-table.min.css')


@config.route('/static/assets/css/material-kit.css')
@gzipped
def css_material_kit():
    return _response_path('assets/css/material-kit.css')


""" JS """


@config.route('/static/bootstrap/js/bootstrap-table.min.js')
@gzipped
def js_bootstrap_table():
    return _response_path('bootstrap/js/bootstrap-table.min.js')


@config.route('/static/js/highlights/highlight.min.js')
@gzipped
def js_highlight():
    return _response_path('js/highlights/highlight.min.js')


@config.route('/static/js/stats/stat.min.js')
@gzipped
def js_stats():
    return _response_path('js/stats/stat.min.js')


@config.route('/static/js/fixtures/fixture.min.js')
@gzipped
def js_fixtures():
    return _response_path('js/fixtures/fixture.min.js')
