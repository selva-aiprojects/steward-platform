import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.security import get_password_hash, verify_password

def test_basic_functionality():
    print("Testing basic functionality...")
    
    # Test password hashing with various lengths
    test_passwords = [
        "short",
        "medium_length_password",
        "very_long_password_that_exceeds_the_bcrypt_limit_of_72_bytes_and_should_be_truncated_or_handled_properly",
        "normal_password_123"
    ]
    
    print("Testing password hashing...")
    for i, pwd in enumerate(test_passwords):
        try:
            print(f"  Testing password {i+1}: {pwd[:20]}{'...' if len(pwd) > 20 else ''}")
            hashed = get_password_hash(pwd)
            is_valid = verify_password(pwd, hashed)
            print(f"    Hashed successfully: {is_valid}")
            assert is_valid, f"Password verification failed for: {pwd}"
        except Exception as e:
            print(f"    Error with password {i+1}: {str(e)}")
            raise
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_basic_functionality()