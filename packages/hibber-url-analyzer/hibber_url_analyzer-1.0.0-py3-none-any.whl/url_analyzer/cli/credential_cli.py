"""
Command-Line Interface for Credential Management

This module provides a command-line interface for managing credentials
such as API keys, with support for different storage backends.
"""

import os
import sys
import argparse
import getpass
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from url_analyzer.utils.logging import get_logger, setup_logging
from url_analyzer.utils.credentials import (
    get_credential_manager, get_api_key, setup_api_key,
    KEYRING_AVAILABLE, ENCRYPTION_AVAILABLE
)

# Create logger
logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="URL Analyzer Credential Manager - Securely manage API keys and other credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set up a new API key
  python -m url_analyzer.cli.credential_cli set --id gemini_api_key --description "Gemini API Key"
  
  # Get an API key
  python -m url_analyzer.cli.credential_cli get --id gemini_api_key
  
  # List all credentials
  python -m url_analyzer.cli.credential_cli list
  
  # Rotate an API key
  python -m url_analyzer.cli.credential_cli rotate --id gemini_api_key
  
  # Delete a credential
  python -m url_analyzer.cli.credential_cli delete --id gemini_api_key
"""
    )
    
    # Add global options
    parser.add_argument('--verbose', '-v', action='count', default=0,
                       help="Increase verbosity (can be used multiple times)")
    parser.add_argument('--quiet', '-q', action='store_true',
                       help="Suppress non-error output")
    parser.add_argument('--credentials-file',
                       help="Path to credentials file (default: credentials.json)")
    parser.add_argument('--no-keyring', action='store_true',
                       help="Disable system keyring storage")
    parser.add_argument('--no-encryption', action='store_true',
                       help="Disable encryption for file-based storage")
    parser.add_argument('--master-password',
                       help="Master password for encryption (if not provided, will prompt if needed)")
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set a credential')
    set_parser.add_argument('--id', required=True,
                          help="Unique identifier for the credential")
    set_parser.add_argument('--value',
                          help="Value of the credential (if not provided, will prompt)")
    set_parser.add_argument('--description',
                          help="Description of the credential")
    set_parser.add_argument('--storage', choices=['file', 'keyring', 'env'], default='env',
                          help="Storage backend to use (default: env)")
    set_parser.add_argument('--expiration', type=int, default=90,
                          help="Number of days until the credential expires (default: 90)")
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a credential')
    get_parser.add_argument('--id', required=True,
                          help="Unique identifier for the credential")
    get_parser.add_argument('--show', action='store_true',
                          help="Show the credential value (otherwise masked)")
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all credentials')
    list_parser.add_argument('--show-expired', action='store_true',
                           help="Include expired credentials in the list")
    list_parser.add_argument('--format', choices=['table', 'json'], default='table',
                           help="Output format (default: table)")
    
    # Rotate command
    rotate_parser = subparsers.add_parser('rotate', help='Rotate a credential')
    rotate_parser.add_argument('--id', required=True,
                             help="Unique identifier for the credential")
    rotate_parser.add_argument('--value',
                             help="New value for the credential (if not provided, will generate one)")
    rotate_parser.add_argument('--expiration', type=int, default=90,
                             help="Number of days until the credential expires (default: 90)")
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a credential')
    delete_parser.add_argument('--id', required=True,
                             help="Unique identifier for the credential")
    delete_parser.add_argument('--force', action='store_true',
                             help="Force deletion without confirmation")
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up common credentials')
    setup_parser.add_argument('--gemini-api-key',
                            help="Gemini API key for content summarization")
    setup_parser.add_argument('--storage', choices=['file', 'keyring', 'env'], default='env',
                            help="Storage backend to use (default: env)")
    
    return parser


def handle_set_command(args: argparse.Namespace, manager) -> int:
    """
    Handle the 'set' command.
    
    Args:
        args: Command-line arguments
        manager: Credential manager instance
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Setting credential '{args.id}'")
    
    try:
        # Get value if not provided
        value = args.value
        if value is None:
            value = getpass.getpass(f"Enter value for credential '{args.id}': ")
        
        # Set the credential
        manager.set_credential(
            credential_id=args.id,
            value=value,
            description=args.description or f"Credential '{args.id}'",
            expiration_days=args.expiration,
            storage=args.storage
        )
        
        print(f"✅ Credential '{args.id}' set successfully")
        return 0
    except Exception as e:
        logger.exception(f"Error setting credential: {e}")
        print(f"❌ Error setting credential: {e}")
        return 1


