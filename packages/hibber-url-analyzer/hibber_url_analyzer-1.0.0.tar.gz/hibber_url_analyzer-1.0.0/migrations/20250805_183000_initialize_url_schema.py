"""
Migration 20250805_183000: Initialize URL schema

This migration creates the initial database schema for storing URLs.
"""

from url_analyzer.infrastructure.migrations.migration_manager import SQLiteMigration


class Migration_20250805_183000(SQLiteMigration):
    """
    Initialize URL schema
    
    This migration creates the initial tables for storing URLs, including
    the main URL table, version history table, and archive table.
    """
    
    def __init__(self):
        super().__init__("20250805_183000", "Initialize URL schema")
    
    def up(self, connection):
        """
        Apply the migration.
        
        Args:
            connection: Database connection
        """
        cursor = connection.cursor()
        
        # Create the main URL table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS url_versions (
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
                FOREIGN KEY (url_id) REFERENCES urls(id)
            )
        """)
        
        # Create the archive table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS url_archives (
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urls_domain ON urls(domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urls_category ON urls(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_url_versions_url_id ON url_versions(url_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_url_archives_url_id ON url_archives(url_id)")
        
        connection.commit()
    
    def down(self, connection):
        """
        Roll back the migration.
        
        Args:
            connection: Database connection
        """
        cursor = connection.cursor()
        
        # Drop indexes
        cursor.execute("DROP INDEX IF EXISTS idx_urls_domain")
        cursor.execute("DROP INDEX IF EXISTS idx_urls_category")
        cursor.execute("DROP INDEX IF EXISTS idx_url_versions_url_id")
        cursor.execute("DROP INDEX IF EXISTS idx_url_archives_url_id")
        
        # Drop tables
        cursor.execute("DROP TABLE IF EXISTS url_archives")
        cursor.execute("DROP TABLE IF EXISTS url_versions")
        cursor.execute("DROP TABLE IF EXISTS urls")
        
        connection.commit()