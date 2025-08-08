"""Generic health checks."""

import flask
import requests
from requests.exceptions import RequestException


def check_true():
    """Check which always returns true."""
    return True


def check_false():
    """Check which always returns false."""
    return False


def check_db():
    """Check the database connectivity.

    Check by querying for 1.
    This checks if the DB is alive and connectable.

    Requires the Flask-SQLAlchemy extension to find the engine.
    Only checks the default engine.
    """
    if "sqlalchemy" not in flask.current_app.extensions:
        return False

    result = 0

    try:
        with flask.current_app.extensions["sqlalchemy"].engine.connect() as conn:
            result = conn.exec_driver_sql("SELECT 1").scalar()
    except Exception:  # pylint: disable=broad-except
        pass

    return result == 1


def base_check_api_liveliness(method, url, status_code=200, timeout=3.0, **kwargs):
    """Base check for liveliness of external API.

    NB: This is the base function for a check; you need to provide a callable
    which does not expect any args. You can e.g. use `functools.partial` to do
    that.

    It checks whether an endpoint is responding as expected.
    If we get a response before the timeout it's OK.

    Default timeout is 3.0 seconds.
    """
    resp = None
    try:
        resp = requests.request(method, url, timeout=timeout, **kwargs)
    except RequestException:
        return False

    if resp.status_code == status_code:
        return True

    return False
