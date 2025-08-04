# Kition Django Defaults

[![CI](https://github.com/kition-dev/djangodefaults/actions/workflows/test.yml/badge.svg)](https://github.com/kition-dev/djangodefaults/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/kition-djangodefaults.svg)](https://pypi.org/project/kition-djangodefaults/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kition-djangodefaults.svg)
[![PyPI - License](https://img.shields.io/pypi/l/kition-djangodefaults.svg)](https://github.com/kition-dev/djangodefaults/blob/main/LICENSE)

This package provides default configuration and components for Django projects.

## Motivation

Building, operating and maintaining many Django applications leads to repetitive code. This repository strives to reduce
the mental overhead by providing code that otherwise would have to be repeated.

## Installation

### Requirements

Python 3.12 and Django 5.1 supported.

### Installation

1. Install with **pip**:
   ```
   python -m pip install kition-djangodefaults
   ```
2. Start your applications settings file with the default setting initialization
   ```python
   from kition_djangodefaults import initialize_default_settings

   initialize_default_settings(__name__)
   ```
3. (Optional) configure any of the following components.

Consider explicitly listing the dependencies of `kition-djangodefaults` in your project to pin specific versions of
Django, psycopg and others.

## Kubernetes Readiness Endpoint Middleware

Install via

```python
MIDDLEWARE = [
    # Putting the healthcheck middleware first to circumvent ALLOWED_HOSTS protections, which would fail Kubernetes
    # Readiness Probe requests.
    "kition_django_defaults.healthcheck.HealthCheckMiddleware",
    ...
]
```

## Prevent Exception Logging in Tests

Django views that raise `PermissionDenied` or `Http404` errors clutter the log and tell them apart from deprecation
warnings. To prevent them call `configure_logging_to_skip_exception` within your test settings.

```python
import logging

from django.core.exceptions import PermissionDenied
from kition_djangodefaults import configure_logging_to_skip_exception

from config.settings import *

global LOGGING
configure_logging_to_skip_exception(LOGGING, PermissionDenied, logging.ERROR)
```

## Development

```bash
poetry env use $(pyenv which python)
poetry install --extras=dev --extras=worker
poetry run python -m unittest
```

## Provided Configuration

The following section describe the general behaviour of setting groups, while not trying to be exhaustive. Check the
code for details. Environment variables are listed for non-Django people.

### General

The settings resolve the `BASEDIR` to be the grandparent of the applications settings file, which usually is the
projects root directory.

| Name         | Description                                                                                                       | Value                                             |
|--------------|-------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| `DEBUG`      | Enable the Django debug mode to print additional error information.                                               | `false`                                           |
| `SECRET_KEY` | A secret key used for cryptographic signing. Has to be unique and unpredictable. 64 character length recommended. | return value of Djangos `get_random_secret_key()` |

### Network

| Name                             | Description                                                                                                         | Value               |
|----------------------------------|---------------------------------------------------------------------------------------------------------------------|---------------------|
| `ALLOWED_HOST`                   | Hostname or domain name that the application is allowed to serve. Prevents HTTP Host header attacks.                | `localhost`         |
| `TLS_ENABLED`                    | Flag to enable or disable TLS/SSL settings for secure connections. Typically set to true in production.             | `false`             |
| `SECURE_PROXY_SSL_HEADER_NAME`   | The name of the HTTP header used by the proxy to indicate that the original request was made via HTTPS.             | `X-Forwarded-Proto` |
| `SECURE_PROXY_SSL_HEADER_VALUE`  | The value for the SECURE_PROXY_SSL_HEADER_NAME that confirms the request was secure (HTTPS).	                       | `https`             |
| `SECURE_HSTS_SECONDS`            | The duration in seconds that the browser should enforce HTTPS via the HTTP Strict Transport Security (HSTS) policy. | `3600`              |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | A flag indicating whether to apply HSTS to all subdomains as well.                                                  | `false`             |
| `SECURE_HSTS_PRELOAD`            | A flag indicating whether the application should be included in browsers' HSTS preload lists.                       | `false`             |

### Database

The application connects to a locally hosted Postgres by default.

| Name                | Description                                                                    | Value       |
|---------------------|--------------------------------------------------------------------------------|-------------|
| `DATABASE_NAME`     | The name of the database used by the application.                              | `app`       |
| `DATABASE_USER`     | The username used to authenticate and connect to the database.	                | `postgres`  |
| `DATABASE_PASSWORD` | The password associated with the database user for authentication.	            | `app`       |
| `DATABASE_HOST`     | The hostname or IP address where the database server is located.               | `localhost` |
| `DATABASE_PORT`     | The port used to connect to the database server, commonly 5432 for PostgreSQL. | `5432`      |

### Storage and Staticfiles

| Name                       | Description                                                                                                                          | Value                   |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| `OBJECT_STORAGE_ENABLED`   | Determines whether object storage is enabled. If disabled, files will be stored at path `BASEDIR/media/`.                            | `false`                 |
| `STORAGE_BUCKET_NAME`      | The name of the storage bucket where files will be stored.                                                                           | `app`                   |
| `STORAGE_ENDPOINT`         | The URL endpoint for accessing the object storage. The URL has to be accessible by the backend and clients.                          | `http://localhost:9000` |
| `STORAGE_REGION`           | The geographic region of the storage service, commonly used in cloud environments like AWS S3 to specify the location of the bucket. | `eu-central-1`          |
| `AWS_S3_ACCESS_KEY_ID`     | The access key ID used to authenticate requests to the object storage service.                                                       | `""`                    |
| `AWS_S3_SECRET_ACCESS_KEY` | The secret access key used alongside the access key ID to authenticate and securely interact with the object storage.                | `""`                    |

### E-Mail

| Name                  | Description                                                                                                 | Value                 |
|-----------------------|-------------------------------------------------------------------------------------------------------------|-----------------------|
| `DEFAULT_FROM_EMAIL`  | The default email address to use for email notifications sent by the application.                           | `noreply@example.com` |
| `EMAIL_HOST`          | The host server that will send the email, typically an external SMTP server.                                | `localhost`           |
| `EMAIL_PORT`          | The port used to connect to the email host, `1025` for local development or standard SMTP ports like `587`. | `1025`                |
| `EMAIL_USE_TLS`       | Specifies whether the email transmission should use TLS encryption.                                         | `false`               |
| `EMAIL_HOST_USER`     | The username for authenticating with the email host.                                                        | `""`                  |
| `EMAIL_HOST_PASSWORD` | The password for authenticating with the email host.                                                        | `""`                  |

### Background Tasks via django-q2

If `django_q` is available

- a default configuration using the DjangoORM is applied and
- the `sendtestmail` management command allows sending via a background task.

You are able to install the dependency via the `worker` extra.