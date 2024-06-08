#!/usr/bin/env python3
""" SQL management  """

import os
import logging

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Sequence, Boolean

from db import Base

# Create a logger for this module
log = logging.getLogger(__name__)

load_dotenv()  # take environment variables

def load_key():
    """ Load the key from the file """

    secret_key = os.getenv('SECRET_KEY')
    log.info("loaded key: %s" % secret_key)
    return open(secret_key, "rb").read()

# Encrypt and decrypt functions
def encrypt_string(plain_text, key):
    """ Encrypts strings """

    log.debug("encrypt_string")
    cipher_suite = Fernet(key)
    if plain_text is None:
        return None
    return cipher_suite.encrypt(plain_text.encode()).decode()
    #return cipher_suite.encrypt(plain_text)

def decrypt_string(encrypted_text, key):
    """ Decrypts strings """

    log.debug("decrypt_string")
    cipher_suite = Fernet(key)
    if encrypted_text is None:
        return None
    return cipher_suite.decrypt(encrypted_text.encode()).decode()
    #return cipher_suite.decrypt(encrypted_text)


# Define the User model
class User(Base):
    """ Define the User model """
    __tablename__ = 'users'
    id = Column(Integer, Sequence('users_seq'), primary_key=True)
    user_name = Column(String(255))
    user_auth = Column(String(255))

    def __init__(self, user_name, user_auth):
        key = load_key()
        self.user_name = user_name
        self.user_auth = encrypt_string(user_auth, key)

    @property
    def decrypted_user_auth(self):
        key = load_key()
        return decrypt_string(self.user_auth, key)

