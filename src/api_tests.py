#!/usr/bin/env python3
""" pytest unit tests """

import os
import json
import pytest

import falcon

from falcon import testing
from dotenv import load_dotenv

import app

load_dotenv()  # take environment variables

# Fixture to set up the test client
@pytest.fixture
def client():
    """ Init test client instance"""

    return testing.TestClient(app.app)

# Fixture to get a valid token
@pytest.fixture
def valid_token(client):
    print("\nObtaining JWT...")
    url = '/login'

    admin_user = os.getenv('API_ADMIN')
    admin_auth = os.getenv('API_ADMIN_AUTH')

    payload = {
        'user': admin_user,
        'auth': admin_auth
    }

    response = client.simulate_post(url, body=json.dumps(payload))
    assert response.status == falcon.HTTP_201
    token = response.json['token']
    return token



def test_login_request(client):
    """ /login api test """
    # Define the URL and payload
    url = '/login'

    admin_user = os.getenv('API_ADMIN')
    admin_auth = os.getenv('API_ADMIN_AUTH')

    payload = {
        'user': admin_user,
        'auth': admin_auth
    }

    # Perform the POST request
    response = client.simulate_post(url, body=json.dumps(payload))

    # Check the response status code
    #assert response.status == "201 Created"
    assert response.status == falcon.HTTP_CREATED

    # Parse the response JSON
    response_json = response.json

    # Check the response content
    assert response_json['message'] == 'auth successful'

def test_public_quote_request(client):
    """ /quote api test """

    url = '/quote'
    response = client.simulate_get(url)

    response_json = response.json

    assert response.status == falcon.HTTP_OK
    assert response_json['author'] == 'Grace Hopper'

def test_public_prometheus_metrics(client):
    """ /metrics api test """

    url = '/metrics'
    response = client.simulate_get(url)

    assert response.status == falcon.HTTP_OK

def test_protected_request(client,valid_token):
    """ /protected api test """

    headers = {'Authorization': "Bearer %s" % valid_token }

    url = '/protected'
    response = client.simulate_get(url, headers=headers)

    response_json = response.json

    assert response.status == falcon.HTTP_OK
    assert response_json['message'] == "Welcome protected"

def test_register_request(client,valid_token):
    """ /register api test """

    headers = {'Authorization': "Bearer %s" % valid_token }

    # Define the URL and payload
    url = '/register'

    payload = {
        'user': "test_user_1",
        'auth': "test_auth_123"
    }

    # Perform the POST request
    response = client.simulate_post(url, headers=headers, body=json.dumps(payload))

    # Check the response status code
    #assert response.status == "201 Created"
    assert response.status == falcon.HTTP_CREATED

    # Parse the response JSON
    response_json = response.json

    # Check the response content
    assert response_json['registered'] == "test_user_1"
