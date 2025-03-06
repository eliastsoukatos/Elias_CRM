import sqlite3
import time
import os
import re
from utils.create_database import create_table, get_db_path

def print_db_path():
    """Prints the database path."""
    print(f"📂 Using database: {get_db_path()}")

def save_to_db(data):
    """
    Saves contact data to the database.
    """
    max_retries = 5
    retry_delay = 2  # Seconds before retrying

    for attempt in range(max_retries):
        try:
            # Get the correct database path from create_database
            db_path = get_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Ensure the table exists before inserting data
            create_table()
            
            # Look up contact_id from contacts_cognism_urls table if not provided
            if 'contact_id' not in data or not data['contact_id']:
                cognism_url = data.get('Cognism_URL')
                if cognism_url:
                    print(f"🔍 Looking up contact_id for URL: {cognism_url}")
                    cursor.execute("SELECT contact_id FROM contacts_cognism_urls WHERE url = ?", (cognism_url,))
                    result = cursor.fetchone()
                    if result:
                        data['contact_id'] = result[0]
                        print(f"✅ Found contact_id: {data['contact_id']}")
                    else:
                        print(f"⚠️ No matching contact_id found for URL: {cognism_url}")
                        data['contact_id'] = "unknown"  # Provide a default value
                else:
                    print("⚠️ No Cognism_URL provided, setting contact_id to 'unknown'")
                    data['contact_id'] = "unknown"

            # Clean the website URL if present
            if 'Website' in data and data['Website']:
                website = data['Website']
                # Remove http://, https://, and trailing /
                website = re.sub(r'^https?://', '', website)
                website = re.sub(r'/$', '', website)
                data['Website'] = website
            
            # Look up company_id from companies table based on website domain
            if 'Website' in data and data['Website']:
                website = data['Website']
                
                # Try exact website match first
                try:
                    cursor.execute("SELECT company_id FROM companies WHERE domain = ?", (website,))
                    result = cursor.fetchone()
                    
                    # If not found, try alternate methods
                    if not result:
                        # Try with www prefix
                        if not website.startswith('www.'):
                            cursor.execute("SELECT company_id FROM companies WHERE domain = ?", (f"www.{website}",))
                            result = cursor.fetchone()
                        
                        # Try without www prefix
                        if not result and website.startswith('www.'):
                            cursor.execute("SELECT company_id FROM companies WHERE domain = ?", (website[4:],))
                            result = cursor.fetchone()
                    
                    # If still not found, try LIKE match
                    if not result:
                        cursor.execute("SELECT company_id FROM companies WHERE domain LIKE ?", (f"%{website}%",))
                        result = cursor.fetchone()
                    
                    if result:
                        data['company_id'] = result[0]
                        print(f"✅ Found company_id: {data['company_id']} for website: {website}")
                    else:
                        print(f"⚠️ No company found for website: {website}")
                        data['company_id'] = None  # Set to NULL in the database
                except Exception as e:
                    print(f"⚠️ Error looking up company: {e}")
                    data['company_id'] = None  # Set to NULL if there's an error
            else:
                # No website provided
                data['company_id'] = None
                print("⚠️ No website available to match with company")
            
            # Insert data into the table (use the updated contacts table structure)
            cursor.execute('''
                INSERT INTO contacts (
                    Name, Last_Name, Mobile_Phone, Email, Role,
                    City, State, Country, Timezone, LinkedIn_URL,
                    Website, Timestamp, Cognism_URL, contact_id, company_id
                ) VALUES (
                    :Name, :Last_Name, :Mobile_Phone, :Email, :Role,
                    :City, :State, :Country, :Timezone, :LinkedIn_URL,
                    :Website, :Timestamp, :Cognism_URL, :contact_id, :company_id
                )
            ''', data)

            conn.commit()
            conn.close()
            print(f"✅ Contact data successfully saved to {db_path}")
            return
        except sqlite3.OperationalError as e:
            print(f"❌ Database error: {e}. Retrying {attempt+1}/{max_retries}...")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"❌ Unexpected error saving contact: {e}")
            break

    print(f"❌ Unable to write contact to database. Ensure it is accessible.")