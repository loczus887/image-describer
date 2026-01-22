#!/usr/bin/env python3
"""
Interactive SQLite query tool
Usage: python query_database.py
"""
import sqlite3
import sys

DB_PATH = "image_describer.db"

def run_query(query):
    """Execute a SQL query and return results"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(query)
        
        # Check if it's a SELECT query
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            # Print results
            if results:
                print("\nResults:")
                print("-" * 80)
                # Print header
                print(" | ".join(columns))
                print("-" * 80)
                # Print rows
                for row in results:
                    print(" | ".join(str(val)[:50] if val else "NULL" for val in row))
                print(f"\nTotal: {len(results)} rows")
            else:
                print("No results found.")
        else:
            conn.commit()
            print("Query executed successfully.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def interactive_mode():
    """Interactive SQL query mode"""
    print("=" * 60)
    print("SQLite Query Tool for Image Describer")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print("\nType SQL queries (or 'exit' to quit, 'help' for examples)")
    print()
    
    while True:
        try:
            query = input("SQL> ").strip()
            
            if not query:
                continue
            
            if query.lower() == 'exit':
                break
            
            if query.lower() == 'help':
                print("\nExample queries:")
                print("  SELECT * FROM descriptions LIMIT 5;")
                print("  SELECT * FROM users;")
                print("  SELECT * FROM preferences;")
                print("  SELECT COUNT(*) FROM descriptions;")
                print("  SELECT description, created_at FROM descriptions ORDER BY created_at DESC LIMIT 10;")
                print()
                continue
            
            run_query(query)
            print()
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run query from command line
        query = " ".join(sys.argv[1:])
        run_query(query)
    else:
        # Interactive mode
        interactive_mode()

