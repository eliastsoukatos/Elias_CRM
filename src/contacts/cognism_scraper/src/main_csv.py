import sqlite3
import csv
from utils.create_database import get_db_path

def export_contacts_to_csv(csv_filename="contacts_export.csv"):
    """
    Exports the 'contacts' table from contacts.db into a CSV file.
    
    :param csv_filename: The name of the output CSV file.
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM contacts")  # Get all data from contacts table
        contacts = cursor.fetchall()

        if not contacts:
            print("⚠️ No contacts found in the database.")
            return

        # Get column names
        column_names = [desc[0] for desc in cursor.description]

        # Write to CSV
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(column_names)  # Write header
            writer.writerows(contacts)  # Write data

        conn.close()
        print(f"✅ Contacts exported successfully to {csv_filename}")

    except Exception as e:
        print(f"❌ Error exporting contacts to CSV: {e}")
