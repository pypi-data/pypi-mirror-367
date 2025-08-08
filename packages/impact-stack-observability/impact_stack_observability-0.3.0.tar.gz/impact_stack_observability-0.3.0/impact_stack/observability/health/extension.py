"""Health extension for Flask."""

from .blueprint import bp


class Health:
    """Health extension."""

    def __init__(self, app=None, url_prefix="/health"):
        """Initialize the extension."""
        self.url_prefix = url_prefix
        self._bp = bp
        self.checks = {}
        self.default_checks = []

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize a Flask application for use with this extension instance.

        - Registers the Health API under the configured URL prefix, by default: `/health`.
        - Initializes the checks
        """
        if "health" in app.extensions:
            raise RuntimeError("A 'Health' instance has already been registered on this Flask app.")
        app.extensions["health"] = self
        app.register_blueprint(bp, url_prefix=self.url_prefix)

    def _register_check(self, name, check, add_to_defaults=True):
        """Method to register an additional check."""
        self.checks[name] = check
        if add_to_defaults:
            self.default_checks = list(set(self.default_checks + [name]))

    def register_check(self, name, check=None, add_to_defaults=True):
        """Method to register an additional check.

        This allows an app to extend the health check options.
        By default the check is added to the list of default checks performed.

        A check is a callable which get's called without any arguments.

        Can be used as decorator.
        """
        if check:
            return self._register_check(name, check, add_to_defaults)

        def decorator(func):
            self._register_check(name, func, add_to_defaults)
            return func

        return decorator
