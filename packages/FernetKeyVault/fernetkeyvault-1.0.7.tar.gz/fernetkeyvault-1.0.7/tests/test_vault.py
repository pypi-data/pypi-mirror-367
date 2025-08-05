#!/usr/bin/env python3
"""
Unit tests for vault.py validation functions and CLI functionality
"""

import os
import tempfile
import pytest
from unittest.mock import patch
from vault import validate_key, validate_value, validate_files, MAX_KEY_LENGTH, MAX_VALUE_LENGTH, main

class TestVaultValidation:
    """Test class for vault.py validation functions"""

    def test_validate_key_valid(self):
        """Test validate_key with valid keys"""
        valid_keys = [
            "simple",
            "with_underscore",
            "with-hyphen",
            "with.dot",
            "alphanumeric123",
            "a" * MAX_KEY_LENGTH  # Maximum length key
        ]
        
        for key in valid_keys:
            is_valid, error_message = validate_key(key)
            assert is_valid is True
            assert error_message is None

    def test_validate_key_invalid(self):
        """Test validate_key with invalid keys"""
        invalid_keys = [
            "",  # Empty key
            "a" * (MAX_KEY_LENGTH + 1),  # Too long
            "invalid space",  # Contains space
            "invalid@char",  # Contains @
            "invalid#char",  # Contains #
            "invalid$char",  # Contains $
            "invalid%char",  # Contains %
            "invalid&char",  # Contains &
            "invalid*char",  # Contains *
            "invalid(char",  # Contains (
            "invalid)char",  # Contains )
        ]
        
        for key in invalid_keys:
            is_valid, error_message = validate_key(key)
            assert is_valid is False
            assert error_message is not None

    def test_validate_value_valid(self):
        """Test validate_value with valid values"""
        valid_values = [
            "simple value",
            "value with special chars !@#$%^&*()",
            "a" * MAX_VALUE_LENGTH  # Maximum length value
        ]
        
        for value in valid_values:
            is_valid, error_message = validate_value(value)
            assert is_valid is True
            assert error_message is None

    def test_validate_value_invalid(self):
        """Test validate_value with invalid values"""
        invalid_values = [
            "",  # Empty value
            "a" * (MAX_VALUE_LENGTH + 1),  # Too long
        ]
        
        for value in invalid_values:
            is_valid, error_message = validate_value(value)
            assert is_valid is False
            assert error_message is not None

    def test_validate_files_valid_paths(self):
        """Test validate_files with valid paths"""
        # Create a temporary directory and file for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            key_file = os.path.join(temp_dir, "test.key")
            
            # Create the key file
            with open(key_file, "wb") as f:
                f.write(b"test_key")
            
            # Test with valid paths
            is_valid, error_message = validate_files(db_path, "file", key_file)
            assert is_valid is True
            assert error_message is None
            
            # Test with env key_type (a key file doesn't need to exist)
            is_valid, error_message = validate_files(db_path, "env", "nonexistent.key")
            assert is_valid is True
            assert error_message is None

    def test_validate_files_invalid_paths(self):
        """Test validate_files with invalid paths"""
        # Test with a non-existent directory
        non_existent_dir = "/non/existent/directory/test.db"
        is_valid, error_message = validate_files(non_existent_dir, "env", "test.key")
        assert is_valid is False
        assert "does not exist" in error_message
        
        # Test with file key_type but non-existent key file
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            non_existent_key = os.path.join(temp_dir, "nonexistent.key")
            
            is_valid, error_message = validate_files(db_path, "file", non_existent_key)
            assert is_valid is False
            assert "does not exist" in error_message

class TestVaultCLI:
    """Test class for vault.py CLI functionality"""

    def test_validate_key_integration(self):
        """Test validate_key function integration with main validation logic"""
        # Test with a valid key
        is_valid, error = validate_key("valid_key")
        assert is_valid is True
        assert error is None
        
        # Test with an invalid key
        is_valid, error = validate_key("")
        assert is_valid is False
        assert error is not None
        
    def test_validate_value_integration(self):
        """Test validate_value function integration with main validation logic"""
        # Test with a valid value
        is_valid, error = validate_value("valid value")
        assert is_valid is True
        assert error is None
        
        # Test with invalid value
        is_valid, error = validate_value("")
        assert is_valid is False
        assert error is not None
        
    def test_validate_files_integration(self):
        """Test validate_files function integration with main validation logic"""
        # Create a temporary directory and file for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with a valid directory
            db_path = os.path.join(temp_dir, "test.db")
            
            # Test with env key type (should pass)
            is_valid, error = validate_files(db_path, "env", "nonexistent.key")
            assert is_valid is True
            assert error is None
            
            # Create a key file
            key_file = os.path.join(temp_dir, "test.key")
            with open(key_file, "wb") as f:
                f.write(b"test_key")
                
            # Test with file key type and existing key file
            is_valid, error = validate_files(db_path, "file", key_file)
            assert is_valid is True
            assert error is None
            
            # Test with file key type and non-existent key file
            is_valid, error = validate_files(db_path, "file", "nonexistent.key")
            assert is_valid is False
            assert "does not exist" in error
            
    @patch('sys.argv', ['vault.py', '--help'])
    @patch('argparse.ArgumentParser.print_help')
    def test_main_help(self, mock_print_help):
        """Test the main function with --help argument"""
        # This test just verifies that main() can be called without errors
        # We're not testing the full functionality, just that it doesn't crash
        try:
            with patch('sys.exit') as mock_exit:
                main()
                mock_print_help.assert_called_once()
        except Exception as e:
            pytest.fail(f"main() raised {type(e).__name__} unexpectedly: {e}")
            
    @patch('sys.argv', ['vault.py', 'list', '--key_type', 'env'])
    @patch('vault.validate_files')
    def test_main_validation_failure(self, mock_validate_files):
        """Test the main function with validation failure"""
        # Mock validate_files to return False
        mock_validate_files.return_value = (False, "Test error message")
        
        # Capture logger calls
        with patch('logging.Logger.error') as mock_logger_error:
            main()
            mock_logger_error.assert_called_once()

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])