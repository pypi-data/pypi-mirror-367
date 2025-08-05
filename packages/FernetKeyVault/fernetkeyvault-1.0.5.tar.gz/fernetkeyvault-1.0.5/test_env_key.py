#!/usr/bin/env python3
"""
Simple script to test the environment variable-based key storage as the default.
"""

import os
import logging
from FernetKeyVault import get_database_vault

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_script')

def main():
    # Set the environment variable for the key
    # Generate a valid Fernet key (must be 32 url-safe base64-encoded bytes)
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    os.environ['MASTER_KEY'] = key.decode()
    
    # Create a vault using the default EnvironmentKeyLoader
    logger.info("Creating vault with default EnvironmentKeyLoader...")
    vault = get_database_vault(db_path="test_env_vault.db")
    
    # Add an entry
    logger.info("Adding entry to vault...")
    success = vault.add_entry("test_key", "test_value")
    logger.info(f"Entry added successfully: {success}")
    
    # Retrieve the entry
    logger.info("Retrieving entry from vault...")
    value = vault.retrieve_entry("test_key")
    logger.info(f"Retrieved value: {value}")
    
    # Verify the value
    assert value == "test_value", f"Expected 'test_value', got '{value}'"
    logger.info("Test passed: Retrieved value matches expected value")
    
    # Clean up
    logger.info("Cleaning up...")
    if os.path.exists("test_env_vault.db"):
        os.remove("test_env_vault.db")
    if os.path.exists("test_env_vault.db-shm"):
        os.remove("test_env_vault.db-shm")
    if os.path.exists("test_env_vault.db-wal"):
        os.remove("test_env_vault.db-wal")
    
    logger.info("Test completed successfully")

if __name__ == "__main__":
    main()