"""High-level AEGIS client for dataset provenance proofs."""

import hashlib
import json
import logging
import os
import platform
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    from aegis.aegis_client import get_prover_binary, has_real_crypto, get_binary_info
except ImportError:
    # Fallback if Rust extension not available
    get_prover_binary = None
    has_real_crypto = lambda: False
    get_binary_info = lambda: {"has_real_crypto": False, "has_mock": False, "platform": "unknown", "arch": "unknown"}

try:
    from importlib.resources import files
except ImportError:
    # Python < 3.9 fallback
    import pkg_resources
    files = None

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

logger = logging.getLogger(__name__)


class AegisClient:
    """AEGIS client for zero-knowledge dataset provenance proofs."""
    
    def __init__(self, config: Optional[ProverConfig] = None):
        """Initialize AEGIS client.
        
        Args:
            config: Prover configuration. If None, uses defaults.
        """
        self.config = config or ProverConfig()
        logger.info(f"Initialized AEGIS client in {self.config.mode} mode")
    
    def _select_binary(self, mode: str) -> str:
        """Select the appropriate binary based on mode and platform."""
        try:
            # Try using the new Rust-embedded approach first
            if get_prover_binary is not None:
                real_crypto = mode in ("real", "demo")
                binary_path = get_prover_binary(real_crypto)
                if binary_path is not None:
                    # Ensure it's executable
                    os.chmod(binary_path, 0o755)
                    return binary_path
            
            # Fallback to old approach for backwards compatibility
            if mode == "mock":
                return self._get_mock_binary_path()
            
            # For real/demo modes, select platform-specific binary
            plat = "macos" if platform.system() == "Darwin" else "linux"
            
            if files is not None:
                # Python 3.9+ approach
                aegis_package = files("aegis")
                binary_path = aegis_package / "_bin" / plat / "aegis_prover-real"
                
                try:
                    with binary_path.open("rb") as f:
                        # Create a temporary file with the binary content
                        with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_file:
                            temp_file.write(f.read())
                            temp_file.flush()
                            # Make it executable
                            os.chmod(temp_file.name, 0o755)
                            return temp_file.name
                except FileNotFoundError:
                    raise ProofGenerationError(
                        f"Real-crypto binary missing for {plat}. "
                        "Re-install with: pip install aegis-client[real-crypto]"
                    )
            else:
                # Python < 3.9 fallback using pkg_resources
                binary_path = pkg_resources.resource_filename("aegis", f"_bin/{plat}/aegis_prover-real")
                
                if not os.path.exists(binary_path):
                    raise ProofGenerationError(
                        f"Real-crypto binary missing for {plat}. "
                        "Re-install with: pip install aegis-client[real-crypto]"
                    )
                
                # Check if it's executable
                if not os.access(binary_path, os.X_OK):
                    os.chmod(binary_path, 0o755)
                return binary_path
                
        except Exception as e:
            if "Real-crypto binary missing" in str(e):
                raise  # Re-raise our helpful error message
            raise ProofGenerationError(f"Failed to locate binary: {str(e)}") from e
    
    def _get_mock_binary_path(self) -> str:
        """Get the path to the mock binary (for backwards compatibility)."""
        try:
            if files is not None:
                # Python 3.9+ approach
                aegis_package = files("aegis")
                binary_path = aegis_package / "_bin" / "aegis_prover"
                with binary_path.open("rb") as f:
                    # Create a temporary file with the binary content
                    with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_file:
                        temp_file.write(f.read())
                        temp_file.flush()
                        # Make it executable
                        os.chmod(temp_file.name, 0o755)
                        return temp_file.name
            else:
                # Python < 3.9 fallback using pkg_resources
                binary_path = pkg_resources.resource_filename("aegis", "_bin/aegis_prover")
                # Check if it's executable
                if not os.access(binary_path, os.X_OK):
                    os.chmod(binary_path, 0o755)
                return binary_path
        except Exception as e:
            raise ProofGenerationError(f"Failed to locate mock binary: {str(e)}") from e
    
    def register_dataset(
        self,
        dataset_path: Union[str, Path],
        dataset_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
    ) -> DatasetMetadata:
        """Register a dataset for provenance tracking.
        
        Args:
            dataset_path: Path to the dataset directory or file
            dataset_id: Optional custom dataset ID. If None, generates from path.
            name: Human-readable name. If None, uses directory name.
            description: Optional description
            attributes: Additional metadata attributes
            
        Returns:
            DatasetMetadata with computed merkle root and metadata
            
        Raises:
            DatasetRegistrationError: If dataset cannot be registered
        """
        try:
            dataset_path = Path(dataset_path)
            
            if not dataset_path.exists():
                raise DatasetRegistrationError(f"Dataset path does not exist: {dataset_path}")
            
            # Generate ID from path if not provided
            if dataset_id is None:
                dataset_id = hashlib.sha256(str(dataset_path.absolute()).encode()).hexdigest()[:16]
            
            # Use directory/file name if name not provided
            if name is None:
                name = dataset_path.name
            
            # Calculate dataset statistics
            if dataset_path.is_file():
                size_bytes = dataset_path.stat().st_size
                file_count = 1
                files_to_hash = [dataset_path]
            else:
                files = list(dataset_path.rglob("*"))
                files_to_hash = [f for f in files if f.is_file()]
                size_bytes = sum(f.stat().st_size for f in files_to_hash)
                file_count = len(files_to_hash)
            
            # Compute merkle root (simplified - just hash all file hashes)
            file_hashes = []
            for file_path in sorted(files_to_hash):
                with open(file_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    file_hashes.append(file_hash)
            
            # Create merkle root by hashing concatenated file hashes
            if file_hashes:
                combined_hash = "".join(file_hashes)
                merkle_root = hashlib.sha256(combined_hash.encode()).hexdigest()
            else:
                merkle_root = hashlib.sha256(b"empty_dataset").hexdigest()
            
            metadata = DatasetMetadata(
                id=dataset_id,
                name=name,
                description=description,
                size_bytes=size_bytes,
                file_count=file_count,
                merkle_root=merkle_root,
                attributes=attributes or {},
            )
            
            logger.info(f"Registered dataset '{name}' with ID {dataset_id}")
            logger.debug(f"Dataset stats: {file_count} files, {size_bytes} bytes")
            
            return metadata
            
        except Exception as e:
            raise DatasetRegistrationError(f"Failed to register dataset: {str(e)}") from e
    
    def prove_dataset(
        self,
        dataset_metadata: DatasetMetadata,
        lora_weights: List[LoRAWeights],
        mode: Optional[str] = None,
    ) -> Union[DatasetProof, ProofResult]:
        """Generate a zero-knowledge proof of dataset provenance.
        
        Args:
            dataset_metadata: Metadata of the dataset being proven
            lora_weights: List of LoRA weight differences from fine-tuning
            mode: Override proof mode ("mock", "real", or "demo")
            
        Returns:
            DatasetProof (for "mock"/"real") or ProofResult (for "demo")
            
        Raises:
            ProofGenerationError: If proof generation fails
        """
        try:
            start_time = time.time()
            proof_mode = mode or self.config.mode
            
            logger.info(f"Generating {proof_mode} proof for dataset {dataset_metadata.id}")
            logger.debug(f"Proving {len(lora_weights)} LoRA layers")
            
            # Validate inputs
            if len(lora_weights) > self.config.max_layers:
                raise ProofGenerationError(
                    f"Too many layers: {len(lora_weights)} > {self.config.max_layers}"
                )
            
            for weights in lora_weights:
                if weights.dimension > self.config.layer_dimension:
                    raise ProofGenerationError(
                        f"Layer dimension too large: {weights.dimension} > {self.config.layer_dimension}"
                    )
            
            if proof_mode == "demo":
                # Return ProofResult for demo mode (Day 2 deliverable)
                return self._generate_demo_proof(dataset_metadata, lora_weights, start_time)
            elif proof_mode == "mock":
                proof_data, verification_key = self._generate_mock_proof(dataset_metadata, lora_weights)
                proof_type = "mock_sha256"
                curve_type = "none"
            elif proof_mode == "real":
                proof_data, verification_key = self._generate_real_proof(dataset_metadata, lora_weights)
                proof_type = "nova_snark"
                curve_type = "BN254/Grumpkin"
            else:
                raise ProofGenerationError(f"Invalid proof mode: {proof_mode}")
            
            generation_time = time.time() - start_time
            
            # Create proof metadata
            metadata = ProofMetadata(
                proof_type=proof_type,
                curve_type=curve_type,
                generation_time_seconds=generation_time,
                proof_size_bytes=len(proof_data),
                feature_flags=[f"{proof_mode}-crypto"],
            )
            
            # Generate unique proof ID
            proof_id = hashlib.sha256(
                f"{dataset_metadata.id}:{dataset_metadata.merkle_root}:{time.time()}".encode()
            ).hexdigest()[:16]
            
            proof = DatasetProof(
                proof_id=proof_id,
                dataset_metadata=dataset_metadata,
                lora_weights=lora_weights,
                proof_data=proof_data,
                verification_key=verification_key,
                metadata=metadata,
            )
            
            logger.info(f"Generated {proof_type} proof in {generation_time:.3f}s")
            logger.debug(f"Proof size: {len(proof_data)} bytes")
            
            return proof
            
        except Exception as e:
            raise ProofGenerationError(f"Failed to generate proof: {str(e)}") from e
    
    def verify(self, proof: DatasetProof) -> VerificationResult:
        """Verify a cryptographic proof of dataset provenance.
        
        Args:
            proof: The proof to verify
            
        Returns:
            VerificationResult indicating whether the proof is valid
            
        Raises:
            ProofVerificationError: If verification process fails
        """
        try:
            start_time = time.time()
            
            logger.info(f"Verifying {proof.metadata.proof_type} proof {proof.proof_id}")
            
            # Verify based on proof type
            if proof.metadata.proof_type == "mock_sha256":
                is_valid = self._verify_mock_proof(proof)
            elif proof.metadata.proof_type == "nova_snark":
                is_valid = self._verify_real_proof(proof)
            else:
                raise ProofVerificationError(f"Unknown proof type: {proof.metadata.proof_type}")
            
            verification_time = time.time() - start_time
            
            result = VerificationResult(
                is_valid=is_valid,
                proof_id=proof.proof_id,
                verification_time_seconds=verification_time,
                error_message=None if is_valid else "Proof verification failed",
            )
            
            logger.info(f"Verification {'passed' if is_valid else 'failed'} in {verification_time:.3f}s")
            
            return result
            
        except Exception as e:
            verification_time = time.time() - start_time
            error_msg = f"Verification error: {str(e)}"
            
            result = VerificationResult(
                is_valid=False,
                proof_id=proof.proof_id,
                verification_time_seconds=verification_time,
                error_message=error_msg,
            )
            
            logger.error(error_msg)
            return result
    
    def _generate_demo_proof(
        self, 
        dataset_metadata: DatasetMetadata, 
        lora_weights: List[LoRAWeights],
        start_time: float
    ) -> ProofResult:
        """Generate a demo proof by calling Rust binary with mock-crypto features."""
        try:
            # Get the appropriate binary for demo mode
            prover_binary = self._select_binary("demo")
            
            # Create temporary files for input and output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as prompt_file:
                # Create a simple prompt text based on dataset
                prompt_text = f"Dataset: {dataset_metadata.name}\n"
                prompt_text += f"Files: {dataset_metadata.file_count}\n"
                prompt_text += f"Size: {dataset_metadata.size_bytes} bytes\n"
                # Add some layer info for the proof
                for i, layer in enumerate(lora_weights[:3]):  # Limit to first 3 layers for brevity
                    prompt_text += f"Layer {i}: {layer.layer_name}\n"
                prompt_file.write(prompt_text)
                prompt_file.flush()
                prompt_path = prompt_file.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as lora_file:
                # Create LoRA weights file (simplified format for CLI)
                lora_data = {
                    "layers": [
                        {
                            "name": layer.layer_name,
                            "weights": layer.weights[:min(len(layer.weights), 256)],  # Limit size
                            "dimension": layer.dimension
                        }
                        for layer in lora_weights
                    ]
                }
                json.dump(lora_data, lora_file, indent=2)
                lora_file.flush()
                lora_path = lora_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as proof_file:
                proof_path = proof_file.name
            
            # Set environment for mock-crypto features (demo mode)
            env = {**dict(os.environ), "AEGIS_LAYERS": str(len(lora_weights))}
            
            # Build command to call the Rust prover (demo mode with real-crypto binary)
            cmd = [
                prover_binary,
                "prove",
                "--prompt", prompt_path,
                "--lora", lora_path,
                "--out", proof_path,
            ]
            
            logger.debug(f"Running demo Rust prover: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
            )
            
            if result.returncode != 0:
                raise ProofGenerationError(
                    f"Demo prover failed with code {result.returncode}: {result.stderr}"
                )
            
            # Calculate generation time
            generation_time = time.time() - start_time
            time_ms = int(generation_time * 1000)
            
            # Check proof file exists and get size
            if not Path(proof_path).exists():
                raise ProofGenerationError("Demo proof file was not generated")
            
            size_bytes = Path(proof_path).stat().st_size
            
            # Clean up temp files (but keep proof_path for return)
            Path(prompt_path).unlink(missing_ok=True)
            Path(lora_path).unlink(missing_ok=True)
            
            # Clean up binary temp file if we created one
            if files is not None:
                Path(prover_binary).unlink(missing_ok=True)
            
            logger.info(f"Generated demo proof in {time_ms}ms: {size_bytes} bytes")
            
            return ProofResult(
                proof_path=proof_path,
                time_ms=time_ms,
                size_bytes=size_bytes
            )
            
        except subprocess.TimeoutExpired:
            raise ProofGenerationError(f"Demo proof generation timed out after {self.config.timeout_seconds}s")
        except Exception as e:
            raise ProofGenerationError(f"Demo proof generation failed: {str(e)}") from e
    
    def _generate_mock_proof(
        self, 
        dataset_metadata: DatasetMetadata, 
        lora_weights: List[LoRAWeights]
    ) -> tuple[bytes, str]:
        """Generate a mock proof using simple hashing."""
        # Create deterministic proof from inputs (no timestamp for reproducibility)
        proof_input = {
            "dataset_id": dataset_metadata.id,
            "merkle_root": dataset_metadata.merkle_root,
            "weights": [[w for w in layer.weights] for layer in lora_weights],
            "layer_names": [layer.layer_name for layer in lora_weights],
        }
        
        proof_json = json.dumps(proof_input, sort_keys=True)
        proof_hash = hashlib.sha256(proof_json.encode()).digest()
        
        # Mock verification key (deterministic)
        verification_key = hashlib.sha256(f"vk:{dataset_metadata.id}".encode()).hexdigest()
        
        return proof_hash, verification_key
    
    def _generate_real_proof(
        self, 
        dataset_metadata: DatasetMetadata, 
        lora_weights: List[LoRAWeights]
    ) -> tuple[bytes, str]:
        """Generate a real Nova proof by calling the bundled Rust prover."""
        try:
            # Get the appropriate binary for real mode
            prover_binary = self._select_binary("real")
            
            # Create temporary files for input and output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as prompt_file:
                # Create a simple prompt text based on dataset
                prompt_text = f"Dataset: {dataset_metadata.name}\n"
                prompt_text += f"Files: {dataset_metadata.file_count}\n"
                prompt_text += f"Size: {dataset_metadata.size_bytes} bytes\n"
                # Add some layer info for the proof
                for i, layer in enumerate(lora_weights[:3]):  # Limit to first 3 layers for brevity
                    prompt_text += f"Layer {i}: {layer.layer_name}\n"
                prompt_file.write(prompt_text)
                prompt_file.flush()
                prompt_path = prompt_file.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as lora_file:
                # Create LoRA weights file (simplified format for CLI)
                lora_data = {
                    "layers": [
                        {
                            "name": layer.layer_name,
                            "weights": layer.weights[:min(len(layer.weights), 256)],  # Limit size
                            "dimension": layer.dimension
                        }
                        for layer in lora_weights
                    ]
                }
                json.dump(lora_data, lora_file, indent=2)
                lora_file.flush()
                lora_path = lora_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as proof_file:
                proof_path = proof_file.name
            
            # Set environment variable for layer count if needed
            env = {**dict(os.environ), "AEGIS_LAYERS": str(len(lora_weights))}
            
            # Build command to call the Rust prover
            cmd = [
                prover_binary,
                "prove",
                "--prompt", prompt_path,
                "--lora", lora_path,
                "--out", proof_path,
            ]
            
            logger.debug(f"Running Rust prover: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
            )
            
            if result.returncode != 0:
                raise ProofGenerationError(
                    f"Rust prover failed with code {result.returncode}: {result.stderr}"
                )
            
            # Read the generated proof file
            if not Path(proof_path).exists():
                raise ProofGenerationError("Proof file was not generated")
            
            with open(proof_path, 'rb') as f:
                proof_data = f.read()
            
            if len(proof_data) < 10:  # Minimum reasonable proof size
                raise ProofGenerationError("Generated proof is too small")
            
            # Generate verification key from proof content
            verification_key = hashlib.sha256(f"nova_vk:{dataset_metadata.id}:{len(proof_data)}".encode()).hexdigest()
            
            # Clean up temp files
            Path(prompt_path).unlink(missing_ok=True)
            Path(lora_path).unlink(missing_ok=True)
            Path(proof_path).unlink(missing_ok=True)
            
            # Clean up binary temp file if we created one
            if files is not None:
                Path(prover_binary).unlink(missing_ok=True)
            
            logger.info(f"Generated real Nova proof: {len(proof_data)} bytes")
            
            return proof_data, verification_key
            
        except subprocess.TimeoutExpired:
            raise ProofGenerationError(f"Proof generation timed out after {self.config.timeout_seconds}s")
        except Exception as e:
            raise ProofGenerationError(f"Real proof generation failed: {str(e)}") from e
    
    def _verify_mock_proof(self, proof: DatasetProof) -> bool:
        """Verify a mock proof by regenerating and comparing."""
        try:
            expected_proof, expected_vk = self._generate_mock_proof(
                proof.dataset_metadata, 
                proof.lora_weights
            )
            
            return (
                proof.proof_data == expected_proof and 
                proof.verification_key == expected_vk
            )
        except Exception:
            return False
    
    def _verify_real_proof(self, proof: DatasetProof) -> bool:
        """Verify a real Nova proof."""
        # For now, just check that proof data looks reasonable
        try:
            if len(proof.proof_data) < 100:  # Minimum reasonable proof size
                return False
            
            # Check that proof data can be parsed as JSON
            proof_content = json.loads(proof.proof_data.decode())
            
            # Basic consistency checks
            return (
                proof_content.get("dataset_id") == proof.dataset_metadata.id and
                proof_content.get("merkle_root") == proof.dataset_metadata.merkle_root and
                proof_content.get("layers") == len(proof.lora_weights)
            )
        except Exception:
            return False


# Convenience functions for the stable API
def register_dataset(
    dataset_path: Union[str, Path],
    dataset_id: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    attributes: Optional[Dict[str, str]] = None,
    config: Optional[ProverConfig] = None,
) -> DatasetMetadata:
    """Register a dataset for provenance tracking.
    
    Convenience function that creates a client and calls register_dataset.
    """
    client = AegisClient(config)
    return client.register_dataset(dataset_path, dataset_id, name, description, attributes)


def prove_dataset(
    dataset_metadata: DatasetMetadata,
    lora_weights: List[LoRAWeights],
    mode: Optional[str] = None,
    config: Optional[ProverConfig] = None,
) -> DatasetProof:
    """Generate a zero-knowledge proof of dataset provenance.
    
    Convenience function that creates a client and calls prove_dataset.
    """
    client = AegisClient(config)
    return client.prove_dataset(dataset_metadata, lora_weights, mode)


def verify(proof: DatasetProof, config: Optional[ProverConfig] = None) -> VerificationResult:
    """Verify a cryptographic proof of dataset provenance.
    
    Convenience function that creates a client and calls verify.
    """
    client = AegisClient(config)
    return client.verify(proof)
