"""Instrumentation."""

# pylint: disable=too-few-public-methods

import functools
import inspect
import logging
import os
import platform
from inspect import Parameter
from typing import Sequence

import pkg_resources
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, ResourceDetector, get_aggregated_resources
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes

logger = logging.getLogger("impact_stack.observability")


def load_one_entry_point_by_name_or_none(group, name):
    """Return a single entry point or None."""
    entry_points = list(pkg_resources.iter_entry_points(group, name))

    import_name = f"{group}:{name}"
    if len(entry_points) == 0:
        logger.warning('No "%s" entry point found.', import_name)
        return None

    if len(entry_points) > 1:
        logger.warning('Multiple "%s" entry points found. Using only the first one.', import_name)

    return entry_points[0].load()


def load_opentelemetry_entry_points(group="opentelemetry_traces_exporter"):
    """Loads available OpenTelemetry components.

    The Python implementation of OpenTelemetry uses Python entry points to
    announce available components like exporters
    (`opentelemetry_traces_exporter`).
    """
    traces_exporters = {}
    for entry_point in pkg_resources.iter_entry_points(group):
        traces_exporters[entry_point.name] = entry_point.load()
    return traces_exporters


def create_resource(attributes=None, resource_detectors=None):
    """Create the resource.

    Used with OTel defaults, configured resource detectors and custom
    attributes.

    Attributes come from OTel standard attributes, the additional attributes for
    the service, and the custom attributes from the arguments.

    Attributes from the env variable `OTEL_RESOURCE_ATTRIBUTES` are read as
    well.

    The Service name is required for most backends, and expected to be set via
    the env variable (`OTEL_SERVICE_NAME`).
    """
    resource_detectors = resource_detectors or [PlatformResourceDetector()]
    attributes = attributes or {}
    resource = get_aggregated_resources(resource_detectors)
    return resource.merge(Resource(attributes))


def init_tracing(
    attributes=None,
    resource_detectors=None,
    tracer_provider=None,
    set_global_tracer_provider=True,
    initialize_exporters=True,
):
    """Initialize tracing.

    This call can be deferred so that pre-forking servers like gunicorn work
    corectly with the `BatchSpanProcessor` used.

    Background: For the service to generate span signals, you need to set up
    the tracer provider. If instrumentations generate spans before a proper
    tracer provider is set up, the minimal NoOp implementation will be used
    (proxy). Once the tracer provider is set, this will be used.

    Exporter config is expected to be set via env variables, e.g.:

    - `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_INSECURE`
    - Honors the SDK env variable `OTEL_TRACES_EXPORTER` and supports adding
      OTLP and console exporters. Multiple exporters can be enabled by joining
      with ",".

    Sets the global tracer provider by default.
    """
    if not tracer_provider:
        resource = create_resource(attributes, resource_detectors)
        tracer_provider = TracerProvider(resource=resource)

    if initialize_exporters:
        init_exporters(tracer_provider)

    if set_global_tracer_provider:
        trace.set_tracer_provider(tracer_provider)

    return tracer_provider


def init_exporters(tracer_provider, span_processor_class=BatchSpanProcessor):
    """Initialize span exporter with tracer provider."""
    traces_exporters = load_opentelemetry_entry_points()
    processors = []

    # Parse exporter names from environment variable
    # Empty strings are omitted
    for exporter_name in os.environ.get("OTEL_TRACES_EXPORTER", "").split(","):
        if not exporter_name or exporter_name == "none":
            continue

        if exporter_name in traces_exporters:
            processor = span_processor_class(traces_exporters[exporter_name]())
            tracer_provider.add_span_processor(processor)
            processors.append(processor)
            logger.info("Span processor added: %s", exporter_name)
        else:
            logger.error(
                (
                    'Exporter "%s" not available. '
                    "Please ensure that the providing package is installed."
                ),
                exporter_name,
            )

    return processors


def get_installed_instrumentor_names():
    """Get a sorted list of names of installed instrumentors."""
    return sorted(
        [
            entry_point.name
            for entry_point in pkg_resources.iter_entry_points("opentelemetry_instrumentor")
        ]
    )


def autoinstrument_app(app, instrumentors=None, tracer_provider=None):
    """Autoinstrument with installed instrumentors.

    You can give
    - a list of instrumentors to load
    - a specific tracer provider to use (default: the global one)
    """
    instrumentors = get_installed_instrumentor_names() if not instrumentors else instrumentors
    loaded_instrumentors = {}
    for entry_point in pkg_resources.iter_entry_points("opentelemetry_instrumentor"):
        if entry_point.name in instrumentors:
            instrumentor = entry_point.load()
            if entry_point.name == "flask":
                instrumentor().instrument_app(app, tracer_provider=tracer_provider)
            # Flask-SQLAlchemy is used
            elif entry_point.name == "sqlalchemy" and "sqlalchemy" in app.extensions:
                with app.app_context():
                    instrumentor().instrument(
                        engine=app.extensions["sqlalchemy"].engine,
                        tracer_provider=tracer_provider,
                    )
            else:
                instrumentor().instrument(tracer_provider=tracer_provider)
            loaded_instrumentors[entry_point.name] = instrumentor
    return loaded_instrumentors


