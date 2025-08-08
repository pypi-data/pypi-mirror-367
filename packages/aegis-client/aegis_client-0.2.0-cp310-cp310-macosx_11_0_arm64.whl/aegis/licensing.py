"""
AEGIS Licensing Utilities

Handles license detection, validation, and upgrade prompts for the dual-licensing model.
"""

import os
import json
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Edition(Enum):
    """AEGIS Edition types"""
    DEVELOPER = "Developer"
    STARTUP = "Startup"
    GROWTH = "Growth"
    ENTERPRISE = "Enterprise"
    OEM = "OEM"


class LicenseInfo:
    """License information and limits"""
    
    # Developer Edition limits (Apache-2.0)
    DEV_MAX_DOCS = 1_000_000  # 1M documents
    DEV_MAX_SIZE_GB = 1  # 1GB total
    DEV_MAX_QPS = 30  # 30 queries per second
    
    # Tier limits
    TIER_LIMITS = {
        Edition.DEVELOPER: {
            "max_docs": DEV_MAX_DOCS,
            "max_size_gb": DEV_MAX_SIZE_GB,
            "max_qps": DEV_MAX_QPS,
            "price": "Free",
            "license": "Apache-2.0",
            "indemnity": False,
        },
        Edition.STARTUP: {
            "max_docs": 10_000_000,
            "max_size_gb": 10,
            "max_qps": 100,
            "price": "$399/month",
            "license": "BSL-1.1",
            "indemnity": False,
        },
        Edition.GROWTH: {
            "max_docs": 100_000_000,
            "max_size_gb": 100,
            "max_qps": 500,
            "price": "$2,499/month",
            "license": "BSL-1.1",
            "indemnity": True,
        },
        Edition.ENTERPRISE: {
            "max_docs": None,  # Unlimited
            "max_size_gb": None,  # Unlimited
            "max_qps": None,  # Unlimited
            "price": "$30,000/year",
            "license": "BSL-1.1",
            "indemnity": True,
        },
    }
    
    def __init__(self):
        self.edition = Edition.DEVELOPER
        self.license_key = None
        self.organization = None
        self.expiry = None
        self._load_license()
    
    def _load_license(self):
        """Load license from environment or file"""
        # Check environment variable
        license_key = os.environ.get("AEGIS_LICENSE_KEY")
        
        if license_key:
            try:
                # Parse license key (JSON format)
                license_data = json.loads(license_key)
                self._apply_license(license_data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️  Invalid license key format: {e}", file=sys.stderr)
        
        # Check for license file
        elif os.path.exists(".aegis-license.json"):
            try:
                with open(".aegis-license.json", "r") as f:
                    license_data = json.load(f)
                    self._apply_license(license_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error reading license file: {e}", file=sys.stderr)
    
    def _apply_license(self, license_data: Dict[str, Any]):
        """Apply license data"""
        # Check expiry
        expiry = license_data.get("expiry_unix", 0)
        if expiry < datetime.now().timestamp():
            print("⚠️  License expired. Reverting to Developer Edition.", file=sys.stderr)
            return
        
        # Set license info
        tier = license_data.get("tier", "Developer")
        self.edition = Edition[tier.upper()]
        self.license_key = license_data
        self.organization = license_data.get("organization", "Unknown")
        self.expiry = datetime.fromtimestamp(expiry)
    
    @property
    def limits(self) -> Dict[str, Any]:
        """Get current edition limits"""
        return self.TIER_LIMITS[self.edition]
    
    @property
    def is_enterprise(self) -> bool:
        """Check if using enterprise features"""
        return self.edition in [Edition.GROWTH, Edition.ENTERPRISE, Edition.OEM]
    
    @property
    def has_indemnity(self) -> bool:
        """Check if license includes legal indemnification"""
        return self.limits["indemnity"]
    
    def check_document_limit(self, count: int) -> bool:
        """Check if document count is within limits"""
        max_docs = self.limits["max_docs"]
        if max_docs is None:
            return True
        return count <= max_docs
    
    def check_size_limit(self, size_gb: float) -> bool:
        """Check if size is within limits"""
        max_size = self.limits["max_size_gb"]
        if max_size is None:
            return True
        return size_gb <= max_size
    
    def format_status(self) -> str:
        """Format license status for display"""
        lines = []
        
        if self.edition == Edition.DEVELOPER:
            lines.append("📝 Using Developer Edition (Apache-2.0)")
            lines.append(f"   • Limited to {self.DEV_MAX_DOCS:,} documents")
            lines.append(f"   • Maximum {self.DEV_MAX_SIZE_GB}GB dataset size")
            lines.append(f"   • {self.DEV_MAX_QPS} queries per second")
            lines.append("   • Watermarked output")
            lines.append("   • No legal guarantees")
        else:
            lines.append(f"🔒 {self.edition.value} Edition - Licensed")
            if self.organization:
                lines.append(f"   • Organization: {self.organization}")
            if self.expiry:
                lines.append(f"   • Valid until: {self.expiry.strftime('%Y-%m-%d')}")
            
            limits = self.limits
            if limits["max_docs"]:
                lines.append(f"   • Document limit: {limits['max_docs']:,}")
            else:
                lines.append("   • Unlimited documents")
            
            if self.has_indemnity:
                lines.append("   • ✅ Legal indemnification active")
        
        return "\n".join(lines)
    
    def show_upgrade_prompt(self, reason: str = "limit exceeded"):
        """Show upgrade prompt when limits are hit"""
        print("\n" + "="*60, file=sys.stderr)
        print("⚠️  DEVELOPER EDITION LIMIT REACHED", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(f"\nReason: {reason}\n", file=sys.stderr)
        
        print("Available upgrade options:", file=sys.stderr)
        print("\n📊 Startup Edition ($399/month):", file=sys.stderr)
        print("   • 10M documents", file=sys.stderr)
        print("   • 10GB datasets", file=sys.stderr)
        print("   • 100 QPS", file=sys.stderr)
        print("   • Priority support", file=sys.stderr)
        
        print("\n🚀 Growth Edition ($2,499/month):", file=sys.stderr)
        print("   • 100M documents", file=sys.stderr)
        print("   • 100GB datasets", file=sys.stderr)
        print("   • 500 QPS", file=sys.stderr)
        print("   • Legal indemnification", file=sys.stderr)
        
        print("\n🏢 Enterprise Edition ($30,000/year):", file=sys.stderr)
        print("   • Unlimited everything", file=sys.stderr)
        print("   • $1M legal indemnification", file=sys.stderr)
        print("   • 24/7 support", file=sys.stderr)
        print("   • Custom integrations", file=sys.stderr)
        
        print("\n📧 Contact sales@aegisprove.com for licensing", file=sys.stderr)
        print("🌐 Visit https://aegisprove.com/pricing for details\n", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)


def get_license_info() -> LicenseInfo:
    """Get current license information"""
    return LicenseInfo()


def check_limits(docs: int = 0, size_gb: float = 0.0) -> bool:
    """
    Check if current usage is within license limits.
    Returns True if within limits, False otherwise.
    """
    license_info = get_license_info()
    
    if not license_info.check_document_limit(docs):
        license_info.show_upgrade_prompt(
            f"Document count ({docs:,}) exceeds limit ({license_info.limits['max_docs']:,})"
        )
        return False
    
    if not license_info.check_size_limit(size_gb):
        license_info.show_upgrade_prompt(
            f"Dataset size ({size_gb:.1f}GB) exceeds limit ({license_info.limits['max_size_gb']}GB)"
        )
        return False
    
    return True


def display_license_info():
    """Display current license information"""
    license_info = get_license_info()
    print(license_info.format_status())
    
    if license_info.edition == Edition.DEVELOPER:
        print("\n💡 Tip: Set AEGIS_LICENSE_KEY environment variable to use Enterprise features")


def validate_license_key(key_json: str) -> bool:
    """
    Validate a license key JSON string.
    Returns True if valid, False otherwise.
    """
    try:
        data = json.loads(key_json)
        required_fields = ["customer_id", "organization", "expiry_unix", "tier", "signature"]
        
        for field in required_fields:
            if field not in data:
                print(f"Missing required field: {field}", file=sys.stderr)
                return False
        
        # Check expiry
        if data["expiry_unix"] < datetime.now().timestamp():
            print("License has expired", file=sys.stderr)
            return False
        
        # TODO: Verify signature cryptographically
        # For now, just check it exists
        if not data["signature"]:
            print("Invalid signature", file=sys.stderr)
            return False
        
        return True
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Invalid license format: {e}", file=sys.stderr)
        return False


def generate_test_license(tier: str = "STARTUP", days: int = 30) -> str:
    """
    Generate a test license key for development.
    NOT FOR PRODUCTION USE.
    """
    import hashlib
    from datetime import timedelta
    
    expiry = datetime.now() + timedelta(days=days)
    
    license_data = {
        "customer_id": "test-customer-001",
        "organization": "Test Organization",
        "expiry_unix": int(expiry.timestamp()),
        "tier": tier,
        "max_documents": None if tier == "ENTERPRISE" else 10_000_000,
        "max_qps": None if tier == "ENTERPRISE" else 100,
        "includes_indemnity": tier in ["GROWTH", "ENTERPRISE"],
        "indemnity_coverage_usd": 1_000_000 if tier == "ENTERPRISE" else None,
        "signature": hashlib.sha256(f"test-{tier}-{expiry}".encode()).hexdigest()
    }
    
    return json.dumps(license_data, indent=2)


if __name__ == "__main__":
    # Test/demo mode
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "info":
            display_license_info()
        elif sys.argv[1] == "generate":
            tier = sys.argv[2] if len(sys.argv) > 2 else "STARTUP"
            print(generate_test_license(tier))
        else:
            print("Usage: python licensing.py [info|generate [TIER]]")
    else:
        display_license_info()
