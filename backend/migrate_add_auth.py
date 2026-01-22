"""
Migration script to add authentication fields to existing database
Run this before starting the updated application if you have existing data
"""

import sqlite3
from pathlib import Path

def migrate_database():
    db_path = Path("image_describer.db")

    if not db_path.exists():
        print("Database doesn't exist yet. Will be created with new schema.")
        return

    print("Migrating existing database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if password_hash column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'password_hash' not in columns:
            print("Adding password_hash column...")
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")

        if 'role' not in columns:
            print("Adding role column...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")

        if 'is_active' not in columns:
            print("Adding is_active column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")

        # Update existing users
        cursor.execute("SELECT COUNT(*) FROM users WHERE password_hash IS NULL")
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            print(f"Warning: {null_count} users don't have passwords.")
            print("These users will need to register new accounts or use password reset.")

        conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
