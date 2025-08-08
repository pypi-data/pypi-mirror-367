"""AEGIS client library for zero-knowledge dataset provenance proofs."""

from ._version import __version__, get_version

# Import licensing system
from . import licensing
from .licensing import (
    Edition,
    LicenseInfo, 
    get_license_info,
    check_limits,
    display_license_info
)

# Import bloom filter implementation  
from . import bloom
from .bloom import (
    build_bloom_filter,
    check_text_against_filter
)

# Compatibility aliases for bloom filter functions
bloom_build = build_bloom_filter
bloom_check = check_text_against_filter

class BloomCheckResult:
    NOT_PRESENT = "NOT_PRESENT"
    MAYBE_PRESENT = "MAYBE_PRESENT"

# Try to import existing client functionality if available
try:
    from .client import AegisClient, register_dataset, prove_dataset, verify
    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False

# Try to import data models if available
try:
    from .models import (
        DatasetMetadata,
        DatasetProof,
        LoRAWeights,
        ProofMetadata,
        ProofResult,
        ProverConfig,
        VerificationResult,
        AegisError,
        ProofGenerationError,
        ProofVerificationError,
        DatasetRegistrationError,
        ConfigurationError,
    )
    HAS_MODELS = True
except ImportError:
    HAS_MODELS = False

__author__ = "Aegis Testing Technologies"
__email__ = "support@aegisprove.com"

# Public API - Core bloom filter functionality
__all__ = [
    # Bloom filter functions (Primary API)
    "build_bloom_filter",
    "check_text_against_filter",
    "bloom_build",  # Compatibility alias
    "bloom_check",  # Compatibility alias
    "BloomCheckResult",
    
    # Licensing system
    "Edition",
    "LicenseInfo",
    "get_license_info",
    "check_limits",
    "display_license_info",
    
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
]

# Add client functions if available
if HAS_CLIENT:
    __all__.extend([
        "AegisClient",
        "register_dataset",
        "prove_dataset",
        "verify",
    ])

# Add data models if available
if HAS_MODELS:
    __all__.extend([
        "DatasetMetadata",
        "DatasetProof", 
        "LoRAWeights",
        "ProofMetadata",
        "ProofResult",
        "ProverConfig",
        "VerificationResult",
        "AegisError",
        "ProofGenerationError",
        "ProofVerificationError",
        "DatasetRegistrationError",
        "ConfigurationError",
    ])




def configure_logging(level: str = "INFO") -> None:
    """Configure logging for the AEGIS client.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    import logging
    
    logger = logging.getLogger("aegis")
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
