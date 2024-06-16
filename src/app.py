#!/usr/bin/env python3
"""Sample API module using JWT"""

import argparse
import logging
import os

import falcon

from falcon_prometheus import PrometheusMiddleware

from dotenv import load_dotenv

import api
import webserver

def create_app(middleware_list=None):

    if not middleware_list:
    # Falcon app and routes
        prometheus = PrometheusMiddleware()
        jwt_auth_middleware = api.JWTAuthMiddleware()
        middleware_list = [jwt_auth_middleware, prometheus]

    login_resource = api.LoginResource()
    register_resource = api.RegisterResource()
    protected_resource = api.ProtectedResource()

    app = falcon.App(middleware=middleware_list)

    app.add_route('/quote', api.QuoteResource())
    app.add_route('/login', login_resource)
    app.add_route('/register', register_resource)
    app.add_route('/protected', protected_resource)

    return app

def configure_logging(log_path,log_level):
    """ Log handler and appenders config """

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

def configure_argparse():
    """ CLI parameters config """
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", help="Enable debug logs", action="store_true")
    parser.add_argument("-p", "--port", help="WSGI server tcp-port to use", default="8000")
    parser.add_argument("--log", help="logfile path, e.g. log/apps.log", default="log/app.log")
    parser.add_argument("--profile", help="environment profile to use, e.g. local, default")
    parser.add_argument("--apm", help="enable Elastic APM", action="store_true")
    parser.add_argument("--apm_url", help="URL of the Elastic APM server",
        default="http://localhost:8200")

    return parser

def main():
    """ main """

    parser = configure_argparse()
    args = parser.parse_args()

    if not os.path.exists(os.path.dirname(args.log)):
        os.mkdir(os.path.dirname(args.log))

    # Log configs for console and file logging
    log = logging.getLogger(__name__)
    log_level = "INFO" if not args.debug else "DEBUG"
    configure_logging(args.log, log_level)

    # override switch to force $PROFILE
    if args.profile:
        log.info("--profile override set: %s." % args.profile)
        os.environ["PROFILE"] = args.profile

    # default Falcon middleware
    prometheus = PrometheusMiddleware()
    jwt_auth_middleware = api.JWTAuthMiddleware()
    middleware_list = [jwt_auth_middleware,prometheus]

    if args.apm:
        from falcon_elastic_apm import ElasticApmMiddleware
        #import apm_config
        elastic_apm_middleware = ElasticApmMiddleware(
            service_name='falcon_apm', 
            server_url=args.apm_url
        )

        # Falcon middleware w/ Elastic APM
        middleware_list = [jwt_auth_middleware,prometheus,elastic_apm_middleware]

        log.info("Elastic APM enabled.")
        log.info("Elastic APM server URL: %s" % args.apm_url)

    load_dotenv()  # take environment variables
    system_profile = os.getenv("PROFILE")
    log.info("Loaded system profile: %s" % system_profile )

    log.info("Instantiating Falcon application.")
    app = create_app(middleware_list)

    # loaded after Falcon app instantiation in create_app() for Prometheus
    # middleware to capture URI stats properly
    app.add_route('/metrics', prometheus)

    log.info("Launching WSGI server for Falcon application.")
    webserver.start(port=int(args.port), app=app)

if __name__ == '__main__':
    main()
