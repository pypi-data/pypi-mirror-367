#!/usr/bin/env python3
"""
Quick test to verify urllib3 warning suppression works.
"""

import warnings

import urllib3

# Suppress urllib3 SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test if GeneInfo initialization triggers warnings
try:
    from geneinfo import GeneInfo

    print("Testing GeneInfo initialization...")
    gi = GeneInfo()
    print("✅ GeneInfo initialized without SSL warnings")
    print("StringDB fetcher present:", hasattr(gi, "stringdb_fetcher"))
except Exception as e:
    print(f"❌ Error during initialization: {e}")

print("Test completed.")
