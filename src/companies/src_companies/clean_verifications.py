import sqlite3

def clean_verification_records():
    """
    Removes empty verification records from the database.
    """
    try:
        # Connect to the database at project root
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(project_root, 'databases', 'database.db')
        conn = sqlite3.connect(db_path)
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