#!/usr/bin/env python3
"""
Simple script to view SQLite database contents
"""
import sqlite3
import sys
from datetime import datetime

DB_PATH = "image_describer.db"

def view_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("Image Describer Database Viewer")
        print("=" * 60)
        print()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in database.")
            return
        
        print(f"Tables found: {len(tables)}")
        print()
        
        # View each table
        for table_name, in tables:
            print(f"\n{'=' * 60}")
            print(f"Table: {table_name}")
            print('=' * 60)
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nTotal rows: {count}")
            
            if count > 0:
                # Get all data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                print("\nData:")
                for i, row in enumerate(rows, 1):
                    print(f"\n  Row {i}:")
                    for col, val in zip(columns, row):
                        if isinstance(val, str) and len(val) > 100:
                            print(f"    {col[1]}: {val[:100]}... (truncated)")
                        else:
                            print(f"    {col[1]}: {val}")
        
        conn.close()
        print("\n" + "=" * 60)
        print("Database view complete")
        print("=" * 60)
        
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        print(f"\nDatabase file: {DB_PATH}")
        print("Make sure the database exists and backend has been run at least once.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_database()

