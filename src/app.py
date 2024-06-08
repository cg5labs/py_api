#!/usr/bin/env python3
"""Sample API module using JWT"""

import argparse
import logging
import os

import falcon

from falcon_prometheus import PrometheusMiddleware

from dotenv import load_dotenv

import api


# Falcon app and routes
prometheus = PrometheusMiddleware()
login_resource = api.LoginResource()

app = falcon.App(middleware=[api.JWTAuthMiddleware(),prometheus])
app.add_route('/quote', api.QuoteResource())
app.add_route('/login', login_resource)
app.add_route('/register', api.RegisterResource())
app.add_route('/protected', api.ProtectedResource())
app.add_route('/metrics', prometheus)


def configure_logging(log_path,log_level):
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_path)

    # Set levels for handlers
    console_handler.setLevel(log_level)
    file_handler.setLevel(log_level)

    # Create formatters and add them to handlers
    log_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(log_fmt)
    file_handler.setFormatter(log_fmt)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", help="Enable debug logs", action="store_true")
    parser.add_argument("--log", help="logfile path, e.g. log/apps.log", default="log/app.log")
    parser.add_argument("-p", "--profile", help="environment profile to use, e.g. local, default")

    args = parser.parse_args()

    # override switch to force $PROFILE
    if args.profile:
        os.environ["PROFILE"] = args.profile


    if not os.path.exists(os.path.dirname(args.log)):
        os.mkdir(os.path.dirname(args.log))

    # Log configs for console and file logging
    log = logging.getLogger(__name__)
    log_level = "INFO" if not args.debug else "DEBUG"
    configure_logging(args.log, log_level)

    load_dotenv()  # take environment variables

    system_profile = os.getenv("PROFILE")
    log.info("Loaded system profile: %s" % system_profile )

    from wsgiref.simple_server import make_server
    with make_server('', 8000, app) as httpd:
        log.info("log: %s" % log.name)
        log.info('Serving on port 8000...')
        httpd.serve_forever()

if __name__ == '__main__':
    main()
