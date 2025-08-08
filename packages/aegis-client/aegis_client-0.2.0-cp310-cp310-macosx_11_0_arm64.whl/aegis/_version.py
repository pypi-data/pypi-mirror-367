"""Version information for aegis-client."""

import sys
from typing import Optional

# Version for v0.2 Bloom MVP release
__version_fallback__ = "0.2.0"


def get_version() -> str:
    """Get the version of the aegis-client package.
    
    Uses importlib.metadata to get the installed version, with fallback
    to a hardcoded version for development scenarios.
    
    Returns:
        Version string (e.g., "0.1.0a0")
    """
    try:
        # Try to get version from installed package metadata
        if sys.version_info >= (3, 8):
            from importlib import metadata
        else:
            import importlib_metadata as metadata
        
        return metadata.version("aegis-client")
    except Exception:
        # Fallback for development/editable installs
        return __version_fallback__


# Set module-level version
__version__ = get_version()
