import sqlite3


def get_db_connection():
    """Gets a connection to the database with fallbacks"""
    import os

    # HARDCODED PATH FOR WINDOWS - TRY THIS FIRST
    windows_path = "/Users/anthonyhurtado/Jobs/personal/others/Elias_CRM/databases/database.db"

    # Try hardcoded path first
    try:
        db_dir = os.path.dirname(windows_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(windows_path)
        print(f"Connected to database at: {windows_path}")
        return conn
    except Exception as e:
        print(f"Hardcoded path failed: {e}")

    # Try project root path
    try:
        # Connect to the database at project root
        project_root = os.environ.get('PROJECT_ROOT')
        if not project_root:
            project_root = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        db_path = os.path.join(project_root, 'databases', 'database.db')
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(db_path)
        print(f"Connected to database at: {db_path}")
        return conn
    except Exception as e:
        print(f"Project root path failed: {e}")

        # Try user's home directory
        try:
            user_home = os.path.expanduser("~")
            alt_db_path = os.path.join(user_home, 'databases', 'database.db')

            # Ensure the directory exists
            db_folder = os.path.join(user_home, 'databases')
            if not os.path.exists(db_folder):
                os.makedirs(db_folder, exist_ok=True)

            conn = sqlite3.connect(alt_db_path)
            print(f"Connected to database at: {alt_db_path}")
            return conn
        except Exception as e2:
            print(f"User home path failed: {e2}")

            # Try APPDATA for Windows
            if os.name == 'nt':  # Windows
                try:
                    appdata = os.environ.get('APPDATA', '')
                    if appdata:
                        app_db_dir = os.path.join(
                            appdata, 'Elias_CRM', 'databases')
                        if not os.path.exists(app_db_dir):
                            os.makedirs(app_db_dir, exist_ok=True)
                        app_db_path = os.path.join(app_db_dir, 'database.db')
                        conn = sqlite3.connect(app_db_path)
                        print(f"Connected to database at: {app_db_path}")
                        return conn
                except Exception as e3:
                    print(f"APPDATA path failed: {e3}")

    # If all attempts fail, raise an exception
    raise Exception(
        "Could not connect to database with any of the fallback paths")


def clean_verification_records():
    """
    Removes empty verification records from the database.
    """
    try:
        # Connect to the database with fallbacks
        conn = get_db_connection()
        cursor = conn.cursor()

        # Commented out to reduce console output
        # print("Checking for empty verification records...")

        # Find empty verification records
        cursor.execute("""
        SELECT verification_id 
        FROM company_verifications 
        WHERE (verification_status IS NULL OR verification_status = '') 
        AND (source IS NULL OR source = '')
        """)

        empty_records = cursor.fetchall()
        count = len(empty_records)

        if count > 0:
            # Commented out to reduce console output
            # print(f"Found {count} empty verification records. Removing...")

            # Delete empty verification records
            cursor.execute("""
            DELETE FROM company_verifications 
            WHERE (verification_status IS NULL OR verification_status = '') 
            AND (source IS NULL OR source = '')
            """)

            conn.commit()
            # Commented out to reduce console output
            # print(f"Successfully removed {count} empty verification records.")
        # else:
            # Commented out to reduce console output
            # print("No empty verification records found.")

    except Exception as e:
        conn.rollback()
        print(f"Error during verification cleanup: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    clean_verification_records()
