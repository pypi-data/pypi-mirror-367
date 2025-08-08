"""Default configuration module for use with gunicorn.

Usage:

    gunicorn -c python:impact_stack.observability.tracing.gunicorn wsgi:app

In your app's pyproject.toml you need to define the following Python entry point
to refer to the tracing extension instance (this then get's picked up by this
gunicorn hook):

    [project.entry-points.impact_stack_observability_tracing]
    gunicorn = "myapp.tracing:tracing"

If you want to or need to use a config file like gunicorn.conf.py, you can just
import the `post_worker_init` name into your config file to get the default
behaviour:

    # gunicorn.conf.py

    from impact_stack.observability.tracing.gunicorn import post_worker_init

    # other hooks
    def pre_fork(*args):
        pass

If you want to extent a post_hook you can call the hook provided in this module
in your own hook:

    # gunicorn.conf.py

    from impact_stack.observability.tracing.gunicorn import start_tracing

    def post_fork(*args):
        app = server.app.wsgi()

        # Initialize tracing
        start_tracing(app, {})

        # Additional behaviour
        # ...

Notes about the gunicorn hook to use:

- As we rely on having the Flask app (not the gunicorn WSGIApplication)
  available when initializing and starting tracing, we use a late hook which
  runs *after* gunicorn loaded the Flask app: `post_worker_init`.
- If we would just use `post_fork` we would load the app before monkey patching
  happens for gevent (by default between post_fork and post_worker_init),
  leading  to potential issues due to importing before patching (see gunicorn
  error log).
- (Monkey patching earlier is a potential option, but triggers gevent warnings.)
- Downside: tracing and instrumentation is not set up until the Flask app is is
  loaded.

This setup is supported when using

- `sync` workers (with preloaded or non-preloaded apps) and;
- `gevent` workers (only with non-preloaded apps).
"""

import logging

from . import utils


def start_tracing(app, resource_attributes):  # pragma: no cover
    """Utility method to start tracing.

    You can call this from your custom post_fork hook as well.
    """
    # Use gunicorn logger as we do not require the WSGI app to be a Flask app
    logger = logging.getLogger("gunicorn.error")
    logger.debug("Initializing tracing in gunicorn worker")

    tracing_ext = utils.load_one_entry_point_by_name_or_none(
        "impact_stack_observability_tracing", "gunicorn"
    )

    # Initialize tracing. This starts emiting tracing signals.
    if tracing_ext:
        tracing_ext.init_app(app, resource_attributes)


def post_worker_init(worker):  # pragma: no cover
    """Gunicorn post worker init hook for initializing tracing.

    Gunicorn works with a fork process model and thus a special treatment is needed when
    initializing the tracer. See
    https://opentelemetry-python.readthedocs.io/en/latest/examples/fork-process-model/README.html
    """
    app = worker.app.wsgi()
    resource_attributes = {"wsgi_server": "gunicorn"}
    start_tracing(app, resource_attributes)
