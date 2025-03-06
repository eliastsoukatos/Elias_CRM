import sqlite3

def clean_rating_records():
    """
    Removes empty rating records from the database.
    """
    try:
        # Connect to the database at project root
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(project_root, 'databases', 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Commented out to reduce console output
        # print("Checking for empty rating records...")
        
        # Find empty rating records
        cursor.execute("""
        SELECT rating_id 
        FROM company_ratings 
        WHERE (overall_rating IS NULL) 
        AND (review_count IS NULL)
        """)
        
        empty_records = cursor.fetchall()
        count = len(empty_records)
        
        if count > 0:
            # Commented out to reduce console output
            # print(f"Found {count} empty rating records. Removing...")
            
            # Delete empty rating records
            cursor.execute("""
            DELETE FROM company_ratings 
            WHERE (overall_rating IS NULL) 
            AND (review_count IS NULL)
            """)
            
            conn.commit()
            # Commented out to reduce console output
            # print(f"Successfully removed {count} empty rating records.")
        # else:
            # Commented out to reduce console output
            # print("No empty rating records found.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during rating cleanup: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_rating_records()