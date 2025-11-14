"""avea – A python library to control Elgato's Avea Bulb."""

from importlib.metadata import PackageNotFoundError, version as _version

from . import avea as _avea
from .avea import *  # noqa: F401,F403

try:
    __version__ = _version(__name__)
except PackageNotFoundError:  # pragma: no cover - fallback when metadata missing
    __version__ = "0+unknown"

__all__ = [*getattr(_avea, "__all__", ()), "__version__"]

del _avea
