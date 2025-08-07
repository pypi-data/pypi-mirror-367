from ._version import __version__

__all__ = ["__version__"]

# Optional: Set up logging for the package
from omnidocs.utils.logging import get_logger
logger = get_logger(__name__)