#!/usr/bin/env python3
"""
Test script for validating the key file existence in vault.py
"""

import os
import subprocess
import tempfile

def test_key_file_validation():
    """Test validation of key file existence"""
    print("\n=== Testing key file validation ===")
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.key', delete=False) as temp_file:
        temp_file.write(b'some key data')
        temp_key_path = temp_file.name
    
    # Test with a non-existent key file when key_type is "file"
    non_existent_key = "non_existent.key"
    print(f"Testing with non-existent key file: {non_existent_key}")
    result = subprocess.run(
        ["python", "vault.py", "retrieve", "--key_type", "file", "--key_file", non_existent_key],
        capture_output=True,
        text=True
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    # The error message might be in stdout or stderr depending on how logging is configured
    assert "does not exist" in result.stderr or "does not exist" in result.stdout
    
    # Test with an existing key file when key_type is "file"
    print(f"Testing with existing key file: {temp_key_path}")
    result = subprocess.run(
        ["python", "vault.py", "retrieve", "--key_type", "file", "--key_file", temp_key_path],
        input="valid_key\n",
        capture_output=True,
        text=True
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    
    # Test with a non-existent key file when key_type is "env"
    print(f"Testing with non-existent key file but key_type is 'env': {non_existent_key}")
    result = subprocess.run(
        ["python", "vault.py", "retrieve", "--key_type", "env", "--key_file", non_existent_key],
        capture_output=True,
        text=True
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    # Should not fail with "does not exist" error since key_type is "env"
    assert "does not exist" not in result.stderr and "does not exist" not in result.stdout
    
    # Clean up
    os.unlink(temp_key_path)

if __name__ == "__main__":
    # Make sure the master.key exists for testing
    if not os.path.exists("master.key"):
        with open("master.key", "wb") as f:
            f.write(b"test_key_for_validation")
        print("Created master.key for testing")
    
    test_key_file_validation()
    
    print("\nAll tests completed.")