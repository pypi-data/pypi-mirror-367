"""
Migration Manager

This module provides tools for managing database schema migrations.
It supports creating, applying, and rolling back migrations for different database types.
"""

import os
import json
import sqlite3
import importlib.util
import inspect
import re
import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from abc import ABC, abstractmethod

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


class Migration(ABC):
    """
    Base class for database migrations.
    
    Migrations define the changes to be applied to a database schema.
    Each migration should implement the up and down methods to apply
    and roll back the changes.
    """
    
    @property
    @abstractmethod
    def version(self) -> str:
        """
        Get the version of this migration.
        
        Returns:
            String version in the format YYYYMMDD_HHMMSS
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Get a description of this migration.
        
        Returns:
            String description of the migration
        """
        pass
    
    @abstractmethod
    def up(self, connection: Any) -> None:
        """
        Apply the migration.
        
        Args:
            connection: Database connection
        """
        pass
    
    @abstractmethod
    def down(self, connection: Any) -> None:
        """
        Roll back the migration.
        
        Args:
            connection: Database connection
        """
        pass


class SQLiteMigration(Migration):
    """Base class for SQLite migrations."""
    
    def __init__(self, version: str, description: str):
        """
        Initialize the migration.
        
        Args:
            version: Migration version
            description: Migration description
        """
        self._version = version
        self._description = description
    
    @property
    def version(self) -> str:
        """Get the version of this migration."""
        return self._version
    
    @property
    def description(self) -> str:
        """Get a description of this migration."""
        return self._description


