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
    parser.add_argument("--apm", help="enable Elastic APM", action="store_true")

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

    prometheus = PrometheusMiddleware()
    jwt_auth_middleware = api.JWTAuthMiddleware()

    # default Falcon middleware 
    middleware_list = [jwt_auth_middleware,prometheus]

    #TODO: externalize APM configs
    if args.apm:
        import apm_config
        apm_client = apm_config.init_apm(app_name="my_falcon_app",
            apm_server_url="https://localhost:8200",
            environment="development")

        # Falcon middleware w/ Elastic APM
        middleware_list = [jwt_auth_middleware,prometheus]

        log.info("Elastic APM enabled.")

    load_dotenv()  # take environment variables
    system_profile = os.getenv("PROFILE")
    log.info("Loaded system profile: %s" % system_profile )

    app = create_app(middleware_list)

    # loaded after Falcon app instantiation in create_app() for Prometheus
    # middleware to capture URI stats properly
    app.add_route('/metrics', prometheus)

    # TODO: externalize server IP, tcp-port
    webserver.start(port=8000, app=app)

if __name__ == '__main__':
    main()
