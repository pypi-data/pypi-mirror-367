# Fernet Key Vault

A simple Python SQLite3-based key-value storage vault for securely storing and retrieving data using Fernet symmetric encryption.

## Project Architecture

FernetKeyVault follows a modular design with a clear separation of concerns:

### Core Components

1. **DatabaseVault** (`database_vault.py`):
   - Main class that provides the key-value storage functionality
   - Integrates encryption and key management
   - Handles SQLite database operations with WAL mode

2. **EncryptionManager** (`encryption_manager.py`):
   - Handles encryption and decryption using Fernet symmetric encryption
   - Provides type-safe encrypt/decrypt methods

3. **KeyLoader** (`key_loader.py`):
   - Abstract interface for loading encryption keys
   - Implementations:
     - `FileKeyLoader`: Loads keys from files
     - `EnvironmentKeyLoader`: Loads keys from environment variables

### Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  KeyLoader  │────▶│EncryptionMgr│◀────▶│DatabaseVault│
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Key File/  │     │ Encryption/ │     │   SQLite    │
│    Env Var  │     │ Decryption  │     │  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
```

1. **Key Loading**: KeyLoader retrieves the encryption key from a file or environment variable
2. **Encryption**: EncryptionManager uses the key to encrypt/decrypt values
3. **Storage**: DatabaseVault stores and retrieves encrypted values in the SQLite database

### Design Principles

- **Modularity**: Components can be replaced or extended independently
- **Encapsulation**: Implementation details are hidden behind clean interfaces
- **Type Safety**: Type hints and validation throughout the codebase
- **Error Handling**: Comprehensive error handling at all levels

## Features

- **Secure Storage**: Store key-value pairs in an SQLite database with Fernet symmetric encryption
- **Key Management**: Flexible key loading from files or environment variables
- **Data Operations**: Add, retrieve, and delete encrypted entries
- **Concurrency Support**: SQLite WAL (Write-Ahead Logging) mode for concurrent read operations
- **Error Handling**: Comprehensive error handling and input validation
- **Logging**: Built-in logging system for tracking operations and errors
- **Type Safety**: Type checking for all operations
- **Extensibility**: Modular design with clear interfaces for customization

## Installation

### From PyPI (Recommended)

You can install the package directly from PyPI:

```bash
uv pip install FernetKeyVault
```

### From Source

You can also install the package directly from the source code:

```bash
# Clone the repository
git clone https://github.com/kvcrajan/FernetKeyVault.git
cd FernetKeyVault

# Install the package
uv pip install .
```

For development, you can install the package in editable mode:

```bash
uv pip install -e .
```

### Dependencies

The package has the following dependencies:
- Python >= 3.8
- cryptography >= 45.0.5 (for Fernet encryption)
- hatchling >= 1.27.0

For testing, additional dependencies are required:
- pytest >= 8.4.1
- pytest-cov >= 6.2.1

These dependencies will be automatically installed when you install the package using uv.


## Building the Package

This section provides instructions for building the FernetKeyVault library distribution packages.

### Prerequisites

Before you can build the package, you need to have the following tools installed:

```bash
# Install uv
pip install uv
```

### Building Distribution Packages

To build the distribution packages (source distribution and wheel), you have two options:

#### Option 1: Using uv

```bash
# Navigate to the project root directory
cd /path/to/FernetKeyVault

# Build the distribution packages
uv build
```

#### Option 2: Using python -m build

```bash
# Navigate to the project root directory
cd /path/to/FernetKeyVault

