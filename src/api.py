#!/usr/bin/env python3
"""Sample API module using JWT"""

import argparse
import datetime
import json
import logging
import os
import time
import uuid

import jwt
import falcon


from falcon_prometheus import PrometheusMiddleware
from dotenv import load_dotenv

from sql_models import User, session

class JWTAuthMiddleware:
    """ # Middleware for handling JWT """

    def process_request(self, req, resp):
        """ Check requests for JWT headers and verify them """

        # for falcon_prometheus middleware support
        req.start_time = time.time()

        # whitelist public pages
        if req.path in ['/login','/register', '/metrics', '/quote' ]:
            return

        token = req.get_header('Authorization')
        if not token:
            raise falcon.HTTPForbidden(description='Token is missing')
        try:
            # Bearer token typically has "Bearer " prefix
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            #req.context['user_name'] = data['user_name']
        except jwt.ExpiredSignatureError:
            raise falcon.HTTPForbidden(description='Token has expired')
        except jwt.InvalidTokenError:
            raise falcon.HTTPForbidden(description='Invalid token')

class Session:
    """Session objects for http session """
    def __init__(self):
        self.user_name = None
        self.user_auth = None
        self.authenticated = None
        self.sid = None
        self.token = None

    def set_user_name(self, name):
        """ Sets the user_name"""
        self.user_name = name

    def get_user_name(self):
        """ Gets the user_name"""
        return self.user_name

    def set_user_auth(self, auth):
        """ Sets the user auth credential"""
        self.user_auth = auth

    def set_authenticated(self, status):
        """ Sets the user auth status"""
        # fixme: sanity check if boolean
        self.authenticated = status

    def get_authenticated(self):
        """ Gets the user auth credential"""
        return self.authenticated

    def set_sid(self):
        """ Sets the SID"""
        self.sid = str(uuid.uuid4())

    def get_sid(self):
        """ Gets the SID"""
        return self.sid


    def set_token(self,token):
        """ Sets the JWT"""
        self.token = token

    def get_token(self):
        """ Gets the JWT"""
        return self.token


    # CREATE
    def create_user(self, user_name, user_auth):
        """ Create new user record in DB """
        new_user = User(user_name, user_auth)
        session.add(new_user)
        session.commit()
        return new_user

    def verify_creds(self):
        """ Verifies the object credentials against user records DB"""

        user = session.query(User).filter(User.user_name == self.user_name).first()

        if user.decrypted_user_auth == self.user_auth:
            self.set_authenticated(True)
        else:
            self.set_authenticated(False)

        return self.get_authenticated()

    def create_token(self, sid):
        """ Generate new JWT"""

        token = jwt.encode(
            {
                'sid': sid,
                'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30),
                #'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            JWT_SECRET_KEY,
            algorithm="HS256"
        )

        self.set_token(token)

        return token


class QuoteResource:
    """Sample API resource (public) """

    def on_get(self, req, resp):
        """Handle GET requests."""

        quote = {
            'author': 'Grace Hopper',
            'quote': (
                "I've always been more interested in "
                "the future than in the past."
            ),
        }

        resp.media = quote

class RegisterResource:
    """ API user enrolment """

    def on_post(self, req, resp):

        try:
            # Retrieve and parse JSON data from the request body
            reg_data = json.loads(req.bounded_stream.read().decode('utf-8'))

            # Extract auth details
            reg_user = reg_data.get('user')
            reg_auth = reg_data.get('auth')

            if reg_user is not None and reg_auth is not None:

                #print("Reg for - ID: %s, %s" % (reg_user,reg_auth))
                #if reg_user:
                #    reg_user_enc = encrypt_string(reg_user)
                #    reg_user_dec = decrypt_string(reg_user_enc)
                #if reg_auth:
                #    reg_auth_enc = encrypt_string(reg_auth)
                #    reg_auth_dec = decrypt_string(reg_auth_enc)

                session = Session()
                session.set_user_name(reg_user)
                session.set_user_auth(reg_auth)

                # TODO: check if user already exists in DB
                session.create_user(reg_user,reg_auth)

                response_data = {
                      'User created successfully': reg_user
                }

                resp.text = json.dumps(response_data)
                resp.status = falcon.HTTP_201  # Created
                #resp.media = {'token': token}

            else:
                # Raise an error if login JSON payload (user, auth) is missing
                raise ValueError("Both user and auth are required in the request JSON.")

        except json.JSONDecodeError:
            # Handle JSON decoding errors
            resp.status = falcon.HTTP_400  # Bad Request
            resp.text = json.dumps({'error': 'Invalid JSON format'})
        except ValueError as e:
            # Handle missing task_id or title
            resp.status = falcon.HTTP_400  # Bad Request
            resp.text = json.dumps({'error': str(e)})
        except Exception as e:
            # Handle other exceptions
            resp.status = falcon.HTTP_500  # Internal Server Error
            resp.text = json.dumps({'error': 'Internal Server Error'})


class ProtectedResource:
    """Sample API resource (restricted) """
    def on_get(self, req, resp):
        resp.media = {'message': 'Welcome protected'}


class LoginResource:
    """Login API"""

    def on_post(self, req, resp):
        """Login API resource.
        ---
        description: Login authentication with user auth creds
        responses:
            201:
                description: Auth successful
                schema: ApiSchema
        """

        try:
            # Retrieve and parse JSON data from the request body
            login_data = json.loads(req.bounded_stream.read().decode('utf-8'))

            # Extract auth details
            login_id = login_data.get('user')
            login_auth = login_data.get('auth')

            if login_id is not None and login_auth is not None:

                log.debug("Auth for - ID: %s, %s" % (login_id,login_auth))

                # FIXME
                session = Session()

                session.set_user_name(login_id)
                session.set_user_auth(login_auth)
                session.set_sid()
                sid = session.get_sid()
                log.info("SID %s" % sid)
                auth_status = session.verify_creds()
                if auth_status is True:
                    token = session.create_token(sid)
                    log.debug("Auth success - ID: %s, %s" % (login_id,login_auth))
                    log.debug("Auth success - %s " % (session.get_user_name()))

                    resp.set_header('Authorization', 'Bearer %s' % token )
                    resp.status = falcon.HTTP_201  # Created
                    response_data = {
                      'message': 'auth successful',
                      'token' : token
                    }
                else:
                    log.debug("Auth failed - ID: %s, %s" % (login_id,login_auth))
                    resp.status = falcon.HTTP_401  # Unauthorized
                    response_data = {
                      'message': 'auth failed'
                    }

                resp.text = json.dumps(response_data)

            else:
                # Raise an error if login JSON payload (user, auth) is missing
                raise ValueError("Both user and auth are required in the request JSON.")

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            resp.status = falcon.HTTP_400  # Bad Request
            resp.text = json.dumps({'error': 'Invalid JSON format'})
        except ValueError as e:
            # Handle missing task_id or title
            resp.status = falcon.HTTP_400  # Bad Request
            resp.text = json.dumps({'error': str(e)})
        except Exception as e:
            # Handle other exceptions
            resp.status = falcon.HTTP_500  # Internal Server Error
            resp.text = json.dumps({'error': 'Internal Server Error'})


# Falcon app and routes
prometheus = PrometheusMiddleware()
login_resource = LoginResource()

app = falcon.App(middleware=[JWTAuthMiddleware(),prometheus])
app.add_route('/quote', QuoteResource())
app.add_route('/login', login_resource)
app.add_route('/register', RegisterResource())
app.add_route('/protected', ProtectedResource())
app.add_route('/metrics', prometheus)


# FIXME: externalize
# Secret key to encode the JWT
JWT_SECRET_KEY = 'your_secret_key'

log = logging.getLogger(__name__)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", help="Enable debug logs", action="store_true")
    parser.add_argument("--log", help="logfile path, e.g. log/apps.log", default="log/app.log")
    parser.add_argument("-p", "--profile", help="environment profile to use, e.g. local,dev")

    args = parser.parse_args()

    # override switch to force $PROFILE
    if args.profile:
        os.environ["PROFILE"] = args.profile


    if not os.path.exists(os.path.dirname(args.log)):
        os.mkdir(os.path.dirname(args.log))

    logging.basicConfig(level="INFO" if not args.debug else "DEBUG",
      format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
      datefmt='%m-%d %H:%M',
      filename=args.log,
      filemode='w')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    load_dotenv()  # take environment variables

    system_profile = os.getenv("PROFILE")
    log.info("Loaded system profile: %s" % system_profile )

    from wsgiref.simple_server import make_server
    with make_server('', 8000, app) as httpd:
        log.info("log: %s" % log.name)
        log.info('Serving on port 8000...')
        httpd.serve_forever()