def handle_get_command(args: argparse.Namespace, manager) -> int:
    """
    Handle the 'get' command.
    
    Args:
        args: Command-line arguments
        manager: Credential manager instance
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Getting credential '{args.id}'")
    
    try:
        # Get the credential
        value = manager.get_credential(args.id)
        
        if value is None:
            print(f"❌ Credential '{args.id}' not found")
            return 1
        
        # Get credential metadata
        creds = manager.list_credentials()
        cred_info = next((c for c in creds if c["id"] == args.id), None)
        
        if cred_info:
            print(f"\nCredential: {args.id}")
            print(f"Description: {cred_info.get('description', 'N/A')}")
            print(f"Storage: {cred_info.get('storage', 'N/A')}")
            print(f"Created: {cred_info.get('created', 'N/A')}")
            print(f"Expires: {cred_info.get('expiration', 'N/A')}")
            print(f"Status: {cred_info.get('status', 'active')}")
            
            if args.show:
                print(f"Value: {value}")
            else:
                masked_value = value[:4] + "*" * (len(value) - 4) if len(value) > 4 else "****"
                print(f"Value: {masked_value} (use --show to reveal)")
        else:
            if args.show:
                print(f"Value: {value}")
            else:
                masked_value = value[:4] + "*" * (len(value) - 4) if len(value) > 4 else "****"
                print(f"Value: {masked_value} (use --show to reveal)")
        
        return 0
    except Exception as e:
        logger.exception(f"Error getting credential: {e}")
        print(f"❌ Error getting credential: {e}")
        return 1


def handle_list_command(args: argparse.Namespace, manager) -> int:
    """
    Handle the 'list' command.
    
    Args:
        args: Command-line arguments
        manager: Credential manager instance
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info("Listing credentials")
    
    try:
        # Get all credentials
        credentials = manager.list_credentials()
        
        # Filter out expired credentials if not requested
        if not args.show_expired:
            credentials = [c for c in credentials if c.get("status") != "expired"]
        
        if not credentials:
            print("No credentials found")
            return 0
        
        # Output in requested format
        if args.format == "json":
            import json
            print(json.dumps(credentials, indent=2))
        else:
            # Table format
            print(f"\nCredentials ({len(credentials)}):\n")
            
            # Calculate column widths
            id_width = max(len("ID"), max(len(c["id"]) for c in credentials))
            desc_width = max(len("Description"), max(len(c.get("description", "")) for c in credentials))
            storage_width = max(len("Storage"), max(len(c.get("storage", "")) for c in credentials))
            status_width = max(len("Status"), max(len(c.get("status", "")) for c in credentials))
            
            # Print header
            print(f"{'ID':{id_width}} | {'Description':{desc_width}} | {'Storage':{storage_width}} | {'Status':{status_width}} | Expiration")
            print(f"{'-' * id_width}-+-{'-' * desc_width}-+-{'-' * storage_width}-+-{'-' * status_width}-+-{'-' * 20}")
            
            # Print rows
            for cred in sorted(credentials, key=lambda c: c["id"]):
                print(f"{cred['id']:{id_width}} | {cred.get('description', ''):{desc_width}} | {cred.get('storage', ''):{storage_width}} | {cred.get('status', 'active'):{status_width}} | {cred.get('expiration', 'N/A')}")
        
        return 0
    except Exception as e:
        logger.exception(f"Error listing credentials: {e}")
        print(f"❌ Error listing credentials: {e}")
        return 1


