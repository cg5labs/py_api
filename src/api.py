#!/usr/bin/env python3

import json
import jwt
import falcon
from falcon_prometheus import PrometheusMiddleware

print("encoded JWT:")
encoded_jwt = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")

print(encoded_jwt)

decoded_jwt = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
print("decoded JWT:")
print(decoded_jwt)

class QuoteResource:
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
       
class LoginResource:
    def on_post(self, req, resp):

        """Process login creds for auth"""

        try:
            # Retrieve and parse JSON data from the request body
            login_data = json.loads(req.bounded_stream.read().decode('utf-8'))
 
            # Extract task details
            login_id = login_data.get('user')
            login_auth = login_data.get('auth')
 
            if login_id is not None and login_auth is not None:
                # Process the task (in this example, just printing)
                print("Auth for - ID: %s, %s" % (login_id,login_auth))

                # TODO: query DB and decrypt password
                # verify the user creds
                if login_id == "user1":
                  if login_auth == "test123":
                    print("Auth success - ID: %s, %s" % (login_id,login_auth))
                    login_success = True
                    response_data = {
                      'message': 'auth successful'
                    }

                  else:
                    print("Auth failed - ID: %s, %s" % (login_id,login_auth))
                    login_success = False
                    response_data = {
                      'message': 'auth failed'
                    }

                else:    
                  login_success = False
                  response_data = {
                    'message': 'user unknown'
                  }

                if login_success == True:
                  resp.status = falcon.HTTP_201  # Created
                else:
                  resp.status = falcon.HTTP_401  # Unauthorized

                resp.text = json.dumps(response_data)

            else:
                # Raise an error if task_id or title is missing
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


prometheus = PrometheusMiddleware()
app = falcon.App(middleware=prometheus)
app.add_route('/metrics', prometheus)
app.add_route('/quote', QuoteResource())
app.add_route('/login', LoginResource())