class MigrationManager:
    """
    Manager for database migrations.
    
    This class provides methods for creating, applying, and rolling back
    migrations for different database types.
    """
    
    def __init__(self, 
                db_type: str = "sqlite",
                connection_string: Optional[str] = None,
                migrations_dir: str = "migrations",
                auto_migrate: bool = False):
        """
        Initialize the migration manager.
        
        Args:
            db_type: Database type (sqlite, mysql, postgresql)
            connection_string: Database connection string
            migrations_dir: Directory containing migration files
            auto_migrate: Whether to automatically apply pending migrations
        """
        self.db_type = db_type.lower()
        self.connection_string = connection_string
        self.migrations_dir = migrations_dir
        self.auto_migrate = auto_migrate
        
        # Set up the database connection
        self.connection = self._create_connection()
        
        # Create the migrations table if it doesn't exist
        self._initialize_migrations_table()
        
        # Apply pending migrations if auto_migrate is enabled
        if self.auto_migrate:
            self.apply_pending_migrations()
    
    def _create_connection(self) -> Any:
        """
        Create a database connection.
        
        Returns:
            Database connection
        """
        if self.db_type == "sqlite":
            if self.connection_string is None:
                self.connection_string = ":memory:"
            connection = sqlite3.connect(self.connection_string)
            connection.row_factory = sqlite3.Row
            return connection
        elif self.db_type == "mysql":
            try:
                import mysql.connector
                return mysql.connector.connect(
                    **self._parse_connection_string(self.connection_string)
                )
            except ImportError:
                logger.error("MySQL support requires mysql-connector-python package")
                raise
        elif self.db_type == "postgresql":
            try:
                import psycopg2
                return psycopg2.connect(self.connection_string)
            except ImportError:
                logger.error("PostgreSQL support requires psycopg2 package")
                raise
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _parse_connection_string(self, connection_string: str) -> Dict[str, str]:
        """
        Parse a connection string into a dictionary of connection parameters.
        
        Args:
            connection_string: Connection string in format "key1=value1;key2=value2"
            
        Returns:
            Dictionary of connection parameters
        """
        if not connection_string:
            return {}
            
        params = {}
        for param in connection_string.split(';'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip()] = value.strip()
        return params
    
    def _initialize_migrations_table(self) -> None:
        """Initialize the migrations table if it doesn't exist."""
        cursor = self.connection.cursor()
        
        if self.db_type == "sqlite":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    version TEXT PRIMARY KEY,
                    description TEXT,
                    applied_at TEXT
                )
            """)
        elif self.db_type in ["mysql", "postgresql"]:
            # Similar schema creation for MySQL and PostgreSQL
            # Adjust syntax as needed for each database type
            pass
        
        self.connection.commit()
    
    def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """
        Get a list of applied migrations.
        
        Returns:
            List of dictionaries containing migration information
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT version, description, applied_at FROM migrations ORDER BY version")
        
        result = []
        for row in cursor.fetchall():
            result.append({
                "version": row["version"],
                "description": row["description"],
                "applied_at": row["applied_at"]
            })
        
        return result
    
    def get_pending_migrations(self) -> List[Migration]:
        """
        Get a list of pending migrations.
        
        Returns:
            List of Migration objects
        """
        # Get applied migrations
        applied_versions = set(m["version"] for m in self.get_applied_migrations())
        
        # Get available migrations
        available_migrations = self._load_migrations()
        
        # Filter out applied migrations
        pending_migrations = [m for m in available_migrations if m.version not in applied_versions]
        
        # Sort by version
        pending_migrations.sort(key=lambda m: m.version)
        
        return pending_migrations
    
    def _load_migrations(self) -> List[Migration]:
        """
        Load migration classes from the migrations directory.
        
        Returns:
            List of Migration objects
        """
        migrations = []
        
        # Create migrations directory if it doesn't exist
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Find migration files
        for filename in os.listdir(self.migrations_dir):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue
            
            # Load the module
            module_path = os.path.join(self.migrations_dir, filename)
            module_name = os.path.splitext(filename)[0]
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None or spec.loader is None:
                    logger.warning(f"Failed to load migration module: {module_path}")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find migration classes
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and issubclass(obj, Migration) and 
                            obj is not Migration and obj is not SQLiteMigration):
                        try:
                            migration = obj()
                            migrations.append(migration)
                        except Exception as e:
                            logger.error(f"Failed to instantiate migration {name}: {str(e)}")
            except Exception as e:
                logger.error(f"Failed to load migration file {filename}: {str(e)}")
        
        return migrations
    
    def apply_migration(self, migration: Migration) -> bool:
        """
        Apply a single migration.
        
        Args:
            migration: Migration to apply
            
        Returns:
            True if the migration was applied successfully, False otherwise
        """
        logger.info(f"Applying migration {migration.version}: {migration.description}")
        
        try:
            # Apply the migration
            migration.up(self.connection)
            
            # Record the migration
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO migrations (version, description, applied_at) VALUES (?, ?, ?)",
                (migration.version, migration.description, datetime.datetime.now().isoformat())
            )
            
            self.connection.commit()
            logger.info(f"Migration {migration.version} applied successfully")
            return True
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to apply migration {migration.version}: {str(e)}")
            return False
    
    def rollback_migration(self, migration: Migration) -> bool:
        """
        Roll back a single migration.
        
        Args:
            migration: Migration to roll back
            
        Returns:
            True if the migration was rolled back successfully, False otherwise
        """
        logger.info(f"Rolling back migration {migration.version}: {migration.description}")
        
        try:
            # Roll back the migration
            migration.down(self.connection)
            
            # Remove the migration record
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM migrations WHERE version = ?", (migration.version,))
            
            self.connection.commit()
            logger.info(f"Migration {migration.version} rolled back successfully")
            return True
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to roll back migration {migration.version}: {str(e)}")
            return False
    
    def apply_pending_migrations(self) -> bool:
        """
        Apply all pending migrations.
        
        Returns:
            True if all migrations were applied successfully, False otherwise
        """
        pending_migrations = self.get_pending_migrations()
        
        if not pending_migrations:
            logger.info("No pending migrations to apply")
            return True
        
        logger.info(f"Applying {len(pending_migrations)} pending migrations")
        
        success = True
        for migration in pending_migrations:
            if not self.apply_migration(migration):
                success = False
                break
        
        return success
    
    def rollback_last_migration(self) -> bool:
        """
        Roll back the last applied migration.
        
        Returns:
            True if the migration was rolled back successfully, False otherwise
        """
        applied_migrations = self.get_applied_migrations()
        
        if not applied_migrations:
            logger.info("No migrations to roll back")
            return True
        
        # Get the last applied migration
        last_migration = applied_migrations[-1]
        
        # Find the migration class
        migrations = self._load_migrations()
        migration = next((m for m in migrations if m.version == last_migration["version"]), None)
        
        if migration is None:
            logger.error(f"Migration {last_migration['version']} not found")
            return False
        
        return self.rollback_migration(migration)
    
    def rollback_to_version(self, version: str) -> bool:
        """
        Roll back migrations to a specific version.
        
        Args:
            version: Target version
            
        Returns:
            True if all migrations were rolled back successfully, False otherwise
        """
        applied_migrations = self.get_applied_migrations()
        
        if not applied_migrations:
            logger.info("No migrations to roll back")
            return True
        
        # Find migrations to roll back
        migrations_to_rollback = []
        for applied in reversed(applied_migrations):
            if applied["version"] <= version:
                break
            migrations_to_rollback.append(applied)
        
        if not migrations_to_rollback:
            logger.info(f"No migrations to roll back to version {version}")
            return True
        
        logger.info(f"Rolling back {len(migrations_to_rollback)} migrations to version {version}")
        
        # Find migration classes
        available_migrations = self._load_migrations()
        
        success = True
        for applied in migrations_to_rollback:
            migration = next((m for m in available_migrations if m.version == applied["version"]), None)
            
            if migration is None:
                logger.error(f"Migration {applied['version']} not found")
                success = False
                break
            
            if not self.rollback_migration(migration):
                success = False
                break
        
        return success
    
    def create_migration(self, description: str) -> str:
        """
        Create a new migration file.
        
        Args:
            description: Description of the migration
            
        Returns:
            Path to the created migration file
        """
        # Create migrations directory if it doesn't exist
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Generate version
        version = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate filename
        filename = f"{version}_{self._slugify(description)}.py"
        file_path = os.path.join(self.migrations_dir, filename)
        
        # Create migration file
        with open(file_path, "w") as f:
            f.write(self._generate_migration_template(version, description))
        
        logger.info(f"Created migration file: {file_path}")
        return file_path
    
    def _slugify(self, text: str) -> str:
        """
        Convert text to a slug.
        
        Args:
            text: Text to convert
            
        Returns:
            Slug version of the text
        """
        # Replace non-alphanumeric characters with underscores
        slug = re.sub(r'[^a-zA-Z0-9]', '_', text.lower())
        # Replace multiple underscores with a single underscore
        slug = re.sub(r'_+', '_', slug)
        # Remove leading and trailing underscores
        slug = slug.strip('_')
        return slug
    
    def _generate_migration_template(self, version: str, description: str) -> str:
        """
        Generate a migration file template.
        
        Args:
            version: Migration version
            description: Migration description
            
        Returns:
            Migration file content
        """
        if self.db_type == "sqlite":
            return f'''"""
Migration {version}: {description}
"""

from url_analyzer.infrastructure.migrations.migration_manager import SQLiteMigration


class Migration_{version}(SQLiteMigration):
    """
    {description}
    """
    
    def __init__(self):
        super().__init__("{version}", "{description}")
    
    def up(self, connection):
        """
        Apply the migration.
        
        Args:
            connection: Database connection
        """
        cursor = connection.cursor()
        
        # TODO: Implement migration
        # Example:
        # cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS my_table (
        #         id TEXT PRIMARY KEY,
        #         name TEXT NOT NULL
        #     )
        # """)
        
        connection.commit()
    
    def down(self, connection):
        """
        Roll back the migration.
        
        Args:
            connection: Database connection
        """
        cursor = connection.cursor()
        
        # TODO: Implement rollback
        # Example:
        # cursor.execute("DROP TABLE IF EXISTS my_table")
        
        connection.commit()
'''
        elif self.db_type == "mysql":
            # MySQL migration template
            pass
        elif self.db_type == "postgresql":
            # PostgreSQL migration template
            pass
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Destructor to ensure the connection is closed."""
        self.close()