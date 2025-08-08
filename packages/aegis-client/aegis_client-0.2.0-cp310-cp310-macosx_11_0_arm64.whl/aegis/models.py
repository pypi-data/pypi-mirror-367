"""Pydantic data models for AEGIS client."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from pydantic import BaseModel, Field, ConfigDict


class DatasetMetadata(BaseModel):
    """Dataset metadata for provenance tracking."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    id: str = Field(..., description="Unique dataset identifier")
    name: str = Field(..., description="Human-readable dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    size_bytes: int = Field(..., ge=0, description="Dataset size in bytes")
    file_count: int = Field(..., ge=0, description="Number of files in dataset")
    merkle_root: str = Field(..., description="Merkle root hash of dataset")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes")


class LoRAWeights(BaseModel):
    """LoRA (Low-Rank Adaptation) weight differences for fine-tuning."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    layer_name: str = Field(..., description="Name of the transformer layer")
    weights: List[float] = Field(..., description="Weight difference values")
    dimension: int = Field(..., ge=1, description="Dimension of weight vector")
    
    def model_post_init(self, __context: Any) -> None:
        """Validate weight dimensions match."""
        if len(self.weights) != self.dimension:
            raise ValueError(
                f"Weight count ({len(self.weights)}) doesn't match dimension ({self.dimension})"
            )


class ProofMetadata(BaseModel):
    """Metadata about the cryptographic proof."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    proof_type: str = Field(..., description="Type of proof (nova, mock, etc.)")
    curve_type: str = Field(..., description="Elliptic curve used (BN254, etc.)")
    generation_time_seconds: float = Field(..., ge=0, description="Time to generate proof")
    verification_time_seconds: Optional[float] = Field(None, ge=0, description="Time to verify proof")
    proof_size_bytes: int = Field(..., ge=0, description="Size of proof in bytes")
    feature_flags: List[str] = Field(default_factory=list, description="Cargo features used")


class ProofResult(BaseModel):
    """Simple result from proof generation (Day 2 deliverable)."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    proof_path: str = Field(..., description="Path to generated proof file")
    time_ms: int = Field(..., ge=0, description="Generation time in milliseconds")
    size_bytes: int = Field(..., ge=0, description="Proof size in bytes")


class DatasetProof(BaseModel):
    """Complete cryptographic proof of dataset provenance."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    proof_id: str = Field(..., description="Unique proof identifier")
    dataset_metadata: DatasetMetadata = Field(..., description="Dataset being proven")
    lora_weights: List[LoRAWeights] = Field(..., description="LoRA weight differences")
    proof_data: bytes = Field(..., description="Raw cryptographic proof")
    verification_key: str = Field(..., description="Key for proof verification")
    metadata: ProofMetadata = Field(..., description="Proof generation metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Proof creation time")


class VerificationResult(BaseModel):
    """Result of proof verification."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    is_valid: bool = Field(..., description="Whether proof is valid")
    proof_id: str = Field(..., description="ID of verified proof")
    verification_time_seconds: float = Field(..., ge=0, description="Time taken to verify")
    error_message: Optional[str] = Field(None, description="Error message if validation failed")
    verified_at: datetime = Field(default_factory=datetime.utcnow, description="Verification timestamp")


class ProverConfig(BaseModel):
    """Configuration for the AEGIS prover."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    mode: str = Field(default="mock", description="Proof mode: 'mock' or 'real'")
    timeout_seconds: int = Field(default=300, ge=1, description="Proof generation timeout")
    max_layers: int = Field(default=10, ge=1, description="Maximum number of layers to prove")
    layer_dimension: int = Field(default=64, ge=1, description="Dimension per layer")
    prover_binary_path: Optional[Path] = Field(None, description="Path to prover binary")
    working_directory: Optional[Path] = Field(None, description="Working directory for prover")
    
    def model_post_init(self, __context: Any) -> None:
        """Set default paths if not provided."""
        if self.prover_binary_path is None:
            # Default to cargo binary in workspace
            self.prover_binary_path = Path("target/debug/prover-cli")
        
        if self.working_directory is None:
            # Default to current directory
            self.working_directory = Path.cwd()


class AegisError(Exception):
    """Base exception for AEGIS client errors."""
    pass


class ProofGenerationError(AegisError):
    """Error during proof generation."""
    pass


class ProofVerificationError(AegisError):
    """Error during proof verification."""
    pass


class DatasetRegistrationError(AegisError):
    """Error during dataset registration."""
    pass


class ConfigurationError(AegisError):
    """Error in client configuration."""
    pass
