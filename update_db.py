"""
Script to update database schema for the User model
Supports both SQLite and MySQL databases
"""
import os
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlparse

# Try to import PyMySQL, but don't require it if using SQLite
try:
    import pymysql
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

# Get the DEBUG setting from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# Create a SQLite database if needed
def create_sqlite_database():
    """Create a SQLite database file for development"""
    db_path = 'db.sqlite3'
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()
        print(f"Created new SQLite database at {db_path}")
    return f'sqlite:///{db_path}'

# Determine the database URI based on available environment variables
def get_database_uri():
    """Get the database URI from the environment or use SQLite as fallback"""
    db_engine = os.getenv('DB_ENGINE', 'sqlite')
    
    if db_engine == 'sqlite':
        db_name = os.getenv('DB_NAME', 'db.sqlite3')
        return f'sqlite:///{db_name}'
    elif db_engine == 'mysql':
        db_username = os.getenv('DB_USERNAME', 'appseed_db_usr')
        db_password = os.getenv('DB_PASS', 'pass')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME', 'appseed_db')
        return f'mysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    else:
        return create_sqlite_database()

# Get database URI
database_uri = get_database_uri()
print(f"Using database URI: {database_uri}")

# Update SQLite database
def update_sqlite_database(db_path):
    """Add new columns to SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the Users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'")
    if not cursor.fetchone():
        print("Users table doesn't exist. Creating the table.")
        cursor.execute('''
        CREATE TABLE Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(64) UNIQUE,
            email VARCHAR(64) UNIQUE,
            password BLOB,
            oauth_github VARCHAR(100),
            first_name VARCHAR(64),
            last_name VARCHAR(64),
            address VARCHAR(128),
            city VARCHAR(64),
            country VARCHAR(64),
            postal_code VARCHAR(16),
            about_me TEXT,
            position VARCHAR(64) DEFAULT 'Member',
            profile_image VARCHAR(128) DEFAULT 'img/default-avatar.png'
        )
        ''')
        conn.commit()
        print("Created Users table with all required columns")
        conn.close()
        return
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(Users)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"Existing columns: {columns}")
    
    # Columns to add
    new_columns = [
        ("first_name", "VARCHAR(64)"),
        ("last_name", "VARCHAR(64)"),
        ("address", "VARCHAR(128)"),
        ("city", "VARCHAR(64)"),
        ("country", "VARCHAR(64)"),
        ("postal_code", "VARCHAR(16)"),
        ("about_me", "TEXT"),
        ("position", "VARCHAR(64) DEFAULT 'Member'"),
        ("profile_image", "VARCHAR(128) DEFAULT 'img/default-avatar.png'")
    ]
    
    # Add each column if it doesn't exist
    for column_name, column_type in new_columns:
        if column_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE Users ADD COLUMN {column_name} {column_type}")
                print(f"Added column {column_name} to Users table")
            except sqlite3.OperationalError as e:
                print(f"Error adding {column_name}: {e}")
    
    # Commit the changes
    conn.commit()
    conn.close()
    print("SQLite database update completed.")

# Update MySQL database
def update_mysql_database(uri):
    """Add new columns to MySQL database"""
    if not HAS_PYMYSQL:
        print("PyMySQL is not installed. Cannot update MySQL database.")
        print("Install it with: pip install pymysql")
        return
    
    # Parse the database URI
    # mysql://username:password@host:port/dbname
    parsed_uri = urlparse(uri)
    username = parsed_uri.username
    password = parsed_uri.password
    hostname = parsed_uri.hostname
    port = parsed_uri.port or 3306
    database = parsed_uri.path.lstrip('/')
    
    try:
        # Connect to the MySQL database
        conn = pymysql.connect(
            host=hostname,
            user=username,
            password=password,
            database=database,
            port=port
        )
        
        print(f"Connected to MySQL database: {database} on {hostname}:{port}")
        
        cursor = conn.cursor()
        
        # Check if the Users table exists
        cursor.execute("SHOW TABLES LIKE 'Users'")
        if not cursor.fetchone():
            print("Users table doesn't exist. Creating the table.")
            cursor.execute('''
            CREATE TABLE Users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(64) UNIQUE,
                email VARCHAR(64) UNIQUE,
                password BLOB,
                oauth_github VARCHAR(100),
                first_name VARCHAR(64),
                last_name VARCHAR(64),
                address VARCHAR(128),
                city VARCHAR(64),
                country VARCHAR(64),
                postal_code VARCHAR(16),
                about_me TEXT,
                position VARCHAR(64) DEFAULT 'Member',
                profile_image VARCHAR(128) DEFAULT 'img/default-avatar.png'
            )
            ''')
            conn.commit()
            print("Created Users table with all required columns")
            conn.close()
            return
        
        # Check if columns exist in the Users table
        cursor.execute("SHOW COLUMNS FROM Users")
        existing_columns = [column[0] for column in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Columns to add
        new_columns = [
            ("first_name", "VARCHAR(64)"),
            ("last_name", "VARCHAR(64)"),
            ("address", "VARCHAR(128)"),
            ("city", "VARCHAR(64)"),
            ("country", "VARCHAR(64)"),
            ("postal_code", "VARCHAR(16)"),
            ("about_me", "TEXT"),
            ("position", "VARCHAR(64) DEFAULT 'Member'"),
            ("profile_image", "VARCHAR(128) DEFAULT 'img/default-avatar.png'")
        ]
        
        # Add each column if it doesn't exist
        for column_name, column_definition in new_columns:
            if column_name.lower() not in [col.lower() for col in existing_columns]:
                try:
                    alter_query = f"ALTER TABLE Users ADD COLUMN {column_name} {column_definition}"
                    print(f"Executing: {alter_query}")
                    cursor.execute(alter_query)
                    print(f"Added column {column_name} to Users table")
                except Exception as e:
                    print(f"Error adding {column_name}: {e}")
        
        # Commit the changes
        conn.commit()
        conn.close()
        print("MySQL database update completed successfully")
        
    except Exception as e:
        print(f"Database connection error: {e}")

# Main execution
if database_uri.startswith('sqlite:///'):
    db_path = database_uri.replace('sqlite:///', '')
    print(f"Using SQLite database at: {db_path}")
    update_sqlite_database(db_path)
elif database_uri.startswith('mysql://'):
    print("Using MySQL database")
    update_mysql_database(database_uri)
else:
    print(f"Unsupported database type: {database_uri}")

print("Script execution completed.") 