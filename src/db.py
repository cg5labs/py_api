#!/usr/bin/env python3
""" DB setup and base class for SQL models  """

import os

from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

#from sql_models import User

def create_db_engine():

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

    #sql_engine = create_engine(DATABASE_URL, echo=True)
    sql_engine = create_engine(DATABASE_URL, echo=False)

    return sql_engine

load_dotenv()  # take environment variables


# Create a base class for our classes definitions.
Base = declarative_base()

engine = create_db_engine()


# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
sql_session = Session()