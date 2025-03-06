import sqlite3
import os
from utils_contacts.read_db import get_urls_from_db
from utils.create_database import create_table, get_db_path
from config import OVERWRITE_SEGMENT  # Import overwrite setting

def get_existing_urls():
    """
    Fetches all existing Cognism URLs from the contacts table in the SQLite database.
    
    :return: A dictionary of URLs with their associated segments.
    """
    # Get the correct database path from create_database
    db_path = get_db_path()
   
    if not os.path.exists(db_path):
        print(f"⚠️ Database file not found: {db_path}. Ensuring database structure...")
        create_table()  # Call the function from database.py
        print(f"✅ Database ready at: {db_path}")
    
    # Create the contacts table if it does not exist
    try:
        print(f"🔍 Connecting to database at: {db_path}")  # Debugging
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT Cognism_URL, Segment FROM contacts")
        existing_urls = {row[0]: row[1] for row in cursor.fetchall() if row[0]}  # Store as {url: segment}

        conn.close()
        print(f"✅ Found {len(existing_urls)} existing URLs in database.")
        return existing_urls

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return {}

def update_segment(url, new_segment):
    """
    Updates the segment for an existing Cognism URL in the database.

    :param url: The Cognism URL to update.
    :param new_segment: The new segment to overwrite.
    """
    try:
        # Get the correct database path
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("UPDATE contacts SET Segment = ? WHERE Cognism_URL = ?", (new_segment, url))
        conn.commit()
        conn.close()
        print(f"🔄 Updated segment for URL: {url}")

    except sqlite3.Error as e:
        print(f"❌ Error updating segment for {url}: {e}")

def filter_new_urls():
    """
    Filters out URLs that already exist in the database.
    If a URL exists but has a different segment, update the segment (if enabled in config).
    
    :return: A list of new URLs that are not present in the database.
    """
    # Load URLs from the database or CSV
    url_entries = get_urls_from_db()
    print(f"📥 Loaded {len(url_entries)} URLs with their contact_ids.")

    # Get existing URLs from the database
    existing_urls = get_existing_urls()

    new_urls = []  # Store new URLs only

    for entry in url_entries:
        url = entry["url"]
        segment = entry["segment"]

        if url in existing_urls:
            # Check if segment is different
            if existing_urls[url] != segment:
                print(f"⚠️ URL found in database, but segment is different: {url}")
                print(f"   - Old segment: {existing_urls[url]}")
                print(f"   - New segment: {segment}")

                # Update segment if overwriting is enabled
                if OVERWRITE_SEGMENT:
                    update_segment(url, segment)
                    print("✅ Segment updated in database.")
                else:
                    print("🚫 Segment overwrite is disabled. Keeping old segment.")

        else:
            new_urls.append(entry)  # Only add completely new URLs

    print(f"✅ {len(new_urls)} new URLs found (not in database).")
    return new_urls
