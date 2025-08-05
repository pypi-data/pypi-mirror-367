from abc import ABC, abstractmethod
import logging
from typing import Optional

# Get a module-level logger
logger = logging.getLogger('FernetKeyVault.key_loader')


# Define an interface for key loading
class KeyLoader(ABC):
    @abstractmethod
    def load_key(self, key_file: str = None):
        """Load a key from a source"""
        pass


# Concrete implementation of the key loader
class FileKeyLoader(KeyLoader):
    def load_key(self, key_file: str = None) -> bytes | None:
        """
        Load a pass key from a file.

        Args:
            key_file (str): Path to the key file.

        Returns:
            str or None: The key as a string if successful, None otherwise

        Raises:
            FileNotFoundError: If the key file doesn't exist,
            ValueError: If key_file is None
        """

        if key_file is None:
            raise ValueError("Key file path cannot be None")

        try:
            with open(key_file, 'rb') as file:
                key: bytes = file.read().strip()
            return key
        except FileNotFoundError:
            logger.error(f"Key file '{key_file}' not found.")
            raise
        except Exception as e:
            logger.error(f"Error loading key: {e}")
            return None


# With a different key loader implementation
class EnvironmentKeyLoader(KeyLoader):
    def load_key(self, key_env_var: str = "MASTER_KEY") -> Optional[str]:
        import os
        return os.environ.get(key_env_var)
