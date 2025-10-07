"""
UPC Validator Core Module
Pure Python UPC validation logic without GUI dependencies
Can be used standalone or imported by the main application
"""

class UPCValidator:
    """
    Core UPC validation and decoding logic.
    Handles validation using check-digit formula and decodes UPC components.
    """
    
    # Product type mappings based on first digit
    PRODUCT_TYPES = {
        '0': 'General groceries',
        '1': 'Reserved for future use',
        '2': 'Meat and produce (variable weight)',
        '3': 'Drugs & health products',
        '4': 'Non-food items (in-store)',
        '5': 'Coupons',
        '6': 'Other items',
        '7': 'Other items',
        '8': 'Reserved for future use',
        '9': 'Reserved for future use'
    }
    
    def __init__(self, upc_code):
        """Initialize validator with a UPC code."""
        self.upc_code = str(upc_code).strip()
        self.is_valid = False
        self.error_message = ""
        self.product_type = ""
        self.manufacturer_code = ""
        self.product_code = ""
        self.check_digit = ""
        
    def validate(self):
        """
        Validate UPC code using check-digit formula:
        3*a1 + a2 + 3*a3 + a4 + 3*a5 + a6 + 3*a7 + a8 + 3*a9 + a10 + 3*a11 + a12 ≡ 0 (mod 10)
        """
        # Check if UPC has exactly 12 digits
        if len(self.upc_code) != 12:
            self.error_message = f"UPC must be exactly 12 digits (got {len(self.upc_code)})"
            return False
        
        # Check if all characters are digits
        if not self.upc_code.isdigit():
            self.error_message = "UPC must contain only digits"
            return False
        
        # Calculate check digit
        total = 0
        for i, digit in enumerate(self.upc_code):
            digit_val = int(digit)
            # Positions 0, 2, 4, 6, 8, 10 get multiplied by 3
            if i % 2 == 0:
                total += digit_val * 3
            else:
                total += digit_val
        
        # Check if total is divisible by 10
        if total % 10 != 0:
            self.error_message = f"Invalid check digit (sum = {total}, should be divisible by 10)"
            return False
        
        # UPC is valid
        self.is_valid = True
        self.decode()
        return True
    
    def decode(self):
        """Decode UPC components."""
        if len(self.upc_code) == 12:
            first_digit = self.upc_code[0]
            self.product_type = self.PRODUCT_TYPES.get(first_digit, 'Unknown')
            self.manufacturer_code = self.upc_code[1:6]  # Digits 2-6
            self.product_code = self.upc_code[6:11]      # Digits 7-11
            self.check_digit = self.upc_code[11]         # Digit 12
    
    def solve_missing_digit(self):
        """
        Solve for one missing digit represented by '?' or '_'.
        Returns the complete UPC if solvable, None otherwise.
        """
        # Count missing digits
        missing_count = self.upc_code.count('?') + self.upc_code.count('_')
        
        if missing_count != 1:
            return None
        
        # Find position of missing digit
        missing_pos = -1
        for i, char in enumerate(self.upc_code):
            if char in ['?', '_']:
                missing_pos = i
                break
        
        # Try each digit 0-9
        for digit in range(10):
            test_upc = self.upc_code[:missing_pos] + str(digit) + self.upc_code[missing_pos+1:]
            validator = UPCValidator(test_upc)
            if validator.validate():
                return test_upc
        
        return None


if __name__ == "__main__":
    # Quick test
    print("UPC Validator Core Module - Quick Test\n")
    
    test_upcs = [
        "036000291452",  # Valid
        "012000161155",  # Valid
        "123456789012",  # Invalid
    ]
    
    for upc in test_upcs:
        validator = UPCValidator(upc)
        if validator.validate():
            print(f"✓ {upc} - VALID - {validator.product_type}")
        else:
            print(f"✗ {upc} - INVALID - {validator.error_message}")