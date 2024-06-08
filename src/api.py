#!/usr/bin/env python3
"""Sample API module using JWT"""

import datetime
import json
import logging
import time
import uuid

import jwt
import falcon

import db
from sql_models import User

# Create a logger for this module
log = logging.getLogger(__name__)

# Secret key to encode the JWT
JWT_SECRET_KEY = str(uuid.uuid4())

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

class APISession:
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
        db.sql_session.add(new_user)
        db.sql_session.commit()
        return new_user

    def verify_creds(self):
        """ Verifies the object credentials against user records DB"""

        log.info("verify_creds")

        #user = db.sql_session.query(sql_models.User).filter(sql_models.User.user_name == self.user_name).first()
        user = db.sql_session.query(User).filter(User.user_name == self.user_name).first()

        if user.decrypted_user_auth == self.user_auth:
            self.set_authenticated(True)
        else:
            self.set_authenticated(False)

        return self.get_authenticated()

    def create_token(self, sid):
        """ Generate new JWT"""

        log.info("create_token")
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
        """ Handle GET requests. """

        quote = {
            'author': 'Grace Hopper',
            'quote': (
                "I've always been more interested in "
                "the future than in the past."
            ),
        }

        log.info("%s %s %s %s" % (req.method,req.path,resp.status,resp.text))
        resp.media = quote

class RegisterResource:
    """ API user enrolment """

    def on_post(self, req, resp):
        """ Handle POST requests. """

        try:
            # Retrieve and parse JSON data from the request body
            reg_data = json.loads(req.bounded_stream.read().decode('utf-8'))

            # Extract auth details
            reg_user = reg_data.get('user')
            reg_auth = reg_data.get('auth')

            if reg_user is not None and reg_auth is not None:

                session = APISession()
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

                log.info("%s %s %s %s" % (req.method,req.path,resp.status,resp.text))

            else:
                # Raise an error if login JSON payload (user, auth) is missing
                raise ValueError("Both user and auth are required in the request JSON.")

        except json.JSONDecodeError:
            # Handle JSON decoding errors
            log.error('Invalid JSON format')
            resp.status = falcon.HTTP_400  # Bad Request
            resp.text = json.dumps({'error': 'Invalid JSON format'})
        except ValueError as e:
            log.error(e)
            # Handle missing task_id or title
            resp.status = falcon.HTTP_400  # Bad Request
            resp.text = json.dumps({'error': str(e)})
        except Exception as e:
            # Handle other exceptions
            log.error(e)
            resp.status = falcon.HTTP_500  # Internal Server Error
            resp.text = json.dumps({'error': 'Internal Server Error'})


class ProtectedResource:
    """ Sample API resource (restricted) """
    def on_get(self, req, resp):
        """ Handle GET requests. """
        log.info("%s %s %s %s" % (req.method,req.path,resp.status,resp.text))
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
                session = APISession()

                session.set_user_name(login_id)
                session.set_user_auth(login_auth)
                session.set_sid()
                sid = session.get_sid()
                log.info("SID %s" % sid)
                auth_status = session.verify_creds()
                if auth_status is True:
                    token = session.create_token(sid)
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

                log.info("%s %s %s %s" % (req.method,req.path,resp.status,resp.text))
                resp.text = json.dumps(response_data)

            else:
                # Raise an error if login JSON payload (user, auth) is missing
                raise ValueError("Both user and auth are required in the request JSON.")

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            log.error(e)
            resp.status = falcon.HTTP_400  # Bad Request
            resp.text = json.dumps({'error': 'Invalid JSON format'})
        except ValueError as e:
            # Handle missing task_id or title
            log.error(e)
            resp.status = falcon.HTTP_400  # Bad Request
            resp.text = json.dumps({'error': str(e)})
        except Exception as e:
            # Handle other exceptions
            log.error(e)
            resp.status = falcon.HTTP_500  # Internal Server Error
            resp.text = json.dumps({'error': 'Internal Server Error'} )
