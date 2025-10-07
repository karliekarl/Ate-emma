"""
Test script for UPC Validator
Run this to test the core validation functionality without the GUI
"""

from upc_core import UPCValidator

def test_upc_validation():
    """Test UPC validation with various examples."""
    
    print("=" * 60)
    print("UPC VALIDATOR - TEST SUITE")
    print("=" * 60)
    print()
    
    test_cases = [
        ("036000291452", True, "Valid UPC - Tide Detergent"),
        ("012000161155", True, "Valid UPC - Coca-Cola"),
        ("078000082487", True, "Valid UPC - Lucky Charms"),
        ("041196403091", True, "Valid UPC - Skippy Peanut Butter"),
        ("123456789013", False, "Invalid UPC - Wrong check digit"),
        ("12345678901", False, "Invalid UPC - Too short"),
        ("1234567890123", False, "Invalid UPC - Too long"),
        ("12345678901X", False, "Invalid UPC - Contains letter"),
    ]
    
    passed = 0
    failed = 0
    
    for upc, expected_valid, description in test_cases:
        validator = UPCValidator(upc)
        is_valid = validator.validate()
        
        # Check if result matches expectation
        if is_valid == expected_valid:
            status = "✓ PASS"
            passed += 1
            color = "\033[92m"  # Green
        else:
            status = "✗ FAIL"
            failed += 1
            color = "\033[91m"  # Red
        
        reset = "\033[0m"
        
        print(f"{color}{status}{reset} | {upc} | {description}")
        
        if is_valid:
            print(f"      Product Type: {validator.product_type}")
            print(f"      Manufacturer: {validator.manufacturer_code}")
            print(f"      Product Code: {validator.product_code}")
            print(f"      Check Digit:  {validator.check_digit}")
        else:
            print(f"      Error: {validator.error_message}")
        
        print()
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    print()

def test_missing_digit_solver():
    """Test missing digit solver functionality."""
    
    print("=" * 60)
    print("MISSING DIGIT SOLVER - TEST")
    print("=" * 60)
    print()
    
    test_cases = [
        "03600029145?",  # Should solve to 2
        "0120001611?5",  # Should solve to 5
        "0780000824?7",  # Should solve to 8
    ]
    
    for upc_with_missing in test_cases:
        validator = UPCValidator(upc_with_missing)
        solved = validator.solve_missing_digit()
        
        if solved:
            print(f"✓ Solved: {upc_with_missing} → {solved}")
            
            # Verify the solved UPC is valid
            verify = UPCValidator(solved)
            if verify.validate():
                print(f"  ✓ Verification: VALID")
                print(f"  Product Type: {verify.product_type}")
            else:
                print(f"  ✗ Verification: INVALID - {verify.error_message}")
        else:
            print(f"✗ Failed to solve: {upc_with_missing}")
        
        print()
    
    print("=" * 60)
    print()

def test_product_type_detection():
    """Test product type detection for different first digits."""
    
    print("=" * 60)
    print("PRODUCT TYPE DETECTION - TEST")
    print("=" * 60)
    print()
    
    # Generate test UPCs for each product type (first digit 0-9)
    print("Testing all product type categories:\n")
    
    for first_digit in range(10):
        # Create a valid UPC starting with this digit
        # We'll use a simple pattern and calculate the check digit
        base_upc = f"{first_digit}12345678"  # 10 digits
        
        # Calculate check digit
        total = 0
        for i, digit in enumerate(base_upc):
            if i % 2 == 0:
                total += int(digit) * 3
            else:
                total += int(digit)
        
        # Add placeholder for 11th digit and check digit
        for eleventh in range(10):
            test_total = total + eleventh
            check_digit = (10 - (test_total % 10)) % 10
            complete_upc = base_upc + str(eleventh) + str(check_digit)
            
            validator = UPCValidator(complete_upc)
            if validator.validate():
                print(f"Digit {first_digit}: {validator.product_type}")
                print(f"  Example UPC: {complete_upc}")
                break
    
    print()
    print("=" * 60)
    print()

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("STARTING UPC VALIDATOR TEST SUITE")
    print("=" * 60)
    print("\nThis script tests the core UPC validation functionality")
    print("without launching the GUI.\n")
    
    try:
        test_upc_validation()
        test_missing_digit_solver()
        test_product_type_detection()
        
        print("\n✓ All tests completed!")
        print("\nTo launch the full GUI application, run:")
        print("  python upc_validator_app.py\n")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()