#!/usr/bin/env python3
"""
Main entry point for the FernetKeyVault package.
This script provides a command-line interface to the vault functionality.
"""

import argparse
import logging
import os
import re
from typing import Optional
from FernetKeyVault import get_database_vault
from FernetKeyVault.database_vault import DatabaseVault

# Get a logger for the CLI
logger: logging.Logger = logging.getLogger('FernetKeyVault.cli')

# Constants for validation
MAX_KEY_LENGTH = 100
MAX_VALUE_LENGTH = 1000
KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_\-.]+$')  # Alphanumeric, underscore, hyphen, and dot

def validate_key(key: str) -> tuple[bool, Optional[str]]:
    """
    Validate a key for the vault.
    
    Args:
        key (str): The key to validate
        
    Returns:
        tuple[bool, Optional[str]]: A tuple containing (is_valid, error_message)
    """
    if not key:
        return False, "Key cannot be empty."
    
    if len(key) > MAX_KEY_LENGTH:
        return False, f"Key is too long. Maximum length is {MAX_KEY_LENGTH} characters."
    
    if not KEY_PATTERN.match(key):
        return False, "Key can only contain alphanumeric characters, underscores, hyphens, and dots."
    
    return True, None

def validate_value(value: str) -> tuple[bool, Optional[str]]:
    """
    Validate a value for the vault.
    
    Args:
        value (str): The value to validate
        
    Returns:
        tuple[bool, Optional[str]]: A tuple containing (is_valid, error_message)
    """
    if not value:
        return False, "Value cannot be empty."
    
    if len(value) > MAX_VALUE_LENGTH:
        return False, f"Value is too long. Maximum length is {MAX_VALUE_LENGTH} characters."
    
    return True, None

def validate_files(db_path: str, key_type: str, key_file: str) -> tuple[bool, Optional[str]]:
    """
    Validate that the database and key files exist or can be created.
    
    Args:
        db_path (str): Path to the database file
        key_type (str): Type of key to use (file or env)
        key_file (str): Path to the key file
        
    Returns:
        tuple[bool, Optional[str]]: A tuple containing (is_valid, error_message)
    """
    
    # For db_path, we just check if the directory exists and is writable
    db_dir: str = os.path.dirname(db_path) or '.'
    if not os.path.exists(db_dir):
        return False, f"Directory for database '{db_dir}' does not exist."
    
    if not os.access(db_dir, os.W_OK):
        return False, f"Directory for database '{db_dir}' is not writable."

    # Check if a key file exists
    if key_type == "file" and not os.path.exists(key_file):
        return False, f"Key file '{key_file}' does not exist."
    
    return True, None

def main() -> None:
    parser = argparse.ArgumentParser(description="Simple Offline Database Vault")
    parser.add_argument("action", help="Action to perform (add, retrieve, delete)", choices=["add", "retrieve", "delete"])
    parser.add_argument("--key_type", help="Type of key to use (default: \"env\")", choices=["file", "env"], required=False, default="env")
    parser.add_argument("--db_path", help="Path to the SQLite database file. Defaults to \"vault.db\"", required=False, default="vault.db")
    parser.add_argument("--key_file", help="Path to the key file. Defaults to \"master.key\" only if key_type is \"env\"", required=False, default="master.key")
    args: argparse.Namespace = parser.parse_args()
    
    # Validate files
    is_valid: bool
    error_message: Optional[str]
    is_valid, error_message = validate_files(args.db_path, args.key_type, args.key_file)
    if not is_valid:
        logger.error(error_message)
        return
    
    try:
        vault: DatabaseVault = get_database_vault(args.db_path, args.key_file)
    except Exception as e:
        logger.error(f"Failed to initialize vault: {e}")
        return

    if args.action == "add":
        keyToAdd: str = input("Enter key to add: ")
        is_valid, error_message = validate_key(keyToAdd)
        if not is_valid:
            logger.error(error_message)
            return

        valueToAdd: str = input("Enter value to add: ")
        is_valid, error_message = validate_value(valueToAdd)
        if not is_valid:
            logger.error(error_message)
            return

        try:
            success: bool = vault.add_entry(keyToAdd, valueToAdd)
            if success:
                logger.info(f"Added key[{keyToAdd}] with value[{valueToAdd}] successfully to Offline Database Vault!")
            else:
                logger.error(f"Failed to add key[{keyToAdd}] to Offline Database Vault.")
        except TypeError as e:
            logger.error(f"Type error: {e}")
        except Exception as e:
            logger.error(f"Error adding entry: {e}")
            
    elif args.action == "delete":
        keyToDelete: str = input("Enter key to delete: ")
        is_valid, error_message = validate_key(keyToDelete)
        if not is_valid:
            logger.error(error_message)
            return

        try:
            success: bool = vault.delete_entry(keyToDelete)
            if success:
                logger.info(f"Deleted key[{keyToDelete}] successfully from Offline Database Vault!")
            else:
                logger.warning(f"No entry found for key[{keyToDelete}] to delete from Offline Database Vault.")
        except TypeError as e:
            logger.error(f"Type error: {e}")
        except Exception as e:
            logger.error(f"Error deleting entry: {e}")
            
    elif args.action == "retrieve":
        keyToRetrieve: str = input("Enter key to retrieve: ")
        is_valid, error_message = validate_key(keyToRetrieve)
        if not is_valid:
            logger.error(error_message)
            return

        try:
            value: str = vault.retrieve_entry(keyToRetrieve)
            if value:
                logger.info(f"Retrieved Value for key[{keyToRetrieve}] is: [{value}] from Offline Database Vault!")
            else:
                logger.warning(f"No value found for key[{keyToRetrieve}] to be retrieved from Offline Database Vault!")
        except TypeError as e:
            logger.error(f"Type error: {e}")
        except Exception as e:
            logger.error(f"Error retrieving entry: {e}")

if __name__ == "__main__":
    main()