# Build the distribution packages
python -m build
```

Both methods will create two files in the `dist/` directory:
- A source distribution (`.tar.gz` file)
- A wheel distribution (`.whl` file)


## Testing

This project uses the pytest framework for testing. The test suite includes comprehensive tests for all components of the FernetKeyVault project.

### Test Files

The project includes the following test files:

1. `test_encryption_manager.py`: Tests for the `EncryptionManager` class
2. `test_key_loader.py`: Tests for the `KeyLoader` implementations
3. `test_database_vault.py`: Tests for the `DatabaseVault` class

### Test Coverage

#### EncryptionManager Tests

The `test_encryption_manager.py` file tests:

- Initialization with a valid key
- Encryption and decryption cycle
- Type validation for encrypt and decrypt methods
- Error handling for invalid tokens
- Security aspects (different keys being incompatible)
- Edge cases:
  - Empty strings
  - Special characters
  - Unicode characters

#### KeyLoader Tests

The `test_key_loader.py` file tests:

- **FileKeyLoader**:
  - Loading a key from a valid file
  - Error handling when key_file is None
  - Error handling when the key file doesn't exist
  - Handling empty key files

- **EnvironmentKeyLoader**:
  - Loading a key from an environment variable
  - Handling non-existent environment variables
  - Using the default environment variable name

#### DatabaseVault Tests

The `test_database_vault.py` file tests:

- Initialization and database setup
- Adding entries to the vault
- Retrieving entries from the vault
- Deleting entries from the vault
- Updating existing entries
- Type validation for keys and values
- Error handling for database operations
- Handling non-existent keys

### Purpose of WAL and SHM Files in test_wal_mode.py

In the `test_wal_mode.py` file, WAL (Write-Ahead Logging) and SHM (Shared Memory) files are SQLite-specific auxiliary files that are created when a database operates in WAL mode. Let's explore their purpose:

#### WAL (Write-Ahead Logging) Files

The WAL file (`test_db_path-wal`) serves these key purposes:
1. **Transaction Management**: Instead of writing changes directly to the main database file, SQLite writes them to the WAL file first
2. **Crash Recovery**: If the application crashes during a write operation, the WAL file helps SQLite recover and maintain database integrity
3. **Concurrency Support**: WAL mode allows multiple readers to access the database simultaneously while a writer is active, which is being tested in the `concurrent_read_test()` function

#### SHM (Shared Memory) Files

The SHM file (`test_db_path-shm`) serves these purposes:
1. **Index Management**: It contains an index of the WAL file to speed up database operations
2. **Shared Memory**: It facilitates communication between different database connections
3. **Concurrency Control**: It helps manage concurrent access to the database by multiple processes

#### Why They're Used in the Tests

The test script verifies two important aspects of WAL mode:

1. **WAL Mode Enablement**: The `test_wal_mode_enabled()` function checks if WAL mode is properly enabled when the `DatabaseVault` is initialized:
2. **Concurrent Access**: The `concurrent_read_test()` function tests that multiple reader threads can access the database simultaneously, which is a key benefit of WAL mode.

#### Summary

WAL and SHM files are SQLite's implementation details for enabling Write-Ahead Logging mode, which provides better concurrency and reliability. The test script verifies that this mode is correctly enabled in the `DatabaseVault` class and demonstrates its concurrent read capabilities.


### Running the Tests

#### Prerequisites

1. Install the required dependencies:

```bash
uv pip install -r requirements.txt
```

This will install both the main dependencies and the test dependencies.

1. Install the package in development mode:

```bash
uv pip install -e .
```

This creates an "editable" installation, which means changes to the source code will be immediately reflected without needing to reinstall the package.

1. Note about `conftest.py`:

The project includes a `conftest.py` file in the root directory that configures pytest to properly find and import the modules. This file adds the project root directory to the Python path, allowing the test files to import the modules directly.

#### Running All Tests

To run all tests:

```bash
pytest
```

#### Running Tests with Coverage

To run tests with coverage reporting:

```bash
pytest --cov=. --cov-report=term
```

#### Running Specific Test Files

To run tests for a specific module:

```bash
pytest test_encryption_manager.py
pytest test_key_loader.py
pytest test_database_vault.py
```

#### Running Specific Test Cases

To run a specific test case:

```bash
pytest test_encryption_manager.py::TestEncryptionManager::test_encrypt_decrypt_cycle
```

### Test Design Approach

The tests follow these principles:

1. **Isolation**: Each test is isolated and doesn't depend on the state from other tests.
2. **Fixtures**: Pytest fixtures are used for setup and teardown.
3. **Mocking**: Dependencies are mocked where appropriate to isolate the unit being tested.
4. **Edge Cases**: Tests cover both normal operation and edge cases.
5. **Error Handling**: Tests verify that errors are handled correctly.

### Continuous Integration

It's recommended to integrate these tests into your CI/CD pipeline to ensure code quality is maintained as the project evolves.


## Deployment

### Deploying to TestPyPI (Recommended for Testing)

Before deploying to the main PyPI repository, it's recommended to test your package on TestPyPI:

```bash
# Upload to TestPyPI
uv publish --repository testpypi dist/*
```

You will be prompted for your TestPyPI username and password. If you don't have a TestPyPI account, you can create one at [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/).

To install the package from TestPyPI:

```bash
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ FernetKeyVault
```

### Deploying to PyPI

Once you've tested your package on TestPyPI and confirmed it works correctly, you can deploy it to the main PyPI repository:

```bash
# Upload to PyPI
uv publish dist/*
```

You will be prompted for your PyPI username and password. If you don't have a PyPI account, you can create one at [https://pypi.org/account/register/](https://pypi.org/account/register/).

### Updating an Existing Package

To update an existing package on PyPI:

1. Update the version number in `pyproject.toml`
2. Rebuild the distribution packages
3. Upload to PyPI using uv

```bash
# Update version in pyproject.toml
# Then build and upload
uv build
uv publish dist/*
```

### As a Library in Your Project

The most common way to deploy FernetKeyVault is as a library within your own Python application:

1. Install the package:
   ```bash
   uv pip install FernetKeyVault
   ```

2. Import and use in your code:
   ```python
   from FernetKeyVault import get_database_vault
   
   # Initialize with default settings
   # This uses the singleton pattern with memory-safe caching
   vault = get_database_vault()
   
   # Or customize the configuration
   # The same parameters as DatabaseVault constructor are supported
   vault = get_database_vault(
       db_path="/path/to/your/database.db",
       key_file="/path/to/your/key.key"
   )
   
   # When you're done with the vault, you can optionally remove it from the cache
   # This is not necessary as weak references allow automatic garbage collection
   # from FernetKeyVault import remove_database_vault_from_cache
   # remove_database_vault_from_cache(db_path="/path/to/your/database.db", key_file="/path/to/your/key.key")
   ```

3. Ensure your key file is properly secured and backed up.

### Security Considerations for Deployment

When deploying to production environments:

1. **Key Management**:
   - Store encryption keys securely, separate from the database
   - Environment variables are used by default (via `EnvironmentKeyLoader`)
   - Implement proper key rotation procedures

2. **Database Location**:
   - Store the database file in a secure, backed-up location
   - Ensure proper file permissions are set

3. **Access Control**:
   - Limit access to both the database and key files
   - Implement application-level access controls

4. **Backup Strategy**:
   - Regularly back up both the database and encryption keys
   - Test restoration procedures

### Containerized Deployment

If deploying in a containerized environment (e.g., Docker):

1. Create a Dockerfile:
   ```dockerfile
   FROM python:3.8-slim
   
   WORKDIR /app
   
   # Install uv
   RUN pip install uv
   
   COPY requirements.txt .
   RUN uv pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["python", "your_application.py"]
   ```

2. Use Docker secrets or environment variables (default) for key management:
   ```bash
   docker run -e MASTER_KEY="your-base64-encoded-key" your-image
   ```


## Usage

### Command-Line Interface (CLI)

FernetKeyVault includes a command-line interface (vault.py) that provides a simple way to interact with the vault:

```bash
# Add an entry
python vault.py add [--db_path DB_PATH] [--key_file KEY_FILE]

# Retrieve an entry
python vault.py retrieve [--db_path DB_PATH] [--key_file KEY_FILE]

# Delete an entry
python vault.py delete [--db_path DB_PATH] [--key_file KEY_FILE]
```

#### CLI Input Validation

The CLI includes comprehensive input validation:

1. **File Validation**:
   - Validates that the key file exists
   - Validates that the database directory exists and is writable

2. **Key Validation**:
   - Validates that keys are not empty
   - Validates that keys are within the maximum length (100 characters)
   - Validates that keys only contain alphanumeric characters, underscores, hyphens, and dots

3. **Value Validation**:
   - Validates that values are not empty
   - Validates that values are within the maximum length (1000 characters)

4. **Error Handling**:
   - Provides clear error messages for validation failures
   - Handles exceptions from the vault operations

Example usage:

```bash
# Add an entry
$ python vault.py add
Enter key to add: my_api_key
Enter value to add: sk_test_abcdefghijklmnopqrstuvwxyz

# Retrieve an entry
$ python vault.py retrieve
Enter key to retrieve: my_api_key

# Delete an entry
$ python vault.py delete
Enter key to delete: my_api_key
```

### Basic Usage (Library)

```python
from FernetKeyVault import get_database_vault

# Initialize the vault (creates vault.db by default)
# This uses the singleton pattern with memory-safe caching
vault = get_database_vault()

# Add entries
vault.add_entry("username", "admin")
vault.add_entry("api_key", "sk_test_abcdefghijklmnopqrstuvwxyz")

# Retrieve entries
username = vault.retrieve_entry("username")
print(f"Username: {username}")  # Output: Username: admin

# Delete entries
vault.delete_entry("username")

# When you're done with the vault, you can optionally remove it from the cache
# This is not necessary as weak references allow automatic garbage collection
# from FernetKeyVault import remove_database_vault_from_cache
# remove_database_vault_from_cache()
```

### Custom Database Path

You can specify a custom path for the database file:

```python
from FernetKeyVault import get_database_vault

vault = get_database_vault(db_path="/path/to/custom/vault.db")
```

### Concurrent Read Operations

The vault uses SQLite's WAL (Write-Ahead Logging) mode, which allows multiple readers to access the database simultaneously without blocking each other. This is particularly useful in multithreaded or multiprocess applications:

### Logging

FernetKeyVault includes a built-in logging system that provides information about operations and errors. By default, log messages are output to the console with appropriate log levels:

```python
import logging
from FernetKeyVault import get_database_vault

# Configure logging to see all log messages
logging.basicConfig(level=logging.DEBUG)

# Get a logger for your application
logger = logging.getLogger('your_app')

# Get a vault instance
vault = get_database_vault()

# The vault will log operations and errors
# For example, when an error occurs:
try:
    vault.add_entry(123, "value")  # Invalid key type
except TypeError as e:
    logger.error(f"Error: {e}")

# You can also customize the logging configuration
logger = logging.getLogger('FernetKeyVault')
logger.setLevel(logging.WARNING)  # Only show warnings and errors
```

Log messages include:
- ERROR: Database errors, key loading errors, and other critical issues
- WARNING: Non-critical issues like missing entries or WAL mode issues
- INFO: Successful operations (when log level is set to INFO or lower)

```python
import threading
from FernetKeyVault import get_database_vault, remove_database_vault_from_cache, clear_database_vault_cache

# Initialize a shared vault
# The get_database_vault function ensures we use a singleton pattern with memory-safe caching
shared_vault = get_database_vault(db_path="shared_vault.db", key_file="master.key")
shared_vault.add_entry("shared_key", "shared_value")

# Function for reader threads
def reader_thread(thread_id):
    # Each thread can use the same vault instance thanks to the singleton pattern
    # This demonstrates the benefit of using get_database_vault over direct instantiation
    local_vault = get_database_vault(db_path="shared_vault.db", key_file="master.key")
    value = local_vault.retrieve_entry("shared_key")
    print(f"Thread {thread_id} read: {value}")

# Create multiple reader threads
threads = []
for i in range(3):
    thread = threading.Thread(target=reader_thread, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Explicitly remove the vault from the cache when no longer needed
# This is optional as weak references will allow garbage collection automatically
# when the vault is no longer referenced elsewhere in the code
remove_database_vault_from_cache(db_path="shared_vault.db", key_file="master.key")

# For applications that need to manage memory more aggressively,
# you can clear the entire cache at once
# clear_database_vault_cache()
```

### Error Handling

The methods return appropriate values to indicate success or failure:

- `add_entry()`: Returns `True` if successful, `False` otherwise
- `retrieve_entry()`: Returns the value if found, `None` otherwise
- `delete_entry()`: Returns `True` if an entry was deleted, `False` otherwise

## API Reference

### `get_database_vault(db_path="vault.db", key_file="master.key", **kwargs)`

Returns a singleton instance of DatabaseVault with caching behavior. This is the recommended way to create a DatabaseVault instance as it provides several benefits over direct instantiation:

- **Singleton Pattern**: Ensures only one instance exists for a given database path and key file
- **Memory-Safe Caching**: Improves performance by reusing existing instances while preventing memory leaks through weak references
- **Thread Safety**: Safe to use in multithreaded applications
- **Automatic Cleanup**: Instances are automatically removed from the cache when they're no longer used elsewhere in the code

**Parameters:**
- `db_path` (str, optional): Path to the SQLite database file. Defaults to "vault.db"
- `key_file` (str, optional): Path to the key file. Defaults to "master.key"
- `**kwargs`: Additional arguments to pass to the DatabaseVault constructor.

**Returns:**
- `DatabaseVault`: A singleton instance of the DatabaseVault class.

**Import:**
```python
from FernetKeyVault import get_database_vault
```

### `remove_database_vault_from_cache(db_path="vault.db", key_file="master.key")`

Explicitly removes a DatabaseVault instance from the cache. This can be useful for managing memory usage or forcing a new instance to be created on the next call to `get_database_vault`.

**Parameters:**
- `db_path` (str, optional): Path to the SQLite database file. Defaults to "vault.db"
- `key_file` (str, optional): Path to the key file. Defaults to "master.key"

**Returns:**
- `bool`: True if the instance was found and removed, False otherwise.

**Import:**
```python
from FernetKeyVault import remove_database_vault_from_cache
```

### `clear_database_vault_cache()`

Clears all DatabaseVault instances from the cache. This can be useful for managing memory usage or forcing new instances to be created on subsequent calls to `get_database_vault`.

**Returns:**
- None

**Import:**
```python
from FernetKeyVault import clear_database_vault_cache
```

### `DatabaseVault(db_path="vault.db", key_file="master.key", key_loader=None, encryption_manager=None)`

Initialize a new DatabaseVault instance. The database is automatically configured to use SQLite's WAL (Write-Ahead Logging) mode for improved concurrency support, allowing multiple readers to access the database simultaneously.

**Parameters:**
- `db_path` (str, optional): Path to the SQLite database file. Defaults to "vault.db"
- `key_file` (str, optional): Path to the key file. Defaults to "master.key"
- `key_loader` (KeyLoader, optional): Key loader implementation. Defaults to EnvironmentKeyLoader.
- `encryption_manager` (EncryptionManager, optional): Custom encryption manager. If None, a new one is created.

### `add_entry(key, value)`

Add a key-value pair to the vault. If the key already exists, its value will be updated.

**Parameters:**
- `key` (str): The key for the entry
- `value` (str): The value to store

**Returns:**
- `bool`: True if successful, False otherwise

**Raises:**
- `TypeError`: If key or value is not a string

### `retrieve_entry(key)`

Retrieve a value from the vault using its key.

**Parameters:**
- `key` (str): The key to look up

**Returns:**
- `str` or `None`: The value associated with the key, or None if the key doesn't exist

**Raises:**
- `TypeError`: If key is not a string

### `delete_entry(key)`

Delete an entry from the vault using its key.

**Parameters:**
- `key` (str): The key of the entry to delete

**Returns:**
- `bool`: True if an entry was deleted, False otherwise

**Raises:**
- `TypeError`: If key is not a string

## Python Installation, Build, and Packaging References

https://realpython.com/python-uv/

https://packaging.python.org/en/latest/flow/
https://packaging.python.org/en/latest/tutorials/installing-packages/
https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
https://medium.com/@ebimsv/building-python-packages-07fbfbb959a9
https://medium.com/clarityai-engineering/migrating-from-pipenv-pipfile-to-uv-59ba2846636f
https://pypi.org/account/login/

## Development References

https://pythononline.net/
https://codepal.ai/
https://testdriven.io/blog/python-concurrency-parallelism/#conclusion
https://www.linkedin.com/pulse/pyre-type-checker-python-nadir-riyani-t0xwf/
https://www.linkedin.com/pulse/good-practices-documenting-python-code-claudio-shigueo-watanabe/
https://medium.com/@sohail_saifi/the-python-feature-thats-10x-faster-than-loops-but-only-3-of-developers-know-it-f8580aece8be