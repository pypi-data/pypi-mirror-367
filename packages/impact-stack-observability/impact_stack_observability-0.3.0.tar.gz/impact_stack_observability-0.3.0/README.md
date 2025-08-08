# Observability for Impact Stack

A package providing observability features for Flask apps.

## Health checks

The `Health` Flask extension provides health checks via an HTTP API.

The list of checks is extendable per app.

### How it works

When called the requested checks run and return `True` or `False`. When *all*
checks return `True` the service/app is considered healthy (i.e. in the
`running` state), otherwise it is considered to be in a `degraded` state.

Checks are expected to be a Python callable, which takes no arguments and
returns a boolean.

### Usage

Create an implementation module, e.g in a `health.py` file:

```python
"""Instantiate and configure checks."""

from impact_stack.observability import health as health_

health = health_.Health()


health.register_check("true", health_.checks.check_true, add_to_defaults=False)


@health.register_check("foo", add_to_defaults=False)
def check_foo():
    """Check for availability of foo."""
    return True
```

In `app.py`:

```python
import flask

from . import health

app = flask.Flask(__name__)
health.health.init_app(app)
```

No configuration is read from `app.config`. You are supposed to configure and
optionally extend the Health extension in the implementation module.

### Checking the liveliness of the app

You can do a simple liveliness check at `/health/ping` (default), which will
just return a `200 OK` text response.

### Checking the service health

A more comprehensive health check is available at `/health/` (default).
This returns a JSON response with following structure (prettyfied):

```javascript
{
  "health": "running",
  "available_checks": [
    "true",
    "foo"
  ],
  "checks": {
    "foo": true
  }
}
```

The `health` field can be of:

- `running`: All requested checks returned `true`
- `degraded`: At least one of the checks returned `false`

Specific checks can be requested with the `checks` parameter:

- `/health/?checks=_defaults`: Run all the checks registered as defaults, same
  as omitting the `checks` parameter alltogether
- `/health/?checks=true,foo`: Run the listed checks

Headers to prevent caching of the health responses are set.

### Provided checks

Some generic checks are providing in this module.

#### `check_true` and `check_false`

Dummy checks which return just `true` resp. `false`

#### `check_db`

(Requires `Flask-SQLAlchemy`.)

Checks if the DB (using the default SQLAlchemy engine) is available by trying a `SELECT 1`

#### `base_check_api_liveliness`

(Needs instantiation.)

Base check for checking the liveliness of an (external) HTTP API.

Example usage:

```python
import functools

from impact_stack.observability import health as health

check_example = functools.partial(
    health_.checks.base_check_api_liveliness,
    "GET",
    "https://api.example.com/v1/health/ping",
    200,  # expected response status code
    2.0,  # timeout
)
health.register_check("example", check_example)
```

### Authorization

A simple mechanism to prevent unrestricted calls to the `/health/` endpoint is
using a shared secret in the HTTP calls.

Set the required config variable `HEALTH_URL_SECRET` to a (random) string and
use the GET param `auth` in calls to the endpoint.
Returns `401` if the secret does not match.
Raises a `RuntimeError` if not set.

If the `HEALTH_URL_SECRET` is set to `None`, checking the secret is disabled.

## Tracing

Tracing is implemented by using the OpenTelemetry Python API and SDK.
OpenTelemetry is a standard for implementing distributed tracing and supports a variety of programming languages by providing API and SDK libraries.
Multiple services exist which receive distributed traces from instrumented apps and provide users an interface to the traces.

See

- <https://opentelemetry.io/> for a general introduction to Open Telemetry and tracing,
- <https://opentelemetry.io/docs/languages/python/instrumentation/> for the Python API and SDK,
- <https://opentelemetry-python-contrib.readthedocs.io/en/latest/> for Python specfic "autoinstrumentations".

You need to "instrument" and configure your app in your code base in order to produce traces.

Using this library you have 3 ways to achieve that, which can all be used together:

- Use the provided `autoinstrument_app()` function for a basic set of instrumentation,
- use the provided `new_span()` decorator to instrument your app for specific functions or methods, or
- just use the OpenTelemetry API to instrument your app.

### Basic Usage

Configure the app:

```python
# app.py
import flask
from impact_stack.observability import tracing

app = flask.Flask(__name__)
app.config["TRACING_ENABLED"] = True  # default
# instrumentors default: None, means using all instrumentors found in the Python
# environment
app.config["TRACING_INSTRUMENTORS"] = ["flask"]
tracing_ext = tracing.Tracing()

# Initialize tracer, create the resource used by this tracer
tracing_ext.init_app(
    app,
    attributes={"additional.attribute": "foo"}
)
```

Then run the app with appropriate OS environment variables set, e.g.

```bash
env OTEL_SERVICE_NAME=myapp OTEL_TRACES_EXPORTER=console OTEL_RESOURCE_ATTRIBUTES=foo.bar=baz flask run
```

You can also use the utility functions `init_tracing()` and `autoinstrument_app()` if you need a bit more control.

NB: The `autoinstrument_app()` call can happen before `init_tracing` as well, but then the `logging` autoinstrumentation is not able to pick up the `service.name` resource value. So you will loose some functionality in this case.

### Autoinstrumentations

Tested and supported autoinstrumentations are:

- `celery`: <https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/celery/celery.html>
- `flask`: <https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/flask/flask.html>
- `logging`: <https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/requests/requests.html>
- `requests`: <https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/requests/requests.html>
- `sqlalchemy`: <https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/sqlalchemy/sqlalchemy.html>

By default `autoinstrument_app()` reads all installed entry points named `opentelemetry_instrumentor` and tries to instantiate them. Special care is applied for `flask` and `sqlalchemy` (when using `Flask-SQLAlchemy`) autoinstrumentations.

For the record: The OpenTelemetry API in general is not bound to something like a Flask app being available before autoinstrumentation. This library on the other hand is intented to be used with Flask apps and thus mandates an Flask `app` object for it's use of `autoinstrument_app()`.

Take a good look at the autoinstrumentations and check how to use them.

### Forking servers (gunicorn)

For WSGI servers like `gunicorn` you need to use lifecycle hooks for initializing the tracing.
See <https://opentelemetry-python.readthedocs.io/en/latest/examples/fork-process-model/README.html>.
