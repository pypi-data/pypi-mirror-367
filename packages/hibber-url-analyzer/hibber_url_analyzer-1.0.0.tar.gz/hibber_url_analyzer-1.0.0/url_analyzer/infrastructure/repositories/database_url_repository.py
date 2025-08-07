"""
Database URL Repository

This module provides a database implementation of the URL repository interface.
It supports storing and retrieving URL data from various database backends.
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
import pandas as pd
import uuid

from url_analyzer.application.interfaces import URLRepository
from url_analyzer.domain.entities import URL
from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseURLRepository(URLRepository):
    """
    Database implementation of the URL repository interface.
    
    This repository stores URL data in a database, supporting various backends
    through a common interface. The default implementation uses SQLite.
    """
    
    def __init__(self, 
                connection_string: str = None, 
                db_type: str = "sqlite",
                table_name: str = "urls",
                version_table_name: str = "url_versions",
                archive_table_name: str = "url_archives",
                compression: bool = False,
                compression_level: int = 6):
        """
        Initialize the database URL repository.
        
        Args:
            connection_string: Database connection string (default: in-memory SQLite)
            db_type: Database type (sqlite, mysql, postgresql)
            table_name: Name of the table to store URLs
            version_table_name: Name of the table to store URL versions
            archive_table_name: Name of the table to store archived URLs
            compression: Whether to compress stored data
            compression_level: Compression level (0-9, higher = more compression)
        """
        self.db_type = db_type.lower()
        self.table_name = table_name
        self.version_table_name = version_table_name
        self.archive_table_name = archive_table_name
        self.compression = compression
        self.compression_level = compression_level
        
        # Set up the database connection
        if self.db_type == "sqlite":
            if connection_string is None:
                connection_string = ":memory:"
            self.connection = sqlite3.connect(connection_string)
            self.connection.row_factory = sqlite3.Row
        elif self.db_type == "mysql":
            try:
                import mysql.connector
                self.connection = mysql.connector.connect(
                    **self._parse_connection_string(connection_string)
                )
            except ImportError:
                logger.error("MySQL support requires mysql-connector-python package")
                raise
        elif self.db_type == "postgresql":
            try:
                import psycopg2
                self.connection = psycopg2.connect(connection_string)
            except ImportError:
                logger.error("PostgreSQL support requires psycopg2 package")
                raise
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Initialize the database schema
        self._initialize_schema()
        
        logger.info(f"Initialized {db_type} URL repository with table {table_name}")
    
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
    
    def _initialize_schema(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        cursor = self.connection.cursor()
        
        # Create the main URL table
        if self.db_type == "sqlite":
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    category TEXT,
                    is_sensitive INTEGER,
                    metadata TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    version INTEGER DEFAULT 1,
                    is_compressed INTEGER DEFAULT 0
                )
            """)
            
            # Create the version history table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.version_table_name} (
                    id TEXT,
                    url_id TEXT,
                    url TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    category TEXT,
                    is_sensitive INTEGER,
                    metadata TEXT,
                    created_at TEXT,
                    version INTEGER,
                    is_compressed INTEGER DEFAULT 0,
                    PRIMARY KEY (url_id, version),
                    FOREIGN KEY (url_id) REFERENCES {self.table_name}(id)
                )
            """)
            
            # Create the archive table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.archive_table_name} (
                    id TEXT PRIMARY KEY,
                    url_id TEXT,
                    url TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    category TEXT,
                    is_sensitive INTEGER,
                    metadata TEXT,
                    created_at TEXT,
                    archived_at TEXT,
                    version INTEGER,
                    is_compressed INTEGER DEFAULT 0,
                    archive_reason TEXT
                )
            """)
            
            # Create indexes
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_domain ON {self.table_name}(domain)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_category ON {self.table_name}(category)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.version_table_name}_url_id ON {self.version_table_name}(url_id)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.archive_table_name}_url_id ON {self.archive_table_name}(url_id)")
        
        elif self.db_type in ["mysql", "postgresql"]:
            # Similar schema creation for MySQL and PostgreSQL
            # Adjust syntax as needed for each database type
            pass
        
        self.connection.commit()
    
    def _compress_data(self, data: str) -> str:
        """
        Compress data using zlib compression.
        
        Args:
            data: Data to compress
            
        Returns:
            Base64-encoded compressed data
        """
        if not self.compression:
            return data
            
        import zlib
        import base64
        
        compressed = zlib.compress(data.encode('utf-8'), self.compression_level)
        return base64.b64encode(compressed).decode('ascii')
    
    def _decompress_data(self, data: str, is_compressed: bool) -> str:
        """
        Decompress data using zlib decompression.
        
        Args:
            data: Compressed data (base64-encoded)
            is_compressed: Whether the data is compressed
            
        Returns:
            Decompressed data
        """
        if not is_compressed:
            return data
            
        import zlib
        import base64
        
        decoded = base64.b64decode(data)
        return zlib.decompress(decoded).decode('utf-8')
    
    def _url_to_row(self, url: URL) -> Dict[str, Any]:
        """
        Convert a URL object to a database row.
        
        Args:
            url: URL object
            
        Returns:
            Dictionary representing a database row
        """
        metadata_json = json.dumps(url.metadata) if url.metadata else "{}"
        
        if self.compression:
            metadata_json = self._compress_data(metadata_json)
        
        return {
            "id": url.id or str(uuid.uuid4()),
            "url": url.url,
            "domain": url.domain,
            "category": url.category,
            "is_sensitive": 1 if url.is_sensitive else 0,
            "metadata": metadata_json,
            "created_at": url.created_at.isoformat() if url.created_at else datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": url.version or 1,
            "is_compressed": 1 if self.compression else 0
        }
    
    def _row_to_url(self, row: Dict[str, Any]) -> URL:
        """
        Convert a database row to a URL object.
        
        Args:
            row: Database row
            
        Returns:
            URL object
        """
        # Handle different row types (sqlite3.Row, dict, etc.)
        if hasattr(row, "keys"):
            # This is a sqlite3.Row or similar
            metadata_json = row["metadata"]
            is_compressed = bool(row["is_compressed"])
        else:
            # This is probably a dict
            metadata_json = row.get("metadata", "{}")
            is_compressed = bool(row.get("is_compressed", False))
        
        # Decompress if necessary
        if metadata_json and is_compressed:
            metadata_json = self._decompress_data(metadata_json, is_compressed)
        
        # Parse metadata
        try:
            metadata = json.loads(metadata_json) if metadata_json else {}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse metadata for URL {row['url']}")
            metadata = {}
        
        # Create URL object
        return URL(
            id=row["id"],
            url=row["url"],
            domain=row["domain"],
            category=row["category"],
            is_sensitive=bool(row["is_sensitive"]),
            metadata=metadata,
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            version=row["version"]
        )
    
    def find_by_id(self, id: str) -> Optional[URL]:
        """
        Find a URL by its ID.
        
        Args:
            id: URL ID
            
        Returns:
            URL object or None if not found
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_url(row)
        return None
    
    def find_by_url(self, url: str) -> Optional[URL]:
        """
        Find a URL by its URL string.
        
        Args:
            url: URL string
            
        Returns:
            URL object or None if not found
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE url = ?", (url,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_url(row)
        return None
    
    def find_all(self) -> List[URL]:
        """
        Find all URLs.
        
        Returns:
            List of URL objects
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = cursor.fetchall()
        
        return [self._row_to_url(row) for row in rows]
    
    def find_by_domain(self, domain: str) -> List[URL]:
        """
        Find URLs by domain.
        
        Args:
            domain: Domain to search for
            
        Returns:
            List of URL objects
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE domain = ?", (domain,))
        rows = cursor.fetchall()
        
        return [self._row_to_url(row) for row in rows]
    
    def find_by_category(self, category: str) -> List[URL]:
        """
        Find URLs by category.
        
        Args:
            category: Category to search for
            
        Returns:
            List of URL objects
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE category = ?", (category,))
        rows = cursor.fetchall()
        
        return [self._row_to_url(row) for row in rows]
    
    def save(self, url: URL) -> URL:
        """
        Save a URL.
        
        If the URL already exists, it will be updated and a new version will be created.
        If the URL doesn't exist, it will be inserted.
        
        Args:
            url: URL to save
            
        Returns:
            Saved URL
        """
        cursor = self.connection.cursor()
        
        # Check if the URL already exists
        existing_url = None
        if url.id:
            existing_url = self.find_by_id(url.id)
        
        if not existing_url and url.url:
            existing_url = self.find_by_url(url.url)
        
        if existing_url:
            # Update the URL and create a new version
            new_version = existing_url.version + 1 if existing_url.version else 1
            
            # Save the current version to the version history
            existing_row = self._url_to_row(existing_url)
            version_id = str(uuid.uuid4())
            
            cursor.execute(
                f"""
                INSERT INTO {self.version_table_name}
                (id, url_id, url, domain, category, is_sensitive, metadata, created_at, version, is_compressed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version_id,
                    existing_url.id,
                    existing_row["url"],
                    existing_row["domain"],
                    existing_row["category"],
                    existing_row["is_sensitive"],
                    existing_row["metadata"],
                    existing_row["created_at"],
                    existing_row["version"],
                    existing_row["is_compressed"]
                )
            )
            
            # Update the URL with the new data
            url.id = existing_url.id
            url.version = new_version
            if not url.created_at:
                url.created_at = existing_url.created_at
            
            row = self._url_to_row(url)
            
            cursor.execute(
                f"""
                UPDATE {self.table_name}
                SET url = ?, domain = ?, category = ?, is_sensitive = ?, 
                    metadata = ?, updated_at = ?, version = ?, is_compressed = ?
                WHERE id = ?
                """,
                (
                    row["url"],
                    row["domain"],
                    row["category"],
                    row["is_sensitive"],
                    row["metadata"],
                    row["updated_at"],
                    row["version"],
                    row["is_compressed"],
                    row["id"]
                )
            )
        else:
            # Insert a new URL
            if not url.id:
                url.id = str(uuid.uuid4())
            if not url.version:
                url.version = 1
            if not url.created_at:
                url.created_at = datetime.now()
            
            row = self._url_to_row(url)
            
            cursor.execute(
                f"""
                INSERT INTO {self.table_name}
                (id, url, domain, category, is_sensitive, metadata, created_at, updated_at, version, is_compressed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    row["url"],
                    row["domain"],
                    row["category"],
                    row["is_sensitive"],
                    row["metadata"],
                    row["created_at"],
                    row["updated_at"],
                    row["version"],
                    row["is_compressed"]
                )
            )
        
        self.connection.commit()
        return self.find_by_id(url.id)
    
    def delete(self, url: URL) -> None:
        """
        Delete a URL.
        
        Args:
            url: URL to delete
        """
        if not url.id:
            return
            
        self.delete_by_id(url.id)
    
    def delete_by_id(self, id: str) -> None:
        """
        Delete a URL by its ID.
        
        Args:
            id: ID of the URL to delete
        """
        cursor = self.connection.cursor()
        
        # Delete versions
        cursor.execute(f"DELETE FROM {self.version_table_name} WHERE url_id = ?", (id,))
        
        # Delete the URL
        cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (id,))
        
        self.connection.commit()
    
    def exists(self, id: str) -> bool:
        """
        Check if a URL exists.
        
        Args:
            id: ID of the URL to check
            
        Returns:
            True if the URL exists, False otherwise
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT 1 FROM {self.table_name} WHERE id = ?", (id,))
        return cursor.fetchone() is not None
    
    def count(self) -> int:
        """
        Count the number of URLs.
        
        Returns:
            Number of URLs
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        return cursor.fetchone()[0]
    
    def get_versions(self, url_id: str) -> List[URL]:
        """
        Get all versions of a URL.
        
        Args:
            url_id: ID of the URL
            
        Returns:
            List of URL versions, ordered by version number
        """
        cursor = self.connection.cursor()
        
        # Get the current version
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (url_id,))
        current_row = cursor.fetchone()
        
        if not current_row:
            return []
        
        # Get all historical versions
        cursor.execute(
            f"SELECT * FROM {self.version_table_name} WHERE url_id = ? ORDER BY version",
            (url_id,)
        )
        version_rows = cursor.fetchall()
        
        # Combine all versions
        versions = [self._row_to_url(row) for row in version_rows]
        versions.append(self._row_to_url(current_row))
        
        return versions
    
    def archive_url(self, url_id: str, reason: str = None) -> bool:
        """
        Archive a URL.
        
        Archiving moves the URL to the archive table and removes it from the main table.
        
        Args:
            url_id: ID of the URL to archive
            reason: Reason for archiving
            
        Returns:
            True if the URL was archived, False otherwise
        """
        cursor = self.connection.cursor()
        
        # Get the URL
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (url_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        # Insert into archive table
        archive_id = str(uuid.uuid4())
        archived_at = datetime.now().isoformat()
        
        cursor.execute(
            f"""
            INSERT INTO {self.archive_table_name}
            (id, url_id, url, domain, category, is_sensitive, metadata, created_at, archived_at, version, is_compressed, archive_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                archive_id,
                row["id"],
                row["url"],
                row["domain"],
                row["category"],
                row["is_sensitive"],
                row["metadata"],
                row["created_at"],
                archived_at,
                row["version"],
                row["is_compressed"],
                reason
            )
        )
        
        # Delete from main table
        cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (url_id,))
        
        # Archive versions
        cursor.execute(
            f"""
            INSERT INTO {self.archive_table_name}
            (id, url_id, url, domain, category, is_sensitive, metadata, created_at, archived_at, version, is_compressed, archive_reason)
            SELECT uuid(), url_id, url, domain, category, is_sensitive, metadata, created_at, ?, version, is_compressed, ?
            FROM {self.version_table_name}
            WHERE url_id = ?
            """,
            (archived_at, reason, url_id)
        )
        
        # Delete versions
        cursor.execute(f"DELETE FROM {self.version_table_name} WHERE url_id = ?", (url_id,))
        
        self.connection.commit()
        return True
    
    def get_archived_urls(self) -> List[URL]:
        """
        Get all archived URLs.
        
        Returns:
            List of archived URL objects
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self.archive_table_name}")
        rows = cursor.fetchall()
        
        return [self._row_to_url(row) for row in rows]
    
    def restore_archived_url(self, archive_id: str) -> Optional[URL]:
        """
        Restore an archived URL.
        
        Args:
            archive_id: ID of the archived URL
            
        Returns:
            Restored URL or None if not found
        """
        cursor = self.connection.cursor()
        
        # Get the archived URL
        cursor.execute(f"SELECT * FROM {self.archive_table_name} WHERE id = ?", (archive_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Check if the original URL ID already exists
        url_id = row["url_id"]
        cursor.execute(f"SELECT 1 FROM {self.table_name} WHERE id = ?", (url_id,))
        if cursor.fetchone():
            # Generate a new ID to avoid conflicts
            url_id = str(uuid.uuid4())
        
        # Insert into main table
        cursor.execute(
            f"""
            INSERT INTO {self.table_name}
            (id, url, domain, category, is_sensitive, metadata, created_at, updated_at, version, is_compressed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                url_id,
                row["url"],
                row["domain"],
                row["category"],
                row["is_sensitive"],
                row["metadata"],
                row["created_at"],
                datetime.now().isoformat(),
                row["version"],
                row["is_compressed"]
            )
        )
        
        # Delete from archive table
        cursor.execute(f"DELETE FROM {self.archive_table_name} WHERE id = ?", (archive_id,))
        
        self.connection.commit()
        return self.find_by_id(url_id)
    
    def backup(self, backup_path: str) -> bool:
        """
        Backup the database.
        
        Args:
            backup_path: Path to save the backup
            
        Returns:
            True if backup was successful, False otherwise
        """
        if self.db_type != "sqlite":
            logger.warning(f"Backup not implemented for {self.db_type}")
            return False
        
        try:
            import shutil
            
            # For SQLite, we can just copy the database file
            if hasattr(self.connection, "isolation_level"):
                # This is a SQLite connection
                db_path = self.connection.execute("PRAGMA database_list").fetchone()[2]
                if db_path != ":memory:":
                    shutil.copy2(db_path, backup_path)
                    return True
            
            # For in-memory databases, we need to dump the data
            self.export_to_file(backup_path)
            return True
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False
    
    def restore(self, backup_path: str) -> bool:
        """
        Restore the database from a backup.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if restore was successful, False otherwise
        """
        if self.db_type != "sqlite":
            logger.warning(f"Restore not implemented for {self.db_type}")
            return False
        
        try:
            # Close the current connection
            self.connection.close()
            
            # For SQLite, we can just replace the database file
            if os.path.exists(backup_path):
                import shutil
                
                # Get the current database path
                db_path = self.connection.execute("PRAGMA database_list").fetchone()[2]
                if db_path != ":memory:":
                    shutil.copy2(backup_path, db_path)
                    
                    # Reopen the connection
                    self.connection = sqlite3.connect(db_path)
                    self.connection.row_factory = sqlite3.Row
                    return True
            
            # For in-memory databases or if the file doesn't exist
            return False
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return False
    
    def export_to_file(self, file_path: str, format: str = "csv") -> bool:
        """
        Export the database to a file.
        
        Args:
            file_path: Path to save the export
            format: Export format (csv, json, excel)
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Get all URLs
            urls = self.find_all()
            
            # Convert to DataFrame
            data = []
            for url in urls:
                row = {
                    "id": url.id,
                    "url": url.url,
                    "domain": url.domain,
                    "category": url.category,
                    "is_sensitive": url.is_sensitive,
                    "metadata": json.dumps(url.metadata),
                    "created_at": url.created_at.isoformat() if url.created_at else None,
                    "version": url.version
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Export to file
            if format.lower() == "csv":
                df.to_csv(file_path, index=False)
            elif format.lower() == "json":
                df.to_json(file_path, orient="records")
            elif format.lower() == "excel":
                df.to_excel(file_path, index=False)
            else:
                logger.warning(f"Unsupported export format: {format}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return False
    
    def import_from_file(self, file_path: str, format: str = "csv") -> bool:
        """
        Import data from a file.
        
        Args:
            file_path: Path to the import file
            format: Import format (csv, json, excel)
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            # Read the file
            if format.lower() == "csv":
                df = pd.read_csv(file_path)
            elif format.lower() == "json":
                df = pd.read_json(file_path, orient="records")
            elif format.lower() == "excel":
                df = pd.read_excel(file_path)
            else:
                logger.warning(f"Unsupported import format: {format}")
                return False
            
            # Import the data
            for _, row in df.iterrows():
                metadata = {}
                if "metadata" in row and row["metadata"]:
                    try:
                        metadata = json.loads(row["metadata"])
                    except json.JSONDecodeError:
                        pass
                
                url = URL(
                    id=row.get("id"),
                    url=row["url"],
                    domain=row["domain"],
                    category=row.get("category"),
                    is_sensitive=bool(row.get("is_sensitive", False)),
                    metadata=metadata,
                    created_at=datetime.fromisoformat(row["created_at"]) if "created_at" in row and row["created_at"] else None,
                    version=row.get("version", 1)
                )
                
                self.save(url)
            
            return True
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Destructor to ensure the connection is closed."""
        self.close()