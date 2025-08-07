"""
Secure Credential Management Module

This module provides secure storage, retrieval, and rotation of credentials
such as API keys, with support for different storage backends.
"""

import os
import json
import base64
import time
import uuid
import getpass
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
import hashlib
import hmac
import logging
import warnings

# Try to import optional dependencies
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    warnings.warn("keyring package not available. System keyring storage will be disabled.")

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    warnings.warn("cryptography package not available. Encrypted storage will be disabled.")

from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Constants
DEFAULT_CREDENTIALS_FILE = "credentials.json"
DEFAULT_SERVICE_NAME = "url_analyzer"
DEFAULT_EXPIRATION_DAYS = 90  # Default credential expiration in days
DEFAULT_ROTATION_WARNING_DAYS = 7  # Warn about expiration this many days before
DEFAULT_ENCRYPTION_ITERATIONS = 100000  # Number of iterations for key derivation


class CredentialError(Exception):
    """Exception raised for credential-related errors."""
    pass


class CredentialManager:
    """
    Secure credential manager for storing and retrieving sensitive information.
    
    Features:
    - Multiple storage backends (environment, file, system keyring)
    - Encryption for file-based storage
    - Credential rotation and expiration
    - Audit logging
    """
    
    def __init__(
        self,
        service_name: str = DEFAULT_SERVICE_NAME,
        credentials_file: str = DEFAULT_CREDENTIALS_FILE,
        master_password: Optional[str] = None,
        use_keyring: bool = KEYRING_AVAILABLE,
        use_encryption: bool = ENCRYPTION_AVAILABLE,
        auto_save: bool = True
    ):
        """
        Initialize the credential manager.
        
        Args:
            service_name: Name of the service for keyring storage
            credentials_file: Path to the credentials file
            master_password: Master password for encryption (if None, will prompt if needed)
            use_keyring: Whether to use system keyring for storage
            use_encryption: Whether to encrypt file-based storage
            auto_save: Whether to automatically save changes to credentials
        """
        self.service_name = service_name
        self.credentials_file = credentials_file
        self.master_password = master_password
        self.use_keyring = use_keyring and KEYRING_AVAILABLE
        self.use_encryption = use_encryption and ENCRYPTION_AVAILABLE
        self.auto_save = auto_save
        
        # Initialize storage
        self.credentials = {}
        self.encryption_key = None
        
        # Load credentials
        self._load_credentials()
    
    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Derive an encryption key from a password.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (if None, generates a new one)
            
        Returns:
            Tuple of (key, salt)
        """
        if not ENCRYPTION_AVAILABLE:
            raise CredentialError("Encryption is not available. Install the cryptography package.")
        
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=DEFAULT_ENCRYPTION_ITERATIONS
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def _encrypt(self, data: str) -> Dict[str, str]:
        """
        Encrypt data with the master password.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        if not ENCRYPTION_AVAILABLE:
            raise CredentialError("Encryption is not available. Install the cryptography package.")
        
        # Get or prompt for master password
        if self.master_password is None:
            self.master_password = getpass.getpass("Enter master password for credential encryption: ")
        
        # Generate salt and derive key
        salt = os.urandom(16)
        key, _ = self._derive_key(self.master_password, salt)
        
        # Encrypt the data
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        
        return {
            "data": base64.b64encode(encrypted_data).decode(),
            "salt": base64.b64encode(salt).decode(),
            "method": "fernet",
            "kdf": "pbkdf2",
            "kdf_iterations": DEFAULT_ENCRYPTION_ITERATIONS,
            "timestamp": datetime.now().isoformat()
        }
    
    def _decrypt(self, encrypted: Dict[str, str]) -> str:
        """
        Decrypt data with the master password.
        
        Args:
            encrypted: Dictionary with encrypted data and metadata
            
        Returns:
            Decrypted data
        """
        if not ENCRYPTION_AVAILABLE:
            raise CredentialError("Encryption is not available. Install the cryptography package.")
        
        # Get or prompt for master password
        if self.master_password is None:
            self.master_password = getpass.getpass("Enter master password for credential decryption: ")
        
        # Extract encryption metadata
        salt = base64.b64decode(encrypted["salt"])
        encrypted_data = base64.b64decode(encrypted["data"])
        
        # Derive key
        key, _ = self._derive_key(self.master_password, salt)
        
        # Decrypt the data
        try:
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            raise CredentialError(f"Failed to decrypt data: {e}. Incorrect password?")
    
    def _load_credentials(self) -> None:
        """Load credentials from all available sources."""
        # Start with an empty credentials dictionary
        self.credentials = {}
        
        # Load from file if it exists
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    file_credentials = json.load(f)
                
                # Check if the file is encrypted
                if isinstance(file_credentials, dict) and "data" in file_credentials and "salt" in file_credentials:
                    # Decrypt the file
                    if self.use_encryption and ENCRYPTION_AVAILABLE:
                        decrypted_data = self._decrypt(file_credentials)
                        file_credentials = json.loads(decrypted_data)
                    else:
                        logger.warning("Encrypted credentials file found but encryption is disabled.")
                        file_credentials = {}
                
                # Update credentials
                self.credentials.update(file_credentials)
                logger.debug(f"Loaded credentials from {self.credentials_file}")
            except Exception as e:
                logger.error(f"Error loading credentials from file: {e}")
        
        # Check for expired credentials
        self._check_expirations()
    
    def _save_credentials(self) -> None:
        """Save credentials to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.credentials_file)), exist_ok=True)
            
            # Prepare data for saving
            data = json.dumps(self.credentials, indent=2)
            
            # Encrypt if enabled
            if self.use_encryption and ENCRYPTION_AVAILABLE:
                encrypted = self._encrypt(data)
                with open(self.credentials_file, 'w') as f:
                    json.dump(encrypted, f, indent=2)
            else:
                with open(self.credentials_file, 'w') as f:
                    f.write(data)
            
            logger.debug(f"Saved credentials to {self.credentials_file}")
        except Exception as e:
            logger.error(f"Error saving credentials to file: {e}")
            raise CredentialError(f"Failed to save credentials: {e}")
    
    def _check_expirations(self) -> None:
        """Check for expired credentials and issue warnings."""
        now = datetime.now()
        warning_threshold = now + timedelta(days=DEFAULT_ROTATION_WARNING_DAYS)
        
        for cred_id, cred_data in list(self.credentials.items()):
            # Skip if no expiration
            if "expiration" not in cred_data:
                continue
            
            try:
                expiration = datetime.fromisoformat(cred_data["expiration"])
                
                # Check if expired
                if expiration <= now:
                    logger.warning(f"Credential '{cred_id}' has expired on {expiration}.")
                    
                    # Mark as expired
                    self.credentials[cred_id]["status"] = "expired"
                    
                    # Auto-save if enabled
                    if self.auto_save:
                        self._save_credentials()
                
                # Check if nearing expiration
                elif expiration <= warning_threshold:
                    days_left = (expiration - now).days
                    logger.warning(f"Credential '{cred_id}' will expire in {days_left} days.")
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid expiration date for credential '{cred_id}': {e}")
    
    def set_credential(
        self,
        credential_id: str,
        value: str,
        description: str = "",
        expiration_days: int = DEFAULT_EXPIRATION_DAYS,
        metadata: Optional[Dict[str, Any]] = None,
        storage: str = "file"  # "file", "keyring", "env"
    ) -> None:
        """
        Store a credential.
        
        Args:
            credential_id: Unique identifier for the credential
            value: The credential value to store
            description: Human-readable description of the credential
            expiration_days: Number of days until the credential expires
            metadata: Additional metadata to store with the credential
            storage: Storage backend to use
        """
        # Validate storage option
        if storage == "keyring" and not self.use_keyring:
            logger.warning("Keyring storage requested but not available. Falling back to file storage.")
            storage = "file"
        
        # Calculate expiration date
        expiration = datetime.now() + timedelta(days=expiration_days)
        
        # Create credential record
        credential_data = {
            "description": description,
            "created": datetime.now().isoformat(),
            "expiration": expiration.isoformat(),
            "last_rotated": datetime.now().isoformat(),
            "storage": storage,
            "status": "active",
            "metadata": metadata or {}
        }
        
        # Store the credential
        if storage == "keyring" and self.use_keyring:
            # Store in system keyring
            keyring.set_password(self.service_name, credential_id, value)
            
            # Store metadata in file (without the actual credential)
            self.credentials[credential_id] = credential_data
            logger.info(f"Stored credential '{credential_id}' in system keyring")
        elif storage == "env":
            # Store metadata in file (without the actual credential)
            credential_data["env_var"] = credential_id.upper()
            self.credentials[credential_id] = credential_data
            
            # Provide instructions for setting the environment variable
            logger.info(f"Credential '{credential_id}' configured to use environment variable '{credential_id.upper()}'")
            print(f"\n✅ To use this credential, set the environment variable: {credential_id.upper()}")
            print(f"   Example: export {credential_id.upper()}='{value}'\n")
        else:
            # Store in file
            credential_data["value"] = value
            self.credentials[credential_id] = credential_data
            logger.info(f"Stored credential '{credential_id}' in credentials file")
        
        # Save changes
        if self.auto_save:
            self._save_credentials()
        
        # Log the action
        self._log_credential_action("create", credential_id)
    
    def get_credential(self, credential_id: str) -> Optional[str]:
        """
        Retrieve a credential.
        
        Args:
            credential_id: Unique identifier for the credential
            
        Returns:
            The credential value or None if not found
        """
        # Check if credential exists
        if credential_id not in self.credentials:
            logger.warning(f"Credential '{credential_id}' not found")
            return None
        
        # Get credential data
        cred_data = self.credentials[credential_id]
        
        # Check if expired
        if cred_data.get("status") == "expired":
            logger.warning(f"Credential '{credential_id}' has expired")
            return None
        
        # Retrieve based on storage type
        storage = cred_data.get("storage", "file")
        
        if storage == "keyring" and self.use_keyring:
            # Retrieve from system keyring
            try:
                value = keyring.get_password(self.service_name, credential_id)
                if value is None:
                    logger.error(f"Credential '{credential_id}' not found in keyring")
                    return None
                return value
            except Exception as e:
                logger.error(f"Error retrieving credential from keyring: {e}")
                return None
        elif storage == "env":
            # Retrieve from environment variable
            env_var = cred_data.get("env_var", credential_id.upper())
            value = os.environ.get(env_var)
            if value is None:
                logger.warning(f"Environment variable '{env_var}' not set")
                return None
            return value
        else:
            # Retrieve from file
            return cred_data.get("value")
    
    def rotate_credential(
        self,
        credential_id: str,
        new_value: Optional[str] = None,
        expiration_days: int = DEFAULT_EXPIRATION_DAYS,
        generator: Optional[Callable[[], str]] = None
    ) -> Optional[str]:
        """
        Rotate a credential by updating its value and expiration.
        
        Args:
            credential_id: Unique identifier for the credential
            new_value: New value for the credential (if None, generates one)
            expiration_days: Number of days until the credential expires
            generator: Function to generate a new credential value
            
        Returns:
            The new credential value or None if rotation failed
        """
        # Check if credential exists
        if credential_id not in self.credentials:
            logger.error(f"Cannot rotate non-existent credential '{credential_id}'")
            return None
        
        # Get credential data
        cred_data = self.credentials[credential_id]
        storage = cred_data.get("storage", "file")
        
        # Generate new value if not provided
        if new_value is None:
            if generator is not None:
                new_value = generator()
            else:
                # Default generator: random string
                new_value = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('=')
        
        # Update expiration
        expiration = datetime.now() + timedelta(days=expiration_days)
        cred_data["expiration"] = expiration.isoformat()
        cred_data["last_rotated"] = datetime.now().isoformat()
        cred_data["status"] = "active"
        
        # Store the new value
        if storage == "keyring" and self.use_keyring:
            # Update in system keyring
            try:
                keyring.set_password(self.service_name, credential_id, new_value)
                logger.info(f"Rotated credential '{credential_id}' in system keyring")
            except Exception as e:
                logger.error(f"Error rotating credential in keyring: {e}")
                return None
        elif storage == "env":
            # Provide instructions for updating the environment variable
            env_var = cred_data.get("env_var", credential_id.upper())
            logger.info(f"Credential '{credential_id}' rotated. Update environment variable '{env_var}'")
            print(f"\n✅ Update your environment variable with the new value: {env_var}")
            print(f"   Example: export {env_var}='{new_value}'\n")
        else:
            # Update in file
            cred_data["value"] = new_value
            logger.info(f"Rotated credential '{credential_id}' in credentials file")
        
        # Save changes
        if self.auto_save:
            self._save_credentials()
        
        # Log the action
        self._log_credential_action("rotate", credential_id)
        
        return new_value
    
    def delete_credential(self, credential_id: str) -> bool:
        """
        Delete a credential.
        
        Args:
            credential_id: Unique identifier for the credential
            
        Returns:
            True if deletion was successful, False otherwise
        """
        # Check if credential exists
        if credential_id not in self.credentials:
            logger.warning(f"Cannot delete non-existent credential '{credential_id}'")
            return False
        
        # Get credential data
        cred_data = self.credentials[credential_id]
        storage = cred_data.get("storage", "file")
        
        # Delete from storage
        if storage == "keyring" and self.use_keyring:
            # Delete from system keyring
            try:
                keyring.delete_password(self.service_name, credential_id)
                logger.info(f"Deleted credential '{credential_id}' from system keyring")
            except Exception as e:
                logger.error(f"Error deleting credential from keyring: {e}")
                return False
        elif storage == "env":
            # Provide instructions for unsetting the environment variable
            env_var = cred_data.get("env_var", credential_id.upper())
            logger.info(f"Credential '{credential_id}' deleted. Unset environment variable '{env_var}'")
            print(f"\n✅ Unset your environment variable: {env_var}")
            print(f"   Example: unset {env_var}\n")
        
        # Remove from credentials dictionary
        del self.credentials[credential_id]
        
        # Save changes
        if self.auto_save:
            self._save_credentials()
        
        # Log the action
        self._log_credential_action("delete", credential_id)
        
        return True
    
    def list_credentials(self) -> List[Dict[str, Any]]:
        """
        List all credentials (without their values).
        
        Returns:
            List of credential metadata
        """
        result = []
        
        for cred_id, cred_data in self.credentials.items():
            # Create a copy without the actual value
            cred_info = cred_data.copy()
            if "value" in cred_info:
                cred_info["value"] = "********"  # Mask the actual value
            
            # Add the ID
            cred_info["id"] = cred_id
            
            result.append(cred_info)
        
        return result
    
    def _log_credential_action(self, action: str, credential_id: str) -> None:
        """
        Log a credential action for audit purposes.
        
        Args:
            action: Action performed (create, rotate, delete)
            credential_id: Identifier of the credential
        """
        logger.info(f"Credential action: {action} {credential_id} by user {getpass.getuser()} at {datetime.now().isoformat()}")


def get_credential_manager(
    service_name: str = DEFAULT_SERVICE_NAME,
    credentials_file: Optional[str] = None,
    master_password: Optional[str] = None,
    use_keyring: bool = KEYRING_AVAILABLE,
    use_encryption: bool = ENCRYPTION_AVAILABLE
) -> CredentialManager:
    """
    Get a configured credential manager instance.
    
    Args:
        service_name: Name of the service for keyring storage
        credentials_file: Path to the credentials file (if None, uses default)
        master_password: Master password for encryption
        use_keyring: Whether to use system keyring for storage
        use_encryption: Whether to encrypt file-based storage
        
    Returns:
        Configured CredentialManager instance
    """
    # Use default credentials file if not specified
    if credentials_file is None:
        # Check for environment variable
        credentials_file = os.environ.get('URL_ANALYZER_CREDENTIALS_FILE', DEFAULT_CREDENTIALS_FILE)
    
    return CredentialManager(
        service_name=service_name,
        credentials_file=credentials_file,
        master_password=master_password,
        use_keyring=use_keyring,
        use_encryption=use_encryption
    )


def get_api_key(credential_id: str = "gemini_api_key") -> Optional[str]:
    """
    Get an API key from the credential manager or environment variable.
    
    This function first checks for an environment variable with the name
    derived from the credential_id (uppercase). If not found, it tries
    to retrieve the credential from the credential manager.
    
    Args:
        credential_id: Identifier of the API key credential
        
    Returns:
        API key string or None if not found
    """
    # First check environment variable (for backward compatibility)
    env_var_name = credential_id.upper()
    api_key = os.environ.get(env_var_name)
    
    if api_key:
        return api_key
    
    # If not in environment, try credential manager
    try:
        manager = get_credential_manager()
        return manager.get_credential(credential_id)
    except Exception as e:
        logger.error(f"Error retrieving API key: {e}")
        return None


def setup_api_key(
    credential_id: str = "gemini_api_key",
    api_key: Optional[str] = None,
    description: str = "Gemini API Key for content summarization",
    storage: str = "env"
) -> Optional[str]:
    """
    Set up an API key in the credential manager.
    
    Args:
        credential_id: Identifier for the API key
        api_key: API key value (if None, prompts for input)
        description: Description of the API key
        storage: Storage backend to use (env, file, keyring)
        
    Returns:
        The API key value or None if setup failed
    """
    try:
        # Get credential manager
        manager = get_credential_manager()
        
        # Prompt for API key if not provided
        if api_key is None:
            api_key = getpass.getpass(f"Enter {description}: ")
        
        # Store the API key
        manager.set_credential(
            credential_id=credential_id,
            value=api_key,
            description=description,
            storage=storage
        )
        
        return api_key
    except Exception as e:
        logger.error(f"Error setting up API key: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    print("Credential Manager Example")
    print("=========================")
    
    # Create a credential manager
    manager = get_credential_manager()
    
    # Set up an API key
    api_key = setup_api_key()
    
    if api_key:
        print(f"\nAPI key set up successfully!")
    else:
        print(f"\nFailed to set up API key.")
    
    # List credentials
    credentials = manager.list_credentials()
    print(f"\nCredentials ({len(credentials)}):")
    for cred in credentials:
        print(f"- {cred['id']}: {cred['description']} (expires: {cred['expiration']})")