def _get_arg_value(param: inspect.Parameter, idx: int, args: list, kwargs: dict):
    """Extract the value of a parameter from args and kwargs."""
    arg_kinds = (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
    if param.kind in arg_kinds and idx < len(args):
        return args[idx]
    kwarg_kinds = (param.KEYWORD_ONLY, param.POSITIONAL_OR_KEYWORD)
    if param.kind in kwarg_kinds and param.name in kwargs:
        return kwargs[param.name]
    return param.default


def new_span(
    name,
    unwrap_attributes_from_return_value=False,
    return_value_as=None,
    args_as=None,
    tracer_provider=None,
):
    """Decorator for creating a new span.

    If you need the current span in the function body, e.g. for setting
    additional attributes or adding events, you can always reach directly to the
    OpenTelemetry API and use `trace.get_current_span()`.

    You can capture attributes returned from the function when
    `unwrap_attributes_from_return_value` is true and the return value is a
    tuple of `tuple(attributes, return_value)`.

    Ensure you are using valid span attribute names and values:

    - The attribute name must at least be a valid Unicode sequence, but should
      adher to best practices, see e.g.
      https://opentelemetry.io/docs/reference/specification/common/attribute-naming/
    - The attribute value value type must be of: `bool`, `int`, `float`, and
      `str` or a sequence thereof.
      If an invalid attribute type is recorded, the attribute is cast to a string;
      the overriden default of OTel would be omitting the value and a logging a
      warning.
      NB: A sequence is not further inspected currently.

    You can capture return values when you give an attribute name to
    `return_value_as`.

    You can also capture call parameters (args and kwargs) via `args_as`.
    The value of `args_as` is a mapping from the argument name to an attribute
    key with which the value of the parameter should be recorded.
    The same rules for valid attribute names and value as above apply.

    If an `args_as` key maps to a Callable, it is called with the argument's
    value as sole argument.  The Callable needs to return a dict with valid
    attribute keys mapping to valid attribute values.

    NB: Specifying the variadic args/kwargs name (usually named
    `*args`/`**kwargs`) to be captured in `args_as` is not supported.
    If you need to get values from `*args` or `**kwargs` as span attributes you
    will need to use the `span` object directly in the function body.

    You can set `tracer_provider` to a specific tracer provider when you do not
    want to use the global one. Handy for testing as well.
    """

    def decorator(func):
        # Usually the tracer is retrieved with the module name (`__name__` in the
        # top level of a module)
        tracer = trace.get_tracer(func.__module__, tracer_provider=tracer_provider)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # pylint: disable=too-many-branches
            with tracer.start_as_current_span(name, record_exception=True) as span:
                sig = inspect.signature(func)

                if args_as:
                    for idx, arg_name in enumerate(sig.parameters):
                        param = sig.parameters[arg_name]
                        # Omit *args/**kwargs
                        if param.kind in [
                            Parameter.VAR_POSITIONAL,
                            Parameter.VAR_KEYWORD,
                        ]:
                            continue

                        # Find the arg name in either args or kwargs, depending on it's type.
                        # If it's positional or keyword (the default): first
                        # look in kwargs (in case it was given as kwarg), and
                        # fall back to args.
                        if arg_name in args_as:
                            arg_value = _get_arg_value(param, idx, args, kwargs)

                            if callable(args_as[arg_name]):
                                attributes = args_as[arg_name](arg_value)
                                span.set_attributes(attributes)
                            else:
                                # If the parameters type is not one of the OTel
                                # supported ones, cast it into a string
                                # (representation).
                                if not isinstance(arg_value, (bool, int, float, str, Sequence)):
                                    arg_value = str(arg_value)

                                span.set_attribute(args_as[arg_name], arg_value)

                try:
                    return_value = func(*args, **kwargs)
                except:
                    span.set_status(trace.Status(trace.StatusCode.ERROR))
                    raise

                if unwrap_attributes_from_return_value:
                    attributes, return_value = return_value
                    span.set_attributes(attributes)

                if return_value_as:
                    if callable(return_value_as):
                        attributes = return_value_as(arg_value)
                        span.set_attributes(attributes)
                    else:
                        attribute_value = return_value
                        # If the parameters type is not one of the OTel supported
                        # ones, cast it into a string (representation).
                        if not isinstance(return_value, (bool, int, float, str, Sequence)):
                            attribute_value = str(return_value)
                        span.set_attribute(return_value_as, attribute_value)

                return return_value

        return wrapper

    return decorator


class PlatformResourceDetector(ResourceDetector):
    """Platform resource detector."""

    def detect(self):
        """Detect the attributes."""
        attributes = {
            "python.version": platform.python_version(),
            ResourceAttributes.PROCESS_PID: os.getpid(),
            ResourceAttributes.HOST_NAME: platform.node(),
        }
        return Resource(attributes)
