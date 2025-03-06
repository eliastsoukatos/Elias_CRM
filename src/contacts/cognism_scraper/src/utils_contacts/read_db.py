import sqlite3
from utils.create_database import get_db_path

def get_urls_from_db():
    """
    Retrieves all URLs from the 'contacts_cognism_urls' table in the database.db database.
    
    :return: A list of dictionaries [{segment, url, timestamp}, ...]
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        # Use the new table name and field names
        cursor.execute("SELECT contact_id, contact_tag, url, timestamp FROM contacts_cognism_urls")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("⚠️ The database contains no URLs.")
            return []

        # Map contact_tag to segment for backward compatibility and include contact_id
        urls = [{"contact_id": row[0], "segment": row[1], "url": row[2], "timestamp": row[3]} for row in rows]
        print(f"✅ Retrieved {len(urls)} URLs from contacts_cognism_urls table")
        return urls

    except Exception as e:
        print(f"❌ Error retrieving URLs from database: {e}")
        # Try CSV import if database query fails
        try:
            import csv
            import os
            csv_files = [f for f in os.listdir() if f.startswith("cognism_urls_") and f.endswith(".csv")]
            if csv_files:
                latest_csv = max(csv_files)
                print(f"📄 Found CSV backup: {latest_csv}")
                urls = []
                with open(latest_csv, 'r') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    for row in reader:
                        if len(row) >= 4:
                            urls.append({"segment": row[1], "url": row[2], "timestamp": row[3]})
                print(f"✅ Loaded {len(urls)} URLs from CSV backup")
                return urls
        except Exception as csv_error:
            print(f"❌ Error loading from CSV: {csv_error}")
        return []
