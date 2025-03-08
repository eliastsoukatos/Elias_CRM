import sqlite3
from sqlite3 import Error
from datetime import datetime

def connect_db():
    """
    Establece conexión con la base de datos 'databases/database.db'.
    """
    # Ensure we're connecting to the database at project root level
    import os
    
    # DEBUG OUTPUT
    print(f"[DEBUG] DB_WRITER Connect_db: Current working directory: {os.getcwd()}")
    print(f"[DEBUG] __file__: {__file__}")
    print(f"[DEBUG] abspath(__file__): {os.path.abspath(__file__)}")
    print(f"[DEBUG] Environment vars: PROJECT_ROOT={os.environ.get('PROJECT_ROOT')}")
    
    # HARDCODED PATH FOR WINDOWS - TRY THIS FIRST
    windows_path = "C:\\Users\\EliasTsoukatos\\Documents\\software_code\\Elias_CRM\\databases\\database.db"
    print(f"🔍 Trying hardcoded Windows database path: {windows_path}")
    
    # Try hardcoded path first
    try:
        db_dir = os.path.dirname(windows_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"✅ Created hardcoded database directory: {db_dir}")
            
        conn = sqlite3.connect(windows_path)
        print(f"✅ Successfully connected to hardcoded database path")
        # Set the project root for future use
        os.environ['PROJECT_ROOT'] = os.path.dirname(db_dir)
        return conn
    except Exception as e:
        print(f"⚠️ Hardcoded path failed: {e}, trying next option")
    
    # Get project root from environment variable if set, otherwise calculate
    project_root = os.environ.get('PROJECT_ROOT')
    print(f"[DEBUG] PROJECT_ROOT from env: {project_root}")
    
    if not project_root:
        # Fallback to calculating the path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        print(f"[DEBUG] Calculated project_root: {project_root}")
    
    # EXPLICIT WINDOWS FIX
    if os.name == 'nt' and '\\' in project_root:  # Windows path
        project_root = project_root.replace("/", "\\")
        print(f"[DEBUG] Windows path detected, fixed project_root: {project_root}")
    
    # Create the database path using the project root
    db_path = os.path.join(project_root, 'databases', 'database.db')
    print(f"[DEBUG] Database path: {db_path}")
    
    try:
        # Ensure the database directory exists
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"✅ Created database directory: {db_dir}")
            
        conn = sqlite3.connect(db_path)
        print(f"✅ Successfully connected to database")
        return conn
    except Error as e:
        print(f"⚠️ Error connecting to database: {e}")
        print(f"[DEBUG] Exception type: {type(e)}")
        
        # Try alternate location in user's home directory
        try:
            user_home = os.path.expanduser("~")
            print(f"[DEBUG] User home: {user_home}")
            alt_db_path = os.path.join(user_home, 'databases', 'database.db')
            
            # Ensure the directory exists
            db_folder = os.path.join(user_home, 'databases')
            if not os.path.exists(db_folder):
                os.makedirs(db_folder, exist_ok=True)
                print(f"✅ Created user home database directory: {db_folder}")
                
            print(f"🔍 Trying alternate database path: {alt_db_path}")
            conn = sqlite3.connect(alt_db_path)
            print(f"✅ Successfully connected to alternate database path")
            return conn
        except Exception as e2:
            print(f"⚠️ User home database failed: {e2}")
            
            # ONE FINAL ATTEMPT - TRY APPDATA FOLDER
            try:
                if os.name == 'nt':  # Windows
                    appdata = os.environ.get('APPDATA', '')
                    print(f"[DEBUG] Trying APPDATA folder: {appdata}")
                    if appdata:
                        app_db_dir = os.path.join(appdata, 'Elias_CRM', 'databases')
                        if not os.path.exists(app_db_dir):
                            os.makedirs(app_db_dir, exist_ok=True)
                            print(f"✅ Created APPDATA database directory: {app_db_dir}")
                        app_db_path = os.path.join(app_db_dir, 'database.db')
                        print(f"🔍 Trying APPDATA database path: {app_db_path}")
                        conn = sqlite3.connect(app_db_path)
                        print(f"✅ Successfully connected to APPDATA database")
                        return conn
            except Exception as e3:
                print(f"⚠️ APPDATA database failed: {e3}")
                raise e  # Re-raise the original error

