import os
import sys
import sqlite3
from datetime import datetime
import uuid
from tabulate import tabulate

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Make the database path accessible with fallback
def get_db_path():
    """Determine the appropriate database path"""
    # Try the project root first
    file_dir = os.path.dirname(os.path.abspath(__file__))
    contacts_dir = file_dir
    src_dir = os.path.dirname(contacts_dir)
    project_root = os.path.dirname(src_dir)
    
    db_dir = os.path.join(project_root, 'databases')
    db_path = os.path.join(db_dir, 'database.db')
    
    # Ensure the database directory exists
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created database directory: {db_dir}")
        except Exception as e:
            print(f"Could not create database directory: {e}")
            
            # Try user's home directory as fallback
            user_home = os.path.expanduser("~")
            db_dir = os.path.join(user_home, 'databases')
            db_path = os.path.join(db_dir, 'database.db')
            
            if not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                    print(f"Created fallback database directory in user home: {db_dir}")
                except Exception as e2:
                    print(f"Error creating fallback directory: {e2}")
    
    print(f"Using database at: {db_path}")
    return db_path

# Get the database path
db_path = get_db_path()

def get_campaign_stats(campaign_id):
    """Get statistics for a campaign."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute(
        "SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ?", 
        (campaign_id,)
    )
    total = cursor.fetchone()[0]
    
    # Get count by state
    states = {}
    for state in ['undecided', 'approved', 'rejected']:
        cursor.execute(
            "SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ? AND current_state = ?", 
            (campaign_id, state)
        )
        states[state] = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total': total,
        'undecided': states['undecided'],
        'approved': states['approved'],
        'rejected': states['rejected']
    }

def list_campaigns():
    """List all available campaigns."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT campaign_id, campaign_name, created_at FROM campaigns ORDER BY created_at DESC")
    campaigns = cursor.fetchall()
    
    if not campaigns:
        print("No campaigns found. Create a campaign first.")
        conn.close()
        return None
    
    print("\n=== Available Campaigns ===")
    
    # Format for display
    table_data = []
    for campaign_id, name, created_at in campaigns:
        table_data.append([campaign_id, name, created_at])
    
    print(tabulate(table_data, headers=["ID", "Name", "Created At"], tablefmt="pretty"))
    
    conn.close()
    return campaigns

def select_campaign():
    """Select a campaign to work with."""
    campaigns = list_campaigns()
    
    if not campaigns:
        return None
    
    while True:
        try:
            campaign_id = input("\nEnter campaign ID to select (or 0 to cancel): ")
            
            if campaign_id == "0":
                return None
            
            campaign_id = int(campaign_id)
            
            # Verify campaign exists
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT campaign_name FROM campaigns WHERE campaign_id = ?", (campaign_id,))
            result = cursor.fetchone()
            
            if not result:
                print("Invalid campaign ID. Please try again.")
                conn.close()
                continue
            
            campaign_name = result[0]
            
            # Get campaign stats
            stats = get_campaign_stats(campaign_id)
            
            print(f"\nSelected Campaign: {campaign_name} (ID: {campaign_id})")
            print(f"Total contacts: {stats['total']}")
            print(f"Undecided: {stats['undecided']}")
            print(f"Approved: {stats['approved']}")
            print(f"Rejected: {stats['rejected']}")
            
            conn.close()
            return campaign_id, campaign_name
            
        except ValueError:
            print("Please enter a valid number.")

def get_company_ids_for_campaign(campaign_id):
    """Get all company IDs in a campaign with approved status."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT company_id FROM companies_campaign WHERE campaign_id = ? AND current_state = 'approved'", 
        (campaign_id,)
    )
    
    company_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return company_ids

def search_contacts_for_companies(company_ids, search_query=None):
    """Search for contacts from specific companies, optionally filtered by a query."""
    if not company_ids:
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        c.contact_id, 
        c.Name, 
        c.Last_Name, 
        c.Role, 
        c.Email, 
        c.LinkedIn_URL, 
        c.company_id,
        co.name as company_name
    FROM contacts c
    JOIN companies co ON c.company_id = co.company_id
    WHERE c.company_id IN ({})
    """.format(','.join(['?'] * len(company_ids)))
    
    params = company_ids.copy()
    
    if search_query:
        # Add search conditions for name, role, email
        query += """ AND (
            c.Name LIKE ? OR 
            c.Last_Name LIKE ? OR 
            c.Role LIKE ? OR 
            c.Email LIKE ?
        )"""
        search_term = f"%{search_query}%"
        params.extend([search_term, search_term, search_term, search_term])
    
    cursor.execute(query, params)
    contacts = cursor.fetchall()
    
    conn.close()
    return contacts

def display_contacts(contacts):
    """Display contacts in a formatted table."""
    if not contacts:
        print("No contacts found matching your criteria.")
        return
    
    table_data = []
    for contact in contacts:
        contact_id, first_name, last_name, role, email, linkedin, company_id, company_name = contact
        name = f"{first_name} {last_name}" if last_name else first_name
        table_data.append([contact_id, name, role, email, company_name])
    
    print(tabulate(table_data, headers=["ID", "Name", "Role", "Email", "Company"], tablefmt="pretty"))

