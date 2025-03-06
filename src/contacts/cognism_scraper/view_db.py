import sqlite3

def choose_database():
    """
    Prompt the user to choose between `contacts.db` and `urls.db`.
    """
    while True:
        print("\n📂 Select a database to view or clear:")
        print("1️⃣ contacts.db")
        print("2️⃣ urls.db")
        choice = input("Enter the number of your choice (1 or 2): ").strip()

        if choice == "1":
            return "contacts.db"
        elif choice == "2":
            return "urls.db"
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

def view_data(db_name):
    """
    Retrieves and displays all data from the chosen database.
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Get the table names in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print(f"⚠️ No tables found in {db_name}.")
            conn.close()
            return
        
        # Display available tables
        print(f"\n📊 Tables in {db_name}:")
        for idx, table in enumerate(tables):
            print(f"{idx + 1}. {table[0]}")

        # Ask user to select a table
        table_choice = input("\nEnter the table name to view data: ").strip()

        if table_choice not in [t[0] for t in tables]:
            print("❌ Invalid table name. Please try again.")
            conn.close()
            return

        # Fetch all data from the chosen table
        cursor.execute(f"SELECT * FROM {table_choice}")
        rows = cursor.fetchall()

        # Print column names
        column_names = [description[0] for description in cursor.description]
        print("\n📋 Data in table:", table_choice)
        print(f"{' | '.join(column_names)}")
        print("-" * 100)

        # Print each row
        for row in rows:
            print(row)

        conn.close()
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

def clear_data(db_name):
    """
    Deletes all records from tables in the selected database.
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Get the table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print(f"⚠️ No tables found in {db_name}.")
            conn.close()
            return
        
        # Exclude 'sqlite_sequence' as it is an internal table
        valid_tables = [table[0] for table in tables if table[0] != 'sqlite_sequence']

        if not valid_tables:
            print(f"⚠️ No user tables found in {db_name}.")
            conn.close()
            return

        print("\n⚠️ WARNING: This will DELETE ALL DATA from the database!")
        confirm = input("Are you sure? Type 'DELETE' to confirm: ").strip()

        if confirm.upper() != "DELETE":
            print("❌ Deletion canceled.")
            conn.close()
            return

        # Delete all data from each table
        for table in valid_tables:
            cursor.execute(f"DELETE FROM {table};")
            print(f"✅ Cleared data from table: {table}")

        # Reset sqlite_sequence if exists
        cursor.execute("DELETE FROM sqlite_sequence;")

        conn.commit()
        conn.close()
        print("🚀 Database has been cleared successfully!")

    except sqlite3.Error as e:
        print(f"❌ Error clearing database: {e}")

# Main Execution
if __name__ == "__main__":
    selected_db = choose_database()

    while True:
        print("\n📌 Choose an action:")
        print("1️⃣ View data")
        print("2️⃣ Clear all data")
        print("3️⃣ Exit")
        action = input("Enter your choice (1, 2, or 3): ").strip()

        if action == "1":
            view_data(selected_db)
        elif action == "2":
            clear_data(selected_db)
        elif action == "3":
            print("👋 Exiting program.")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