def insert_or_update(cursor, table, data, unique_key):
    placeholders = ', '.join(['?'] * len(data))
    columns = ', '.join(data.keys())
    
    # Use CASE WHEN to only update with non-NULL/non-empty values
    # This preserves existing data when new data is NULL or empty
    update_fields = ', '.join(
        f"{k}=CASE WHEN excluded.{k} IS NOT NULL AND excluded.{k} != '' THEN excluded.{k} ELSE {k} END"
        for k in data.keys() if k != unique_key
    )

    sql = f"""
    INSERT INTO {table} ({columns})
    VALUES ({placeholders})
    ON CONFLICT({unique_key}) DO UPDATE SET {update_fields};
    """
    cursor.execute(sql, tuple(data.values()))

def insert_related_table(cursor, table, company_id, data_list, unique_fields):
    for data in data_list:
        data['company_id'] = company_id
        placeholders = ', '.join(['?'] * len(data))
        columns = ', '.join(data.keys())
        conflict_clause = ', '.join(unique_fields)
        
        # For phone numbers and other tables, we want to keep existing data
        # but allow new values to be added if they're unique
        if table == "company_phones":
            # For phones, we just use DO NOTHING to avoid duplicating the same phone number
            action = "DO NOTHING"
        else:
            # For other tables, we preserve existing non-empty values
            update_fields = ', '.join(
                f"{k}=CASE WHEN excluded.{k} IS NOT NULL AND excluded.{k} != '' THEN excluded.{k} ELSE {k} END"
                for k in data.keys() if k not in unique_fields
            )
            action = f"DO UPDATE SET {update_fields}" if update_fields else "DO NOTHING"

        sql = f"""
        INSERT INTO {table} ({columns})
        VALUES ({placeholders})
        ON CONFLICT({conflict_clause}) {action};
        """
        cursor.execute(sql, tuple(data.values()))

