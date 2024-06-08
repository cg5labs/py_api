#!/usr/bin/env python3
""" Encryption key generator """

import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()  # take environment variables

# Generate a key
key = Fernet.generate_key()

# Save the key to a file

secret_key = os.getenv('SECRET_KEY')
with open(secret_key, "wb") as key_file:
    key_file.write(key)

print("Key saved to %s" % secret_key)