def add_contacts_to_campaign(campaign_id, campaign_name, contact_ids):
    """Add selected contacts to the campaign."""
    if not contact_ids:
        print("No contacts selected.")
        return 0
    
    # Prompt for batch tag
    print("\nEnter a batch tag to identify this group of contacts:")
    batch_tag = input("> ").strip()
    
    if not batch_tag:
        # If empty, use a default tag with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_tag = f"cli_add_{timestamp}"
        print(f"Using default batch tag: {batch_tag}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Generate batch identifier
    batch_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add each contact to the campaign
    added_count = 0
    for contact_id in contact_ids:
        try:
            # Get company_id for this contact
            cursor.execute(
                "SELECT company_id FROM contacts WHERE contact_id = ?",
                (contact_id,)
            )
            result = cursor.fetchone()
            company_id = result[0] if result else None
            
            cursor.execute(
                """
                INSERT INTO contacts_campaign 
                (contact_id, campaign_id, campaign_name, campaign_batch_tag, campaign_batch_id, company_id, notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (contact_id, campaign_id, campaign_name, batch_tag, batch_id, company_id, "")
            )
            added_count += 1
        except sqlite3.IntegrityError:
            # Contact already in campaign
            pass
    
    # Add batch to import logs
    cursor.execute(
        "INSERT INTO import_logs (batch_tag, batch_id, source, timestamp) VALUES (?, ?, ?, ?)",
        (batch_tag, batch_id, "manual_contact_add", timestamp)
    )
    
    conn.commit()
    conn.close()
    
    print(f"Successfully added {added_count} contacts with batch tag: {batch_tag}")
    return added_count

def search_and_add_contacts():
    """Main function to search for contacts and add them to a campaign."""
    # Select campaign
    campaign_data = select_campaign()
    if not campaign_data:
        return
    
    campaign_id, campaign_name = campaign_data
    
    # Get approved companies for this campaign
    company_ids = get_company_ids_for_campaign(campaign_id)
    
    if not company_ids:
        print(f"No approved companies found in campaign '{campaign_name}'. Approve companies first.")
        return
    
    print(f"\nFound {len(company_ids)} approved companies in this campaign.")
    
    # Search for contacts
    while True:
        search_query = input("\nEnter search term for contacts (or press Enter to see all): ").strip()
        
        contacts = search_contacts_for_companies(company_ids, search_query if search_query else None)
        
        print(f"\nFound {len(contacts)} contacts matching your criteria:")
        display_contacts(contacts)
        
        # Select contacts to add
        selection = input("\nEnter contact IDs to add (comma-separated) or 'all' for all contacts (0 to cancel): ").strip()
        
        if selection == "0":
            return
        
        if selection.lower() == "all":
            contact_ids = [contact[0] for contact in contacts]
        else:
            try:
                contact_ids = [int(id.strip()) for id in selection.split(",") if id.strip()]
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")
                continue
        
        # Add contacts to campaign
        added = add_contacts_to_campaign(campaign_id, campaign_name, contact_ids)
        print(f"\nAdded {added} contacts to campaign '{campaign_name}'")
        
        another = input("\nSearch for more contacts? (y/n): ").lower()
        if another != 'y':
            break

def clear_campaign_contacts():
    """Clear all contacts from a selected campaign."""
    # Select campaign
    campaign_data = select_campaign()
    if not campaign_data:
        return
    
    campaign_id, campaign_name = campaign_data
    
    # Confirm with user
    confirm = input(f"\nAre you sure you want to remove ALL contacts from campaign '{campaign_name}'? (y/n): ").lower()
    
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Clear contacts
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current count
    cursor.execute(
        "SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ?", 
        (campaign_id,)
    )
    count = cursor.fetchone()[0]
    
    # Delete all contacts in the campaign
    cursor.execute(
        "DELETE FROM contacts_campaign WHERE campaign_id = ?",
        (campaign_id,)
    )
    
    conn.commit()
    conn.close()
    
    print(f"\nSuccessfully removed {count} contacts from campaign '{campaign_name}'.")

def main():
    """Main function to run the contact campaign process."""
    print("\n=== Contact Campaign Process ===")
    
    while True:
        print("\nOptions:")
        print("1. Search and Add Contacts to Campaign")
        print("2. Run Contact Prospector")
        print("3. Clear Campaign Contacts")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            search_and_add_contacts()
        elif choice == "2":
            # Launch the contact prospector
            import subprocess
            import os
            
            # Calculate path to contact prospector script
            contacts_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(contacts_dir, 'run_contact_prospector.py')
            
            # Check if the file exists
            if not os.path.exists(script_path):
                print(f"Error: Could not find the contact prospector script at {script_path}")
                continue
            
            # Run the script
            subprocess.Popen([sys.executable, script_path])
        elif choice == "3":
            clear_campaign_contacts()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()