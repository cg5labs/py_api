# py_api
Sample Python project for web API. 

Features

* Manages JWT (JSON Web Token)
* URI RBAC using JWT

## Tech stack

- Falcon Web API framework
- Falcon Prometheus add-on for metrics
- PyJWT
- SQL Alchemy (SQLite, PostgreSQL)

## Setup

Create '.env' file with environment settings:

```
# Comment
PROFILE="LOCAL"
LOCAL_DB_ENGINE="sqlite"
DEFAULT_DB_ENGINE="postgresql"

# only for sqlite local DB
DB_PATH="dev.db"

# only for PostgreSQL
DB_USER="postgres"
DB_PASS="password123"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="apidb"

# API admin to manage API users
API_ADMIN="user1"
API_ADMIN_AUTH="pass123"
```

Create crypto key: Generate a secret.key and store it in the working path.

```$ python3 generate_key.py```

## Testing
Verbose output with supressed warnings:
```$ pytest --disable-warnings -v -s api_tests.py```

Summary only with supressed warnings:
```$ pytest --disable-warnings api_tests.py```
