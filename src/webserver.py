#!/usr/bin/env python3
"""Webserver module"""

import logging
from wsgiref.simple_server import make_server

# Create a logger for this module
log = logging.getLogger(__name__)

def start(port, app):
    """ instantiate wsgi server """
    with make_server('', port, app) as httpd:
        log.info("log: %s" % log.name)
        log.info('Serving on port 8000...')
        httpd.serve_forever()
