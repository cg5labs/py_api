#!/usr/bin/env python3
""" SQL management  """

import os

from sqlalchemy import create_engine, Column, Integer, String, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet

from dotenv import load_dotenv

load_dotenv()  # take environment variables

# Load database configuration from environment variables
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_path = os.getenv('DB_PATH')
system_profile = os.getenv("PROFILE")

db_engine = "%s_DB_ENGINE" % system_profile

match os.getenv(db_engine):
    case "sqlite":
        DATABASE_URL = "sqlite:///%s" % db_path

    case "postgresql":
        DATABASE_URL = ( "postgresql+psycopg2://%s:%s@%s:%s/%s" % (db_user, db_pass, db_host,
            db_port, db_name))

# Create the SQLAlchemy engine
#engine = create_engine(DATABASE_URL, echo=True)
engine = create_engine(DATABASE_URL, echo=False)

# Create a base class for our classes definitions.
Base = declarative_base()

# Load the key from the file
def load_key():
    return open("secret.key", "rb").read()

# Encrypt and decrypt functions
def encrypt_string(plain_text):
    if plain_text is None:
        return None
    return cipher_suite.encrypt(plain_text.encode()).decode()
    #return cipher_suite.encrypt(plain_text)

def decrypt_string(encrypted_text):
    if encrypted_text is None:
        return None
    return cipher_suite.decrypt(encrypted_text.encode()).decode()
    #return cipher_suite.decrypt(encrypted_text)


# Define the User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('users_seq'), primary_key=True)
    user_name = Column(String(255))
    user_auth = Column(String(255))

    def __init__(self, user_name, user_auth):
        self.user_name = user_name
        self.user_auth = encrypt_string(user_auth)

    @property
    def decrypted_user_auth(self):
        return decrypt_string(self.user_auth)


key = load_key()
cipher_suite = Fernet(key)

# Create all tables
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()
