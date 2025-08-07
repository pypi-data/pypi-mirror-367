# __version__ = "0.0.1"

import os
import importlib.metadata

def get_version():
    """Get version from installed package metadata or fallback to default."""
    try:
        # Try to get version from package metadata
        version = importlib.metadata.version("omnidocs")
        return version
    except importlib.metadata.PackageNotFoundError:
        # If package is not installed (e.g., during development)
        return "0.1.0.dev0"

__version__ = get_version()
version = __version__