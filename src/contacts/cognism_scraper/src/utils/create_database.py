import sqlite3
import os

# Dynamically determine the database path
def get_db_path():
    """Gets the absolute path to the database."""
    # Get project root using relative path from this file
    current_file = os.path.abspath(__file__)
    utils_dir = os.path.dirname(current_file)
    src_dir = os.path.dirname(utils_dir)
    cognism_dir = os.path.dirname(src_dir)
    contacts_dir = os.path.dirname(cognism_dir)
    src_parent = os.path.dirname(contacts_dir)
    project_root = os.path.dirname(src_parent)
    
    # First try the project root path
    db_path = os.path.join(project_root, 'databases', 'database.db')
    db_dir = os.path.dirname(db_path)
    
    # Ensure database directory exists
    try:
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created database directory: {db_dir}")
            except Exception as e:
                print(f"Error creating database directory at {db_dir}: {e}")
                # Fall back to user home directory
                user_home = os.path.expanduser("~")
                db_dir = os.path.join(user_home, 'databases')
                db_path = os.path.join(db_dir, 'database.db')
                
                if not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                    print(f"Created fallback database directory: {db_dir}")
        
        # Print debug info
        print(f"Using database at: {db_path}")
        print(f"Database exists: {os.path.exists(db_path)}")
        print(f"Database directory exists: {os.path.exists(db_dir)}")
        
        return db_path
    except Exception as e:
        print(f"Error setting up database path: {e}")
        # Last resort - use local path
        local_db = os.path.join(os.path.dirname(current_file), "cognism_database.db")
        print(f"Using local database as last resort: {local_db}")
        return local_db

def create_table():
    """Creates the necessary tables if they don't exist."""
    try:
        # Make sure we can access the database
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Keep the original contacts table for backward compatibility
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT,
                Last_Name TEXT,
                Mobile_Phone TEXT,
                Email TEXT,
                Role TEXT,
                City TEXT,
                State TEXT,
                Country TEXT,
                Timezone TEXT,
                LinkedIn_URL TEXT,
                Website TEXT,
                Timestamp TEXT,
                Cognism_URL TEXT,
                contact_id TEXT,
                company_id TEXT
            )
        ''')
    
        # Create the new contacts_cognism_urls table in the main database
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts_cognism_urls (
                contact_id TEXT PRIMARY KEY,
                contact_tag TEXT,
                url TEXT UNIQUE,
                timestamp TEXT
            )
        ''')
        
        # Create contacts campaign table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts_campaign (
                counter INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id TEXT,
                campaign_id INTEGER,
                campaign_name TEXT,
                current_state TEXT DEFAULT 'undecided',
                reason TEXT,
                notes TEXT,
                campaign_batch_tag TEXT,
                campaign_batch_id TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id TEXT,
                FOREIGN KEY (contact_id) REFERENCES contacts(contact_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
                FOREIGN KEY (company_id) REFERENCES companies(company_id),
                UNIQUE(contact_id, campaign_id)
            )
        ''')
    
        conn.commit()
        conn.close()
        print(f"✅ Database tables ensured at {db_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        # Try to create a local database as fallback
        try:
            local_db = "cognism_urls.db"
            print(f"Attempting to create local database at {local_db} as fallback")
            conn = sqlite3.connect(local_db)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts_cognism_urls (
                    contact_id TEXT PRIMARY KEY,
                    contact_tag TEXT,
                    url TEXT UNIQUE,
                    timestamp TEXT
                )
            ''')
            conn.commit()
            conn.close()
            print(f"Created fallback database at {local_db}")
            # Update DB_NAME to use the local database
            global DB_NAME
            DB_NAME = os.path.abspath(local_db)
            return False
        except Exception as inner_e:
            print(f"❌ Error creating fallback database: {inner_e}")
            return False

# If this script is run directly, it will create the database and tables
if __name__ == "__main__":
    create_table()
