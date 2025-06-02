#!/usr/bin/env python3
"""
Test script to verify that class source retrieval works correctly for namespaced classes.
This test demonstrates the fix for the namespace encoding issue.
"""

import sys
import os

# Add src/tools to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'tools'))

from utils import encode_sap_object_name

def test_namespace_url_construction():
    """Test URL construction for namespaced classes."""
    
    print("Testing URL construction for namespaced SAP objects...")
    print("=" * 60)
    
    # Test case: the problematic class mentioned in the issue
    class_name = "/1CPR/CL_000_0SAP2_FAG"
    encoded_name = encode_sap_object_name(class_name)
    
    # Construct the URL as it would be done in class_source.py
    base_url = "https://example.sap.com"
    endpoint = f"{base_url}/sap/bc/adt/oo/classes/{encoded_name}/source/main"
    
    print(f"Original class name: {class_name}")
    print(f"Encoded class name:  {encoded_name}")
    print(f"Full endpoint URL:   {endpoint}")
    print()
    
    # Verify the encoding is correct
    expected_encoded = "%2F1CPR%2FCL_000_0SAP2_FAG"
    expected_url = f"{base_url}/sap/bc/adt/oo/classes/{expected_encoded}/source/main"
    
    if encoded_name == expected_encoded:
        print("✓ Encoding is correct!")
    else:
        print(f"✗ Encoding mismatch! Expected: {expected_encoded}")
        return False
    
    if endpoint == expected_url:
        print("✓ URL construction is correct!")
    else:
        print(f"✗ URL mismatch! Expected: {expected_url}")
        return False
    
    print()
    print("Before fix: URL would have been:")
    print(f"  {base_url}/sap/bc/adt/oo/classes/{class_name}/source/main")
    print("  ^ This would cause HTTP 404 or other errors due to unencoded '/' characters")
    print()
    print("After fix: URL is now:")
    print(f"  {endpoint}")
    print("  ^ This correctly encodes '/' as '%2F' for safe URL usage")
    
    return True

def test_other_namespace_examples():
    """Test other namespace examples."""
    
    print("\nTesting other namespace examples...")
    print("=" * 40)
    
    test_cases = [
        ("/NAMESPACE/CLASS_NAME", "%2FNAMESPACE%2FCLASS_NAME"),
        ("/ABC/DEF/PROGRAM", "%2FABC%2FDEF%2FPROGRAM"),
        ("NORMAL_CLASS", "NORMAL_CLASS"),  # Non-namespaced should remain unchanged
    ]
    
    all_passed = True
    for original, expected in test_cases:
        encoded = encode_sap_object_name(original)
        passed = encoded == expected
        all_passed = all_passed and passed
        
        status = "✓" if passed else "✗"
        print(f"{status} {original} -> {encoded}")
        if not passed:
            print(f"    Expected: {expected}")
    
    return all_passed

if __name__ == "__main__":
    print("SAP Namespace Encoding Fix Verification")
    print("=" * 60)
    print()
    
    success1 = test_namespace_url_construction()
    success2 = test_other_namespace_examples()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✓ All tests passed! The namespace encoding fix is working correctly.")
        print("\nThe issue with classes like '/1CPR/CL_000_0SAP2_FAG' should now be resolved.")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)
