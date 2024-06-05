#!/usr/bin/env python3

import os

from dotenv import load_dotenv

from sql_models import User, session, encrypt_string, decrypt_string

# CREATE
def create_user(user_name, user_auth):
    new_user = User(user_name, user_auth)
    session.add(new_user)
    session.commit()
    return new_user

# READ
def get_user(user_id):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        return {
            'id': user.id,
            'name': user.user_name,
            'auth': user.user_auth
        }
    return None

def get_all_users():
    users = session.query(User).all()
    return [{
        'id': user.id,
        'name': user.user_name,
        'auth': user.user_auth
    } for user in users]

# UPDATE
def update_user(user_id, user_name=None, user_auth=None):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        if user_name:
            user.name = encrypt_string(user_name)
        if user_auth:
            user.auth = encrypt_string(user_auth)
        session.commit()
        return {
            'id': user.id,
            'name': user.user_name,
            'auth': user.user_auth
        }
    return None

# DELETE
def delete_user(user_id):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        session.delete(user)
        session.commit()
        return True
    return False

if __name__ == "__main__":

    load_dotenv()  # take environment variables

    # Create admin user
    admin_user = os.getenv('API_ADMIN')
    admin_auth = os.getenv('API_ADMIN_AUTH')
    admin = create_user(admin_user, admin_auth)

    # Read users
    print(f"admin: {get_user(admin.id)}")
    print(f"All Users: {get_all_users()}")

    # Update user
    #update_user(user2.id, user_auth='test999')
    #print(f"Updated User 2: {get_user(user2.id)}")

    # Delete user
    #delete_user(user2.id)
    #print(f"All Users after deletion: {get_all_users()}")
