#!/usr/bin/env python3
""" SQL init and tests   """

import os

from dotenv import load_dotenv

import db
from sql_models import User, encrypt_string, decrypt_string, load_key

# CREATE
def create_user(user_name, user_auth):
    """ create user record """
    new_user = User(user_name, user_auth)
    db.sql_session.add(new_user)
    db.sql_session.commit()
    return new_user

# READ
def get_user(user_id):
    """ query user records for user_id """
    user = db.sql_session.query(User).filter(User.id == user_id).first()
    if user:
        return {
            'id': user.id,
            'name': user.user_name,
            'auth': user.user_auth
        }
    return None

def get_all_users():
    """ select * from users """
    users = db.sql_session.query(User).all()
    return [{
        'id': user.id,
        'name': user.user_name,
        'auth': user.user_auth
    } for user in users]

# UPDATE
def update_user(user_id, user_name=None, user_auth=None):
    """ update user record """

    key = load_key()

    user = db.sql_session.query(User).filter(User.id == user_id).first()
    if user:
        if user_name:
            user.name = user_name
        if user_auth:
            user.auth = encrypt_string(user_auth, key)
        db.sql_session.commit()
        return {
            'id': user.id,
            'name': user.user_name,
            'auth': user.user_auth
        }
    return None

# DELETE
def delete_user(user_id):
    """ delete user record """
    user = db.sql_session.query(User).filter(User.id == user_id).first()
    if user:
        db.sql_session.delete(user)
        db.sql_session.commit()
        return True
    return False


def main():
    """ main """

    load_dotenv()  # take environment variables

    engine = db.create_db_engine()
    db.Base.metadata.create_all(engine)

    # Create admin user
    admin_user = os.getenv('API_ADMIN')
    admin_auth = os.getenv('API_ADMIN_AUTH')
    admin = create_user(admin_user, admin_auth)

    # Read users
    print(f"admin: {get_user(admin.id)}")
    print(f"All Users: {get_all_users()}")

def crud_tests():
    """ SQL unit tests """

    # Create, Update user
    user2 = create_user("user2", "test123")
    update_user(user2.id, user_auth='test999')
    print(f"Updated User 2: {get_user(user2.id)}")

    # Delete user
    delete_user(user2.id)
    print(f"All Users after deletion: {get_all_users()}")

if __name__ == "__main__":

    main()
    crud_tests()

