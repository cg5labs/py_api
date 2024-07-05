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

## Kubernetes

### Deployment
Two-stage deployment on Kubernetes clusters.

**Stage 1:** Create/deploy secrets. Example with mock-credentials. To use a K8s secrets manager (e.g. HC Vault) in production scenarios.

```bash
$ kubectl create secret generic api-credentials --from-literal=API_ADMIN=user1 --from-literal=API_ADMIN_AUTH=pass123
```

```bash
$ kubectl create secret generic postgres-credentials --from-literal=POSTGRES_DB=apidb --from-literal=POSTGRES_PASSWORD=pass123 --from-literal=POSTGRES_USER=postgres
```

Optional for Elastic APM support:

```bash
$ kubectl create secret generic eck-apm-token --from-literal=secret-token=123456789
```

**Stage 2:**  Deploy Helm chart
The Helm chart can be customized further with the provided values.yaml file. Not all parameters are exposed yet in values.yaml.

```bash
$ Helm upgrade --install -n api py-api py-api -f py-api/values.yaml
```

The Helm chart configures two K8s deployments, one for a DB backend pod with PostgreSQL, the other for the API app. To run this without the PostgreSQL DB backend, just remove the DB deployment from the Helm templates path and replace the DB config values with the external DB in the Helm values.yaml. 

### Verification
Post-deployment verification on pod health and logs follows.

```bash
$ kubectl get pod -n api
NAME                          READY   STATUS    RESTARTS   AGE
postgresql-7d4564945b-ghd8l   1/1     Running   0          38m
py-api-5dc656c4b9-lwhms       1/1     Running   0          33m
```

```bash
$ kubectl logs -n api -f py-api-5dc656c4b9-lwhms
Defaulted container "py-api" out of: py-api, keygen (init), db-init (init)
2024-07-05 09:12:43,913 - __main__ - INFO - --profile override set: DEFAULT.
2024-07-05 09:12:43,914 - __main__ - INFO - Loaded system profile: DEFAULT
2024-07-05 09:12:43,914 - __main__ - INFO - Instantiating Falcon application.
2024-07-05 09:12:43,915 - __main__ - INFO - Launching WSGI server for Falcon application.
2024-07-05 09:12:43,918 - webserver - INFO - log: webserver
2024-07-05 09:12:43,918 - webserver - INFO - Serving on port 8000...
2024-07-05 09:57:52,715 - api - INFO - SID 38cc964a-3ac3-415f-9b0b-91523edd2839
2024-07-05 09:57:52,716 - api - INFO - verify_creds
2024-07-05 09:57:52,766 - api - INFO - create_token
2024-07-05 09:57:52,766 - api - INFO - POST /login 201 Created None
127.0.0.1 - - [05/Jul/2024 09:57:52] "POST /login HTTP/1.1" 201 208
2024-07-05 09:58:43,270 - api - INFO - GET /quote 200 OK None
127.0.0.1 - - [05/Jul/2024 09:58:43] "GET /quote HTTP/1.1" 200 103


```
