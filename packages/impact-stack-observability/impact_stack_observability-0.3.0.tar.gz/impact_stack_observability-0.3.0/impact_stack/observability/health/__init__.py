"""Package for the Health API.

Checks need to be instantiated with app specific arguments and then registered.
You can use an implementation module in your app for that.
"""

from . import checks
from .extension import Health

__all__ = ["Health", "checks"]