def db_writer(data):
    """
    Inserta o actualiza la información de la empresa, registra la asociación en company_batches,
    e inserta un registro en import_logs (si es la primera vez para este batch).
    """
    try:
        # Debug data structure for tables
        for table_name, table_data in data.items():
            if table_name not in ["batch_tag", "batch_id", "source"] and table_data:
                if isinstance(table_data, list) and table_data:
                    print(f"📋 Writing to {table_name} with data: {table_data}")
                elif isinstance(table_data, dict):
                    print(f"📋 Writing to {table_name} with data: {table_data}")
        conn = connect_db()
        cursor = conn.cursor()
        conn.execute('BEGIN TRANSACTION;')

        # Insertar o actualizar en la tabla companies
        insert_or_update(cursor, "companies", data['companies'], "company_id")
        company_id = data['companies']['company_id']

        # Insertar datos en la tabla company_locations (usa los nuevos campos)
        insert_related_table(cursor, "company_locations", company_id, data.get("company_locations", []), 
                             ["company_id", "street", "city", "state", "country", "postal_code", "office_type"])
        insert_related_table(cursor, "company_phones", company_id, data.get("company_phones", []), 
                             ["company_id", "phone_number"])
        insert_related_table(cursor, "company_technologies", company_id, data.get("company_technologies", []), 
                             ["company_id", "technology_name"])
        insert_related_table(cursor, "company_industries", company_id, data.get("company_industries", []), 
                             ["company_id", "industry_name"])
        insert_related_table(cursor, "company_identifiers", company_id, data.get("company_identifiers", []), 
                             ["company_id", "sic_code", "isic_code", "naics_code"])
        insert_related_table(cursor, "company_reviews", company_id, data.get("company_reviews", []), 
                             ["review_id"])
        insert_related_table(cursor, "company_portfolio", company_id, data.get("company_portfolio", []), 
                             ["company_id", "portfolio_name"])
        insert_related_table(cursor, "company_focus_areas", company_id, data.get("company_focus_areas", []), 
                             ["company_id", "focus_title", "focus_name"])
        # Handle social links in the new format - preserve existing values
        social_links = data.get("company_social_links", [])
        if social_links:
            for link_data in social_links:
                link_data['company_id'] = company_id
                placeholders = ', '.join(['?'] * len(link_data))
                columns = ', '.join(link_data.keys())
                
                # Use COALESCE to only update if new value is not NULL/empty
                update_fields = ', '.join(
                    f"{k}=CASE WHEN excluded.{k} IS NOT NULL AND excluded.{k} != '' THEN excluded.{k} ELSE {k} END"
                    for k in link_data.keys() if k != "company_id"
                )
                
                sql = f"""
                INSERT INTO company_social_links ({columns})
                VALUES ({placeholders})
                ON CONFLICT(company_id) DO UPDATE SET {update_fields};
                """
                cursor.execute(sql, tuple(link_data.values()))
        # Only insert verification records if they have actual data
        verification_records = []
        for verification in data.get("company_verifications", []):
            if verification.get("verification_status") or verification.get("source"):
                verification_records.append(verification)
        
        if verification_records:
            insert_related_table(cursor, "company_verifications", company_id, verification_records, ["verification_id"])
        
        # Only insert rating records if they have actual data
        rating_records = []
        for rating in data.get("company_ratings", []):
            if rating.get("overall_rating") is not None or rating.get("review_count") is not None:
                rating_records.append(rating)
        
        if rating_records:
            insert_related_table(cursor, "company_ratings", company_id, rating_records, ["rating_id"])
        insert_related_table(cursor, "company_events", company_id, data.get("company_events", []), 
                             ["event_id"])
                             
        # Handle any custom tables that were created
        for table_name, table_data in data.items():
            # Skip standard tables and non-data fields
            if table_name in ["companies", "company_locations", "company_phones", 
                             "company_technologies", "company_industries", 
                             "company_identifiers", "company_reviews", 
                             "company_portfolio", "company_focus_areas", 
                             "company_social_links", "company_verifications", 
                             "company_events", "company_ratings", 
                             "batch_tag", "batch_id", "source"]:
                continue
                
            # Check if this is a custom table with data
            if isinstance(table_data, list) and table_data:
                print(f"📊 Writing to custom table {table_name}")
                try:
                    # Verify table exists
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    if cursor.fetchone():
                        # Use a simple conflict resolution for custom tables
                        for record in table_data:
                            # Ensure company_id is set
                            record['company_id'] = company_id
                            
                            # Build dynamic insert query
                            placeholders = ', '.join(['?'] * len(record))
                            columns = ', '.join(record.keys())
                            
                            sql = f"""
                            INSERT OR REPLACE INTO {table_name} ({columns})
                            VALUES ({placeholders});
                            """
                            cursor.execute(sql, tuple(record.values()))
                            print(f"✅ Inserted record into custom table {table_name}")
                    else:
                        print(f"⚠️ Custom table {table_name} not found in database. Skipping.")
                except Exception as e:
                    print(f"🚨 Error inserting into custom table {table_name}: {e}")

        # Insertar la asociación de la empresa con el batch en company_batches
        batch_info = {
            "batch_tag": data["batch_tag"],
            "batch_id": data["batch_id"]
        }
        insert_related_table(cursor, "company_batches", company_id, [batch_info], 
                             ["company_id", "batch_tag", "batch_id"])

        # Insertar en import_logs si no existe un registro para este batch
        cursor.execute("SELECT log_id FROM import_logs WHERE batch_id = ?", (data["batch_id"],))
        if not cursor.fetchone():
            import_log = {
                "batch_tag": data["batch_tag"],
                "batch_id": data["batch_id"],
                "source": data.get("source", "unknown"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            insert_or_update(cursor, "import_logs", import_log, "batch_id")

        conn.commit()
        print(f"✅ Data successfully written for company_id: {company_id}")
    except Error as e:
        conn.rollback()
        print(f"🚨 Transaction failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    sample_data = {
        "companies": {
            "company_id": "test-id",
            "name": "Test Company",
            "website": "https://testcompany.com",
            "domain": "testcompany.com",
            "headcount": 100,
            "revenue": 5000000,
            "founded": "2020",
            "linkedin_url": ""
        },
        "company_technologies": [{"technology_name": "Python"}, {"technology_name": "Django"}],
        "company_industries": [{"industry_name": "Technology"}],
        "company_portfolio": [
            {
                "portfolio_id": "p1",
                "portfolio_name": "Project Alpha",
                "portfolio_category": "Web Development",
                "portfolio_size": "Large",
                "portfolio_description": "A flagship project."
            }
        ],
        "company_events": [],
        "source": "csv import",
        "batch_tag": "test-tag",
        "batch_id": "batch-test"
    }
    db_writer(sample_data)
