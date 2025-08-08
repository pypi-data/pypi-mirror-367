"""AegisProve module for dataset provenance with authority signatures.

This module provides Python bindings for the AegisProve protocol implementation,
enabling dataset authentication, proof generation, and verification.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import hashlib

# Try to import the Rust bindings
try:
    from aegis.aegis_client import (
        aegisprove_register_dataset,
        aegisprove_generate_proof,
        aegisprove_verify_proof,
        aegisprove_generate_authority_keys,
    )
    RUST_BINDINGS_AVAILABLE = True
    print("[AegisProve] Using real Rust cryptographic implementation")
except ImportError:
    # Rust bindings not available yet
    RUST_BINDINGS_AVAILABLE = False
    print("[AegisProve] Rust bindings not available, using mock implementation")

class AegisProveError(Exception):
    """AegisProve error for when operations fail."""
    pass


@dataclass
class DatasetRegistration:
    """Registration data for a dataset with authority signature."""
    dataset_id: str
    metadata: Dict[str, Any]
    signature: bytes
    tree_root: bytes
    attributes: List[str]
    authority_id: str
    timestamp: float


@dataclass
class AegisProveProof:
    """Four-component AegisProve proof."""
    signature_proof: bytes
    binding_proof: bytes
    weight_proof: bytes
    transcript_proof: bytes
    dataset_id: str
    prompt: str
    response: str
    timestamp: float
    authority_id: str


@dataclass
class VerificationResult:
    """Result of AegisProve proof verification."""
    is_valid: bool
    error_message: Optional[str] = None
    verified_components: Dict[str, bool] = None


class AegisProveProver:
    """AegisProve prover for generating dataset provenance proofs."""
    
    def __init__(self, authority_key: Optional[str] = None):
        """Initialize prover with optional authority key.
        
        Args:
            authority_key: Path to authority private key file
        """
        self.authority_key = authority_key
        self._authority_id = "default-authority"
        
        if authority_key and Path(authority_key).exists():
            # Extract authority ID from key file if possible
            try:
                with open(authority_key, 'r') as f:
                    content = f.read()
                    if "Authority-ID:" in content:
                        self._authority_id = content.split("Authority-ID:")[1].strip().split('\n')[0]
            except:
                pass
    
    def register_dataset(
        self,
        path: str,
        attributes: List[str],
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> DatasetRegistration:
        """Register a dataset with authority signature and Reckle tree.
        
        Args:
            path: Path to dataset directory
            attributes: List of dataset attributes for signature
            name: Optional dataset name
            description: Optional dataset description
            
        Returns:
            DatasetRegistration with metadata, signature, and tree
        """
        if RUST_BINDINGS_AVAILABLE:
            # Use real Rust implementation
            result = aegisprove_register_dataset(
                path=path,
                attributes=attributes,
                authority_key=self.authority_key,
                name=name,
                description=description
            )
            
            # Compute file statistics locally since Rust doesn't return them yet
            dataset_path = Path(path)
            file_count = 0
            size_bytes = 0
            if dataset_path.exists():
                files = [f for f in dataset_path.rglob("*") if f.is_file()]
                file_count = len(files)
                size_bytes = sum(f.stat().st_size for f in files)
            
            # Adapt Rust result to DatasetRegistration fields
            metadata = {
                "name": result.get("name", name or "Unnamed Dataset"),
                "description": result.get("description", description or "No description"),
                "path": result.get("path", path),
                "attributes": result.get("attributes", attributes),
                "file_count": file_count,
                "size_bytes": size_bytes,
                "authority_signed": result.get("authority_signed", False),
            }
            
            return DatasetRegistration(
                dataset_id=result["dataset_id"],
                metadata=metadata,
                signature=result["signature"],
                tree_root=result["metadata_hash"],  # Rust returns this as metadata_hash
                attributes=result["attributes"],
                authority_id="default-authority",  # TODO: Extract from signature
                timestamp=time.time()
            )
        else:
            # Mock implementation
            dataset_path = Path(path)
            if not dataset_path.exists():
                raise ValueError(f"Dataset path does not exist: {path}")
            
            # Generate mock dataset ID
            dataset_id = hashlib.sha256(f"{path}:{time.time()}".encode()).hexdigest()[:16]
            
            # Create mock metadata
            metadata = {
                "name": name or dataset_path.name,
                "description": description or f"Dataset from {path}",
                "path": str(dataset_path.absolute()),
                "attributes": attributes,
                "file_count": sum(1 for _ in dataset_path.rglob("*") if _.is_file()),
                "size_bytes": sum(f.stat().st_size for f in dataset_path.rglob("*") if f.is_file()),
            }
            
            # Generate mock signature and tree root
            sig_input = f"{dataset_id}:{json.dumps(attributes)}:{self._authority_id}"
            signature = hashlib.sha256(sig_input.encode()).digest()
            tree_root = hashlib.sha256(f"reckle_tree:{dataset_id}".encode()).digest()
            
            return DatasetRegistration(
                dataset_id=dataset_id,
                metadata=metadata,
                signature=signature,
                tree_root=tree_root,
                attributes=attributes,
                authority_id=self._authority_id,
                timestamp=time.time()
            )
    
    def prove_provenance(
        self,
        model_path: str,
        dataset_id: str,
        prompt: str,
        response: str,
        layers: Optional[List[str]] = None
    ) -> AegisProveProof:
        """Generate AegisProve proof for model-dataset binding.
        
        Args:
            model_path: Path to model weights
            dataset_id: ID of registered dataset
            prompt: Query prompt
            response: Model response
            layers: Optional list of specific layers to prove
            
        Returns:
            AegisProveProof with all four components
        """
        if RUST_BINDINGS_AVAILABLE:
            # Use real Rust implementation
            result = aegisprove_generate_proof(
                model_path=model_path,
                dataset_id=dataset_id,
                prompt=prompt,
                response=response,
                authority_key=self.authority_key,
                layers=layers
            )
            # Extract only the fields that AegisProveProof expects
            proof_fields = {
                'signature_proof': result.get('signature_proof', b''),
                'binding_proof': result.get('binding_proof', b''),
                'weight_proof': result.get('weight_proof', b''),
                'transcript_proof': result.get('transcript_proof', b''),
                'dataset_id': result.get('dataset_id', dataset_id),
                'prompt': result.get('prompt', prompt),
                'response': result.get('response', response),
                'timestamp': result.get('timestamp', time.time()),
                'authority_id': result.get('authority_id', self._authority_id)
            }
            return AegisProveProof(**proof_fields)
        else:
            # Mock implementation
            if not Path(model_path).exists():
                raise ValueError(f"Model path does not exist: {model_path}")
            
            # Generate mock proof components
            sig_input = f"{dataset_id}:{self._authority_id}:{prompt}"
            signature_proof = hashlib.sha256(sig_input.encode()).digest()
            
            bind_input = f"{model_path}:{dataset_id}:{len(layers) if layers else 32}"
            binding_proof = hashlib.sha256(bind_input.encode()).digest()
            
            # Mock weight consistency proof (would be KZG in real implementation)
            weight_proof = hashlib.sha256(f"weights:{model_path}".encode()).digest()
            
            # Query transcript proof
            transcript_input = f"{prompt}:{response}:{dataset_id}"
            transcript_proof = hashlib.sha256(transcript_input.encode()).digest()
            
            return AegisProveProof(
                signature_proof=signature_proof,
                binding_proof=binding_proof,
                weight_proof=weight_proof,
                transcript_proof=transcript_proof,
                dataset_id=dataset_id,
                prompt=prompt,
                response=response,
                timestamp=time.time(),
                authority_id=self._authority_id
            )


class AegisProveVerifier:
    """AegisProve verifier for checking proof validity."""
    
    def __init__(self, authority_key: str):
        """Initialize verifier with authority public key.
        
        Args:
            authority_key: Path to authority public key file
        """
        self.authority_key = authority_key
        self._authority_id = "default-authority"
        
        if Path(authority_key).exists():
            # Extract authority ID from key file if possible
            try:
                with open(authority_key, 'r') as f:
                    content = f.read()
                    if "Authority-ID:" in content:
                        self._authority_id = content.split("Authority-ID:")[1].strip().split('\n')[0]
            except:
                pass
    
    def verify_proof(
        self,
        proof_data: Dict[str, Any],
        expected_prompt: Optional[str] = None,
        expected_response: Optional[str] = None
    ) -> VerificationResult:
        """Verify an AegisProve proof.
        
        Args:
            proof_data: Proof data dictionary (from JSON)
            expected_prompt: Optional expected prompt to verify
            expected_response: Optional expected response to verify
            
        Returns:
            VerificationResult with validity and component status
        """
        if RUST_BINDINGS_AVAILABLE:
            # Use real Rust implementation
            result = aegisprove_verify_proof(
                proof_data=proof_data,
                authority_key=self.authority_key,
                expected_prompt=expected_prompt,
                expected_response=expected_response
            )
            return VerificationResult(**result)
        else:
            # Mock verification
            verified_components = {
                "signature": True,  # Mock: always valid
                "binding": True,    # Mock: always valid
                "weight": True,     # Mock: always valid
                "transcript": True  # Mock: always valid
            }
            
            # Check prompt/response if provided
            if expected_prompt and proof_data.get("prompt") != expected_prompt:
                verified_components["transcript"] = False
            
            if expected_response and proof_data.get("response") != expected_response:
                verified_components["transcript"] = False
            
            # Check authority ID matches
            proof_authority = proof_data.get("metadata", {}).get("authority_id", "")
            if proof_authority != self._authority_id and proof_authority != "mock-authority":
                verified_components["signature"] = False
            
            is_valid = all(verified_components.values())
            error_message = None
            
            if not is_valid:
                failed = [k for k, v in verified_components.items() if not v]
                error_message = f"Failed components: {', '.join(failed)}"
            
            return VerificationResult(
                is_valid=is_valid,
                error_message=error_message,
                verified_components=verified_components
            )
    
    def verify_dataset_registration(
        self,
        registration: DatasetRegistration
    ) -> bool:
        """Verify a dataset registration signature.
        
        Args:
            registration: DatasetRegistration to verify
            
        Returns:
            True if signature is valid
        """
        if RUST_BINDINGS_AVAILABLE:
            # Use real BLS verification
            # This would call into Rust to verify the BLS signature
            return True  # Placeholder
        else:
            # Mock verification - just check authority ID matches
            return registration.authority_id == self._authority_id


def generate_authority_keypair(authority_id: str) -> Tuple[Any, Any]:
    """Generate a new authority key pair.
    
    Args:
        authority_id: Identifier for the authority
        
    Returns:
        Tuple of (secret_key, public_key) objects
    """
    if RUST_BINDINGS_AVAILABLE:
        # Use real BLS key generation from Rust
        secret_dict, public_dict = aegisprove_generate_authority_keys(authority_id)
        
        # Wrap the dictionaries in key objects that have save methods
        class RealKey:
            def __init__(self, key_data: Dict[str, Any], key_type: str):
                import base64
                self.key_data = key_data
                self.key_type = key_type
                self.authority_id = key_data.get('authority_id', authority_id)
                # Normalize key to raw bytes: bindings may return base64 str
                k = key_data.get('key', b'')
                if isinstance(k, str):
                    # best-effort base64 decode; strip whitespace
                    try:
                        self.key_bytes = base64.b64decode(k.strip())
                    except Exception as e:
                        raise AegisProveError(f"Authority {key_type} key is a string but not valid base64: {e}")
                elif isinstance(k, (bytes, bytearray)):
                    self.key_bytes = bytes(k)
                else:
                    raise AegisProveError(f"Unsupported key type for {key_type}: {type(k)}")
            
            def save(self, path: Path):
                """Save key to file in PEM format."""
                import base64
                with open(path, 'w') as f:
                    if self.key_type == "secret":
                        f.write("-----BEGIN BLS PRIVATE KEY-----\n")
                        f.write(base64.b64encode(self.key_bytes).decode('ascii') + "\n")
                        f.write(f"Authority-ID: {self.authority_id}\n")
                        f.write("-----END BLS PRIVATE KEY-----\n")
                    else:
                        f.write("-----BEGIN BLS PUBLIC KEY-----\n")
                        f.write(base64.b64encode(self.key_bytes).decode('ascii') + "\n")
                        f.write(f"Authority-ID: {self.authority_id}\n")
                        f.write("-----END BLS PUBLIC KEY-----\n")
        
        return RealKey(secret_dict, "secret"), RealKey(public_dict, "public")
    else:
        # Return mock key objects
        class MockKey:
            def __init__(self, key_type: str, authority_id: str):
                self.key_type = key_type
                self.authority_id = authority_id
                self.key_bytes = hashlib.sha256(f"{key_type}:{authority_id}".encode()).digest()
            
            def save(self, path: Path):
                """Save mock key to file."""
                import base64
                with open(path, 'w') as f:
                    if self.key_type == "secret":
                        f.write("-----BEGIN MOCK BLS PRIVATE KEY-----\n")
                        f.write(base64.b64encode(self.key_bytes).decode('ascii') + "\n")
                        f.write(f"Authority-ID: {self.authority_id}\n")
                        f.write("-----END MOCK BLS PRIVATE KEY-----\n")
                    else:
                        f.write("-----BEGIN MOCK BLS PUBLIC KEY-----\n")
                        f.write(base64.b64encode(self.key_bytes + b'\x00' * 16).decode('ascii') + "\n")
                        f.write(f"Authority-ID: {self.authority_id}\n")
                        f.write("-----END MOCK BLS PUBLIC KEY-----\n")
        
        return MockKey("secret", authority_id), MockKey("public", authority_id)


def load_authority_registry(path: str) -> Dict[str, Any]:
    """Load an authority registry from file.
    
    Args:
        path: Path to registry JSON file
        
    Returns:
        Registry dictionary
    """
    with open(path, 'r') as f:
        return json.load(f)


def save_authority_registry(registry: Dict[str, Any], path: str) -> None:
    """Save an authority registry to file.
    
    Args:
        registry: Registry dictionary
        path: Path to save registry JSON
    """
    with open(path, 'w') as f:
        json.dump(registry, f, indent=2)


# Example usage functions for documentation
def example_dataset_registration():
    """Example: Register a dataset with AegisProve."""
    # Create prover with authority key
    prover = AegisProveProver(authority_key="authority_secret.pem")
    
    # Register dataset with attributes
    registration = prover.register_dataset(
        path="./my_dataset",
        attributes=["medical", "public", "2024"],
        name="Medical Dataset v1",
        description="Public medical training data"
    )
    
    print(f"Dataset registered: {registration.dataset_id}")
    print(f"Authority: {registration.authority_id}")
    print(f"Tree root: {registration.tree_root.hex()}")


def example_proof_generation():
    """Example: Generate an AegisProve proof."""
    # Create prover
    prover = AegisProveProver(authority_key="authority_secret.pem")
    
    # Generate proof for model-dataset binding
    proof = prover.prove_provenance(
        model_path="./model_weights.safetensors",
        dataset_id="abc123def456",
        prompt="What is the diagnosis?",
        response="Based on the symptoms..."
    )
    
    print(f"Proof generated for dataset: {proof.dataset_id}")
    print(f"Signature proof: {proof.signature_proof.hex()[:16]}...")
    print(f"Binding proof: {proof.binding_proof.hex()[:16]}...")


def example_proof_verification():
    """Example: Verify an AegisProve proof."""
    # Create verifier with public key
    verifier = AegisProveVerifier(authority_key="authority_public.pem")
    
    # Load proof from file
    with open("proof.json", 'r') as f:
        proof_data = json.load(f)
    
    # Verify the proof
    result = verifier.verify_proof(proof_data)
    
    if result.is_valid:
        print("✓ Proof is valid")
    else:
        print(f"✗ Proof is invalid: {result.error_message}")
        for component, valid in result.verified_components.items():
            print(f"  {component}: {'✓' if valid else '✗'}")
