"""Celery signal.

Use this module directly as config module for the celery worker:

    env CELERY_CONFIG_MODULE=impact_stack.observability.tracing.celery celery worker

Or via a custom celery config module (eg. located at the project root path) by
specifiying it in `imports`:

    # celeryconfig.py
    imports = ["impact_stack.observability.tracing.celery"]

    env CELERY_CONFIG_MODULE=celeryconfig celery worker

In your app's pyproject.toml you need to define the following Python entry point
to refer to the tracing extension instance (this then get's picked up by this
Celery signal):

    [project.entry-points.impact_stack_observability_tracing]
    celery = "myapp.tracing:tracing"

"""

from celery import current_app
from celery.signals import worker_process_init

from . import utils


@worker_process_init.connect
def init_tracing(*_args, **_kwargs):  # pragma: no cover
    """Celery worker init hook.

    Tracing needs to be set up after each worker has started. See
    https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/celery/celery.html#setting-up-tracing
    """
    current_app.log.get_default_logger().debug("Initializing tracing in celery worker")

    tracing_ext = utils.load_one_entry_point_by_name_or_none(
        "impact_stack_observability_tracing", "celery"
    )

    # Initialize tracing. This starts emiting tracing signals.
    if tracing_ext:
        tracing_ext.init_celery(current_app)
