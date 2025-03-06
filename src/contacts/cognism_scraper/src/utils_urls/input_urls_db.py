import sqlite3
import uuid
import time
import os
from utils.create_database import get_db_path, create_table

def save_urls_to_db(urls_data):
    """Saves the list of URLs to the database in the contacts_cognism_urls table."""
    if not urls_data or not isinstance(urls_data, list):
        print("⚠️ No URLs to save or incorrect format.")
        return
    
    try:
        # Ensure the table exists before inserting data
        table_created = create_table()
        
        # Get the path to the database
        db_path = get_db_path()
        print(f"Opening database at: {db_path}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        
        # Count URLs successfully saved
        saved_count = 0

        for entry in urls_data:
            try:
                # Rename segment to contact_tag as requested
                contact_tag = entry["segment"]
                url = entry["url"]
                timestamp = entry["timestamp"]
                
                # Generate a unique contact_id for each entry
                contact_id = str(uuid.uuid4())
    
                cursor.execute(
                    "INSERT OR IGNORE INTO contacts_cognism_urls (contact_id, contact_tag, url, timestamp) VALUES (?, ?, ?, ?)",
                    (contact_id, contact_tag, url, timestamp)
                )
                saved_count += 1
            except Exception as e:
                print(f"⚠️ Error saving URL {entry.get('url', 'unknown')}: {e}")
                continue

        conn.commit()
        conn.close()
        
        if saved_count > 0:
            print(f"✅ {saved_count} URLs saved to database in contacts_cognism_urls table.")
        else:
            print(f"⚠️ No URLs were saved to the database.")

    except Exception as e:
        print(f"⚠️ Error saving URLs to database: {e}")
        
        # Try saving to a local file as a last resort
        try:
            print("Attempting to save URLs to a local CSV file as backup...")
            import csv
            csv_file = f"cognism_urls_{int(time.time())}.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['contact_id', 'contact_tag', 'url', 'timestamp'])
                for entry in urls_data:
                    writer.writerow([
                        str(uuid.uuid4()),
                        entry.get("segment", ""),
                        entry.get("url", ""),
                        entry.get("timestamp", "")
                    ])
            print(f"✅ Saved URLs to backup file: {csv_file}")
        except Exception as backup_error:
            print(f"❌ Failed to save backup file: {backup_error}")