def handle_rotate_command(args: argparse.Namespace, manager) -> int:
    """
    Handle the 'rotate' command.
    
    Args:
        args: Command-line arguments
        manager: Credential manager instance
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Rotating credential '{args.id}'")
    
    try:
        # Get new value if provided
        new_value = args.value
        
        # Rotate the credential
        result = manager.rotate_credential(
            credential_id=args.id,
            new_value=new_value,
            expiration_days=args.expiration
        )
        
        if result is None:
            print(f"❌ Failed to rotate credential '{args.id}'")
            return 1
        
        print(f"✅ Credential '{args.id}' rotated successfully")
        
        # Get credential metadata
        creds = manager.list_credentials()
        cred_info = next((c for c in creds if c["id"] == args.id), None)
        
        if cred_info:
            print(f"\nNew expiration: {cred_info.get('expiration', 'N/A')}")
            
            # If storage is env, show instructions
            if cred_info.get("storage") == "env":
                env_var = cred_info.get("env_var", args.id.upper())
                print(f"\nRemember to update your environment variable:")
                print(f"export {env_var}='{result}'")
        
        return 0
    except Exception as e:
        logger.exception(f"Error rotating credential: {e}")
        print(f"❌ Error rotating credential: {e}")
        return 1


def handle_delete_command(args: argparse.Namespace, manager) -> int:
    """
    Handle the 'delete' command.
    
    Args:
        args: Command-line arguments
        manager: Credential manager instance
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Deleting credential '{args.id}'")
    
    try:
        # Confirm deletion if not forced
        if not args.force:
            confirm = input(f"Are you sure you want to delete credential '{args.id}'? (y/N): ")
            if confirm.lower() != "y":
                print("Deletion cancelled")
                return 0
        
        # Delete the credential
        result = manager.delete_credential(args.id)
        
        if not result:
            print(f"❌ Failed to delete credential '{args.id}'")
            return 1
        
        print(f"✅ Credential '{args.id}' deleted successfully")
        return 0
    except Exception as e:
        logger.exception(f"Error deleting credential: {e}")
        print(f"❌ Error deleting credential: {e}")
        return 1


def handle_setup_command(args: argparse.Namespace, manager) -> int:
    """
    Handle the 'setup' command.
    
    Args:
        args: Command-line arguments
        manager: Credential manager instance
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info("Setting up common credentials")
    
    try:
        # Set up Gemini API key
        if args.gemini_api_key is not None or input("Set up Gemini API key? (y/N): ").lower() == "y":
            api_key = args.gemini_api_key
            if api_key is None:
                api_key = getpass.getpass("Enter Gemini API key: ")
            
            manager.set_credential(
                credential_id="gemini_api_key",
                value=api_key,
                description="Gemini API Key for content summarization",
                storage=args.storage
            )
            
            print(f"✅ Gemini API key set up successfully")
        
        print("\nCredential setup complete")
        return 0
    except Exception as e:
        logger.exception(f"Error setting up credentials: {e}")
        print(f"❌ Error setting up credentials: {e}")
        return 1


def main() -> int:
    """
    Main entry point for the command-line interface.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Create parser and parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging based on verbosity
    if args.quiet:
        log_level = "ERROR"
    elif args.verbose == 0:
        log_level = "INFO"
    elif args.verbose == 1:
        log_level = "DEBUG"
    else:
        log_level = "DEBUG"  # More detailed debug for verbosity > 1
    
    setup_logging(log_level=log_level, console=not args.quiet)
    
    # Create credential manager
    try:
        manager = get_credential_manager(
            credentials_file=args.credentials_file,
            master_password=args.master_password,
            use_keyring=not args.no_keyring and KEYRING_AVAILABLE,
            use_encryption=not args.no_encryption and ENCRYPTION_AVAILABLE
        )
    except Exception as e:
        logger.exception(f"Error creating credential manager: {e}")
        print(f"❌ Error creating credential manager: {e}")
        return 1
    
    # Handle commands
    if args.command == 'set':
        return handle_set_command(args, manager)
    elif args.command == 'get':
        return handle_get_command(args, manager)
    elif args.command == 'list':
        return handle_list_command(args, manager)
    elif args.command == 'rotate':
        return handle_rotate_command(args, manager)
    elif args.command == 'delete':
        return handle_delete_command(args, manager)
    elif args.command == 'setup':
        return handle_setup_command(args, manager)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())