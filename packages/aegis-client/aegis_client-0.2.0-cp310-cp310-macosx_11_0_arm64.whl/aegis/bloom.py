"""
AEGIS Bloom Filter Python Bindings

This module provides Python bindings to the Rust Bloom filter implementation
with integrated license checking and enforcement.
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import tempfile

# Import licensing module for limit checks
from . import licensing


def build_bloom_filter(
    input_dir: str,
    output_path: str,
    chunk_size: int = 512,
    size_mb: int = 64,
    expected_items: int = 10_000_000
) -> Dict[str, Any]:
    """
    Build a Bloom filter from a directory of text files.
    
    Args:
        input_dir: Directory containing text files to process
        output_path: Path for the output bloom filter file
        chunk_size: Size of text chunks in bytes (default: 512)
        size_mb: Target filter size in MB (default: 64)
        expected_items: Expected number of items (default: 10M)
    
    Returns:
        Dictionary containing build statistics
    
    Raises:
        RuntimeError: If the build fails or limits are exceeded
    """
    # Pre-check license limits
    license_info = licensing.get_license_info()
    
    # For now, we'll use the Rust CLI directly
    # In production, this would use compiled Rust bindings
    try:
        # Build command
        cmd = [
            sys.executable, "-m", "aegis_bloom_rust",
            "build",
            "--input", input_dir,
            "--output", output_path,
            "--chunk-size", str(chunk_size),
            "--size-mb", str(size_mb),
            "--expected-items", str(expected_items)
        ]
        
        # Add license key if present
        if license_info.license_key:
            env = os.environ.copy()
            env["AEGIS_LICENSE_KEY"] = json.dumps(license_info.license_key)
        else:
            env = os.environ.copy()
        
        # Run the Rust implementation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            # Check if it's a license error
            if "DEVELOPER EDITION LIMIT" in result.stderr:
                license_info.show_upgrade_prompt("Build limits exceeded")
            raise RuntimeError(f"Bloom filter build failed: {result.stderr}")
        
        # Parse the JSON output
        try:
            stats = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback to basic stats
            stats = {
                "documents_processed": 0,
                "chunks_added": 0,
                "raw_size_bytes": 0,
                "compressed_size_bytes": os.path.getsize(output_path) if os.path.exists(output_path) else 0,
                "estimated_false_positive_rate": 0.01,
                "processing_time_seconds": 0
            }
        
        return stats
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Bloom filter build timed out after 5 minutes")
    except FileNotFoundError:
        # Rust module not available, use pure Python fallback
        return _build_bloom_filter_python(
            input_dir, output_path, chunk_size, size_mb, expected_items
        )


def check_text_against_filter(
    text: str,
    filter_path: str
) -> str:
    """
    Check if text appears in a Bloom filter.
    
    Args:
        text: Text to check
        filter_path: Path to the bloom filter file
    
    Returns:
        "NOT_PRESENT" or "MAYBE_PRESENT"
    
    Raises:
        RuntimeError: If the check fails
    """
    # Check rate limits for Developer Edition
    license_info = licensing.get_license_info()
    
    try:
        # Create temporary file with text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(text)
            temp_path = f.name
        
        try:
            # Build command
            cmd = [
                sys.executable, "-m", "aegis_bloom_rust",
                "check",
                "--filter", filter_path,
                "--input", temp_path
            ]
            
            # Add license key if present
            if license_info.license_key:
                env = os.environ.copy()
                env["AEGIS_LICENSE_KEY"] = json.dumps(license_info.license_key)
            else:
                env = os.environ.copy()
            
            # Run the Rust implementation
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode != 0:
                # Check if it's a rate limit error
                if "rate limit" in result.stderr.lower():
                    license_info.show_upgrade_prompt("Query rate limit exceeded")
                raise RuntimeError(f"Bloom filter check failed: {result.stderr}")
            
            # Parse the result
            if "NOT_PRESENT" in result.stdout:
                return "NOT_PRESENT"
            elif "MAYBE_PRESENT" in result.stdout:
                return "MAYBE_PRESENT"
            else:
                # Default to conservative result
                return "MAYBE_PRESENT"
                
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except subprocess.TimeoutExpired:
        raise RuntimeError("Bloom filter check timed out after 30 seconds")
    except FileNotFoundError:
        # Rust module not available, use pure Python fallback
        return _check_text_python(text, filter_path)


def _build_bloom_filter_python(
    input_dir: str,
    output_path: str,
    chunk_size: int,
    size_mb: int,
    expected_items: int
) -> Dict[str, Any]:
    """
    Pure Python fallback implementation for building Bloom filters.
    This is much slower than the Rust version but works without compilation.
    """
    import hashlib
    import gzip
    import time
    from bitarray import bitarray
    
    start_time = time.time()
    
    # Initialize bit array
    size_bits = size_mb * 1024 * 1024 * 8
    bloom_bits = bitarray(size_bits)
    bloom_bits.setall(0)
    
    # Process files
    docs_processed = 0
    chunks_added = 0
    total_bytes = 0
    
    input_path = Path(input_dir)
    for file_path in input_path.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.rst']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    total_bytes += len(content)
                    
                    # Check limits
                    if not licensing.check_limits(
                        docs=docs_processed + 1,
                        size_gb=total_bytes / (1024**3)
                    ):
                        raise RuntimeError("License limits exceeded")
                    
                    # Process chunks
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i+chunk_size]
                        chunk_hash = hashlib.sha256(chunk.encode()).digest()
                        
                        # Simple hash functions (not optimal, but functional)
                        for k in range(3):  # Use 3 hash functions
                            h = int.from_bytes(
                                hashlib.sha256(chunk_hash + k.to_bytes(1, 'big')).digest()[:8],
                                'big'
                            )
                            bit_pos = h % size_bits
                            bloom_bits[bit_pos] = 1
                            
                        chunks_added += 1
                    
                    docs_processed += 1
                    
            except Exception as e:
                print(f"Warning: Failed to process {file_path}: {e}", file=sys.stderr)
    
    # Save to file with compression
    output_data = {
        "bloom_bits": bloom_bits.tobytes().hex(),
        "size_bits": size_bits,
        "hash_functions": 3,
        "chunks_added": chunks_added,
        "docs_processed": docs_processed,
        "edition": licensing.get_license_info().edition.value,
        "watermark": "AEGIS_DEVELOPER_EDITION" if licensing.get_license_info().edition == licensing.Edition.DEVELOPER else None
    }
    
    with gzip.open(output_path, 'wt', encoding='utf-8') as f:
        json.dump(output_data, f)
    
    elapsed = time.time() - start_time
    
    return {
        "documents_processed": docs_processed,
        "chunks_added": chunks_added,
        "raw_size_bytes": size_mb * 1024 * 1024,
        "compressed_size_bytes": os.path.getsize(output_path),
        "estimated_false_positive_rate": 0.01,
        "processing_time_seconds": elapsed
    }


def _check_text_python(text: str, filter_path: str) -> str:
    """
    Pure Python fallback implementation for checking Bloom filters.
    """
    import hashlib
    import gzip
    from bitarray import bitarray
    
    # Load filter
    with gzip.open(filter_path, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    
    bloom_bits = bitarray()
    bloom_bits.frombytes(bytes.fromhex(data["bloom_bits"]))
    size_bits = data["size_bits"]
    hash_functions = data.get("hash_functions", 3)
    
    # Check for watermark (Developer Edition)
    if data.get("watermark") == "AEGIS_DEVELOPER_EDITION":
        print("⚠️  Developer Edition bloom filter detected", file=sys.stderr)
    
    # Check text in chunks
    chunk_size = 512  # Default chunk size
    consecutive_hits = 0
    required_hits = 3  # Require 3 consecutive hits
    
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        chunk_hash = hashlib.sha256(chunk.encode()).digest()
        
        # Check all hash functions
        is_hit = True
        for k in range(hash_functions):
            h = int.from_bytes(
                hashlib.sha256(chunk_hash + k.to_bytes(1, 'big')).digest()[:8],
                'big'
            )
            bit_pos = h % size_bits
            if not bloom_bits[bit_pos]:
                is_hit = False
                break
        
        if is_hit:
            consecutive_hits += 1
            if consecutive_hits >= required_hits:
                return "MAYBE_PRESENT"
        else:
            consecutive_hits = 0
    
    return "NOT_PRESENT"


# Export main functions
__all__ = [
    'build_bloom_filter',
    'check_text_against_filter',
]
