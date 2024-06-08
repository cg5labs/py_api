#!/usr/bin/env python3
""" DB connection and base class for SQL models  """

import os

from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

#from sql_models import User

def create_db_engine():
    """ Initialize DB connection """

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
            database_url = "sqlite:///%s" % db_path

        case "postgresql":
            database_url = ( "postgresql+psycopg2://%s:%s@%s:%s/%s" % (db_user, db_pass, db_host,
                db_port, db_name))

    #sql_engine = create_engine(database_url, echo=True)
    sql_engine = create_engine(database_url, echo=False)

    return sql_engine

load_dotenv()  # take environment variables

# Create a base class for our classes definitions.
Base = declarative_base()

engine = create_db_engine()


# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
sql_session = Session()
