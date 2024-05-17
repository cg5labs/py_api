#!/usr/bin/env python3

import jwt
import falcon
from falcon_prometheus import PrometheusMiddleware

print("encoded JWT:")
encoded_jwt = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")

print(encoded_jwt)

decoded_jwt = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
print("decoded JWT:")
print(decoded_jwt)

# sample.py

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


prometheus = PrometheusMiddleware()
app = falcon.App(middleware=prometheus)

#api = falcon.API(middleware=prometheus)
app.add_route('/metrics', prometheus)
app.add_route('/quote', QuoteResource())

