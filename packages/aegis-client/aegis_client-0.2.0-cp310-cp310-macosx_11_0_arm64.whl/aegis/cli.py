#!/usr/bin/env python3
"""
AEGIS Bloom Filter CLI

Command-line interface for building and checking copyright compliance using Bloom filters.
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional
import json

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from aegis import bloom
    from aegis import licensing
    from aegis._version import __version__
except ImportError:
    print("Error: Could not import aegis modules. Please ensure the package is installed correctly.")
    sys.exit(1)


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def count_files_and_size(directory: Path) -> tuple[int, int]:
    """Count files and total size in a directory"""
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in ['.txt', '.md', '.rst', '.tex', '.py', '.rs', '.js', '.c', '.cpp', '.h', '.hpp']:
                total_files += 1
                try:
                    total_size += file_path.stat().st_size
                except OSError:
                    pass
    
    return total_files, total_size


def cmd_bloom_build(args):
    """Build a Bloom filter from a directory of text files"""
    input_dir = Path(args.input_dir)
    output_file = Path(args.output)
    
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist", file=sys.stderr)
        return 1
    
    # Display license info at start
    license_info = licensing.get_license_info()
    print(license_info.format_status())
    print()
    
    # Pre-check directory size for limits
    print(f"Scanning directory: {input_dir}")
    file_count, total_size = count_files_and_size(input_dir)
    size_gb = total_size / (1024**3)
    
    print(f"Found {file_count:,} text files, total size: {format_size(total_size)}")
    
    # Check license limits
    if not licensing.check_limits(docs=file_count, size_gb=size_gb):
        return 1
    
    # Build the filter
    print("\nBuilding Bloom filter...")
    start_time = time.time()
    
    try:
        # Call the Rust implementation through Python bindings
        stats = bloom.build_bloom_filter(
            str(input_dir),
            str(output_file),
            chunk_size=args.chunk_size,
            size_mb=args.size_mb,
            expected_items=args.expected_items
        )
        
        elapsed = time.time() - start_time
        
        # Display results
        print(f"\n✅ Bloom filter built successfully!")
        print(f"   • Output: {output_file}")
        print(f"   • Documents processed: {stats.get('documents_processed', 0):,}")
        print(f"   • Chunks added: {stats.get('chunks_added', 0):,}")
        print(f"   • Raw size: {format_size(stats.get('raw_size_bytes', 0))}")
        print(f"   • Compressed size: {format_size(stats.get('compressed_size_bytes', 0))}")
        print(f"   • False positive rate: {stats.get('estimated_false_positive_rate', 0.01):.2%}")
        print(f"   • Processing time: {elapsed:.1f}s")
        
        # Watermark notice for Developer Edition
        if license_info.edition == licensing.Edition.DEVELOPER:
            print("\n⚠️  Developer Edition: Output includes watermark - not for production use")
            print("    Upgrade to Enterprise for legally-binding proofs")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error building Bloom filter: {e}", file=sys.stderr)
        return 1


def cmd_bloom_check(args):
    """Check if text appears in a Bloom filter"""
    filter_file = Path(args.filter)
    
    if not filter_file.exists():
        print(f"Error: Filter file '{filter_file}' does not exist", file=sys.stderr)
        return 1
    
    # Display license info
    license_info = licensing.get_license_info()
    if args.verbose:
        print(license_info.format_status())
        print()
    
    # Read input text
    if args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
            return 1
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        print(f"Checking file: {input_path}")
    else:
        print("Enter text to check (Ctrl+D to finish):")
        text = sys.stdin.read()
    
    # Check text against filter
    try:
        result = bloom.check_text_against_filter(text, str(filter_file))
        
        # Display result
        print("\n" + "="*60)
        if result == "NOT_PRESENT":
            print("✅ RESULT: NOT_PRESENT")
            print("   The text is definitely NOT in the training corpus")
        else:  # MAYBE_PRESENT
            print("⚠️  RESULT: MAYBE_PRESENT")
            print("   The text MAY be present in the training corpus")
            print("   (or this could be a false positive)")
        print("="*60)
        
        # Legal disclaimer for Developer Edition
        if license_info.edition == licensing.Edition.DEVELOPER:
            print("\n📝 Developer Edition Notice:")
            print("   This result is for development purposes only.")
            print("   For legally-binding compliance checks, upgrade to Enterprise.")
        elif license_info.has_indemnity:
            print("\n🔒 Enterprise Edition:")
            print("   This result is covered by legal indemnification.")
            print("   Save this output for compliance records.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error checking text: {e}", file=sys.stderr)
        return 1


def cmd_license_info(args):
    """Display license information"""
    licensing.display_license_info()
    
    if args.validate:
        # Validate current license key if present
        license_key = os.environ.get("AEGIS_LICENSE_KEY")
        if license_key:
            print("\nValidating license key...")
            if licensing.validate_license_key(license_key):
                print("✅ License key is valid")
            else:
                print("❌ License key validation failed")
                return 1
        else:
            print("\nNo license key found in environment")
    
    if args.generate_test:
        print("\n" + "="*60)
        print("TEST LICENSE KEY (NOT FOR PRODUCTION)")
        print("="*60)
        test_key = licensing.generate_test_license(args.generate_test)
        print(test_key)
        print("\nTo use this test key:")
        print(f"export AEGIS_LICENSE_KEY='{test_key}'")
    
    return 0


def cmd_version(args):
    """Display version information"""
    print(f"AEGIS Bloom Filter v{__version__}")
    print("Copyright 2025 Aegis Testing Technologies LLC")
    print()
    
    license_info = licensing.get_license_info()
    print(f"Edition: {license_info.edition.value}")
    
    if license_info.organization:
        print(f"Licensed to: {license_info.organization}")
    
    print()
    print("This software is dual-licensed:")
    print("• Apache-2.0 for Developer Edition (≤1M docs, ≤1GB)")
    print("• BSL-1.1 for Enterprise Edition (unlimited)")
    print()
    print("For more information: https://aegisprove.com/licensing")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AEGIS Bloom Filter - Copyright compliance for AI training data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build a Bloom filter from a dataset
  aegis bloom-build data/ corpus.bloom

  # Check if text appears in the filter
  aegis bloom-check corpus.bloom -f text.txt

  # Display license information
  aegis license-info

For more information: https://aegisprove.com
        """
    )
    
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # bloom-build command
    build_parser = subparsers.add_parser(
        'bloom-build',
        help='Build a Bloom filter from a directory of text files'
    )
    build_parser.add_argument('input_dir', help='Directory containing text files')
    build_parser.add_argument('output', help='Output Bloom filter file (.bloom)')
    build_parser.add_argument('--chunk-size', type=int, default=512,
                            help='Chunk size in bytes (default: 512)')
    build_parser.add_argument('--size-mb', type=int, default=64,
                            help='Target filter size in MB (default: 64)')
    build_parser.add_argument('--expected-items', type=int, default=10_000_000,
                            help='Expected number of items (default: 10M)')
    build_parser.set_defaults(func=cmd_bloom_build)
    
    # bloom-check command
    check_parser = subparsers.add_parser(
        'bloom-check',
        help='Check if text appears in a Bloom filter'
    )
    check_parser.add_argument('filter', help='Bloom filter file (.bloom)')
    check_parser.add_argument('-f', '--input-file', help='Text file to check')
    check_parser.add_argument('-v', '--verbose', action='store_true',
                            help='Show detailed output')
    check_parser.set_defaults(func=cmd_bloom_check)
    
    # license-info command
    license_parser = subparsers.add_parser(
        'license-info',
        help='Display license information and limits'
    )
    license_parser.add_argument('--validate', action='store_true',
                              help='Validate current license key')
    license_parser.add_argument('--generate-test', choices=['STARTUP', 'GROWTH', 'ENTERPRISE'],
                              help='Generate a test license key (development only)')
    license_parser.set_defaults(func=cmd_license_info)
    
    # version command
    version_parser = subparsers.add_parser(
        'version',
        help='Display version and license information'
    )
    version_parser.set_defaults(func=cmd_version)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if hasattr(args, 'func'):
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()
