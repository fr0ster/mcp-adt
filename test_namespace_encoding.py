#!/usr/bin/env python3
"""
Test script to verify that SAP object name encoding works correctly for namespaces.
"""

import sys
import os

# Add src/tools to path so we can import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'tools'))

from utils import encode_sap_object_name

def test_namespace_encoding():
    """Test encoding of SAP object names with namespaces."""
    
    test_cases = [
        # (input, expected_output)
        ('/1CPR/CL_000_0SAP2_FAG', '%2F1CPR%2FCL_000_0SAP2_FAG'),
        ('ZCL_NORMAL_CLASS', 'ZCL_NORMAL_CLASS'),
        ('/NAMESPACE/OBJECT_NAME', '%2FNAMESPACE%2FOBJECT_NAME'),
        ('/ABC/DEF/GHI', '%2FABC%2FDEF%2FGHI'),
        ('NORMAL_OBJECT', 'NORMAL_OBJECT'),
    ]
    
    print("Testing SAP object name encoding...")
    print("=" * 50)
    
    all_passed = True
    
    for input_name, expected in test_cases:
        result = encode_sap_object_name(input_name)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} | Input: '{input_name}' -> Output: '{result}'")
        if not passed:
            print(f"      Expected: '{expected}'")
    
    print("=" * 50)
    if all_passed:
        print("✓ All tests passed!")
        return True
    else:
        print("✗ Some tests failed!")
        return False

if __name__ == "__main__":
    success = test_namespace_encoding()
    sys.exit(0 if success else 1)
