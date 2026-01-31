"""
Database Migration Script: Add username column to batches table

This script adds a username column to the existing batches table.
For SQLite, we need to handle this carefully since ALTER TABLE has limitations.

Usage:
    python migration_add_username.py

Note: This script will:
1. Check if username column already exists
2. Add the column if it doesn't exist
3. Set default username 'unknown' for existing batches
4. Since SQLite doesn't support adding NOT NULL directly, the column will be nullable
   but the application will enforce NOT NULL for new batches
"""

import sqlite3
import os
from pathlib import Path


def migrate_add_username(db_path: str = "./mushroom_farming.db"):
    """
    Migrate the batches table to add username column.
    
    Args:
        db_path: Path to the SQLite database file
    """
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Skipping migration.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(batches)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'username' in columns:
            print("[OK] Username column already exists. Migration not needed.")
            return
        
        print("Starting migration: Adding username column to batches table...")
        
        # Add username column (nullable for existing rows)
        cursor.execute("ALTER TABLE batches ADD COLUMN username TEXT")
        print("[OK] Added username column")
        
        # Set default username for existing batches
        cursor.execute("UPDATE batches SET username = 'unknown' WHERE username IS NULL")
        updated_count = cursor.rowcount
        print(f"[OK] Updated {updated_count} existing batch(es) with default username 'unknown'")
        
        conn.commit()
        print("[OK] Migration completed successfully!")
        print("\nNote: The username column is nullable in the database.")
        print("The application will enforce NOT NULL for new batches.")
        print("You may want to update existing batches with actual usernames.")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Unexpected error during migration: {e}")
        raise
    finally:
        conn.close()


def verify_migration(db_path: str = "./mushroom_farming.db"):
    """
    Verify that the migration was successful.
    
    Args:
        db_path: Path to the SQLite database file
    """
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found.")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(batches)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'username' in columns:
            # Check for null usernames
            cursor.execute("SELECT COUNT(*) FROM batches WHERE username IS NULL")
            null_count = cursor.fetchone()[0]
            
            if null_count > 0:
                print(f"[WARNING] {null_count} batch(es) still have NULL username")
            else:
                print("[OK] All batches have a username assigned")
            
            return True
        else:
            print("[ERROR] Username column not found")
            return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add Username Column")
    print("=" * 60)
    print()
    
    # Run migration
    migrate_add_username()
    
    print()
    print("=" * 60)
    print("Verifying migration...")
    print("=" * 60)
    verify_migration()
    
    print()
    print("Migration script completed!")

