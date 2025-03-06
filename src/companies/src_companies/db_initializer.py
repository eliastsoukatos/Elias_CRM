import os
import sqlite3
from sqlite3 import Error

def check_for_database():
    # Get project root from environment variable if set, otherwise calculate
    project_root = os.environ.get('PROJECT_ROOT')
    
    if not project_root:
        # Fallback to calculating the path
        # Make sure to use the correct path - should be the parent of src
        script_dir = os.path.dirname(os.path.abspath(__file__))  # src_companies dir
        src_companies_dir = os.path.dirname(script_dir)          # companies dir
        companies_dir = os.path.dirname(src_companies_dir)       # src dir
        project_root = os.path.dirname(companies_dir)            # project root
    
    # Ensure we're using the database in the project root
    db_folder = os.path.join(project_root, 'databases')
    db_path = os.path.join(db_folder, 'database.db')
    
    # Print the path in debug mode
    if os.environ.get('CRM_DEBUG', '0') == '1':
        print(f"Using database at: {db_path}")

    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    db_exists = os.path.exists(db_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Reduced console output - uncomment if needed during development
        # if not db_exists:
        #     print("✅ Database 'database.db' created successfully in the 'databases' folder.")
        # else:
        #     print("📂 Database 'database.db' already exists.")

        tables = {
            "campaigns": """
                CREATE TABLE IF NOT EXISTS campaigns (
                    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_name TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    query TEXT
                );
            """,
            "companies_campaign": """
                CREATE TABLE IF NOT EXISTS companies_campaign (
                    counter INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    campaign_id INTEGER,
                    campaign_name TEXT,
                    current_state TEXT DEFAULT 'undecided',
                    reason TEXT,
                    campaign_batch_tag TEXT,
                    campaign_batch_id TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
                    UNIQUE(company_id, campaign_id)
                );
            """,
            "companies": """
                CREATE TABLE IF NOT EXISTS companies (
                    company_id TEXT PRIMARY KEY,
                    name TEXT,
                    website TEXT,
                    domain TEXT,
                    headcount INTEGER,
                    headcount_range TEXT,
                    description TEXT,
                    revenue BIGINT,
                    company_type TEXT,
                    founded TEXT,
                    verification_status TEXT,
                    min_project_size TEXT,
                    avg_hourly_rate TEXT,
                    locations TEXT,
                    hq_location TEXT
                );
            """,
            "company_locations": """
                CREATE TABLE IF NOT EXISTS company_locations (
                    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    street TEXT,
                    city TEXT,
                    state TEXT,
                    country TEXT,
                    postal_code TEXT,
                    office_type TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id, street, city, state, country, postal_code, office_type)
                );
            """,
            "company_phones": """
                CREATE TABLE IF NOT EXISTS company_phones (
                    phone_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    phone_number TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id, phone_number)
                );
            """,
            "company_technologies": """
                CREATE TABLE IF NOT EXISTS company_technologies (
                    tech_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    technology_name TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id, technology_name)
                );
            """,
            "company_industries": """
                CREATE TABLE IF NOT EXISTS company_industries (
                    industry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    industry_name TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id, industry_name)
                );
            """,
            "company_identifiers": """
                CREATE TABLE IF NOT EXISTS company_identifiers (
                    identifier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    sic_code TEXT,
                    isic_code TEXT,
                    naics_code TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id, sic_code, isic_code, naics_code)
                );
            """,
            "company_reviews": """
                CREATE TABLE IF NOT EXISTS company_reviews (
                    review_id TEXT PRIMARY KEY,
                    company_id TEXT,
                    reviewer_name TEXT,
                    review_title TEXT,
                    review_content TEXT,
                    review_rating FLOAT,
                    review_date DATE,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id)
                );
            """,
            "company_portfolio": """
                CREATE TABLE IF NOT EXISTS company_portfolio (
                    portfolio_id TEXT PRIMARY KEY,
                    company_id TEXT,
                    portfolio_name TEXT,
                    portfolio_category TEXT,
                    portfolio_size TEXT,
                    portfolio_description TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id, portfolio_name)
                );
            """,
            "company_focus_areas": """
                CREATE TABLE IF NOT EXISTS company_focus_areas (
                    focus_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    focus_title TEXT,
                    focus_name TEXT,
                    percentage INTEGER,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id, focus_title, focus_name)
                );
            """,
            "company_social_links": """
                CREATE TABLE IF NOT EXISTS company_social_links (
                    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    linkedin TEXT,
                    facebook TEXT,
                    twitter TEXT,
                    instagram TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id)
                );
            """,
            "company_verifications": """
                CREATE TABLE IF NOT EXISTS company_verifications (
                    verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    verification_status TEXT,
                    source TEXT,
                    last_updated DATE,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id)
                );
            """,
            "company_ratings": """
                CREATE TABLE IF NOT EXISTS company_ratings (
                    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    overall_rating FLOAT,
                    review_count INTEGER,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id)
                );
            """,
            "company_batches": """
                CREATE TABLE IF NOT EXISTS company_batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    batch_tag TEXT,
                    batch_id TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id, batch_tag, batch_id)
                );
            """,
            "import_logs": """
                CREATE TABLE IF NOT EXISTS import_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_tag TEXT,
                    batch_id TEXT UNIQUE,
                    source TEXT,
                    timestamp TEXT
                );
            """,
            "company_events": """
                CREATE TABLE IF NOT EXISTS company_events (
                    event_id TEXT PRIMARY KEY,
                    company_id TEXT,
                    event_data TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    UNIQUE(company_id, event_data)
                );
            """
        }

        for table_name, create_statement in tables.items():
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            result = cursor.fetchone()
            if result:
                # Commented out to reduce console output
                # print(f"📂 Table '{table_name}' already exists.")
                pass
            else:
                cursor.execute(create_statement)
                conn.commit()
                # Commented out to reduce console output
                # print(f"✅ Table '{table_name}' created successfully.")

        return True

    except Error as e:
        print(f"🚨 Error occurred: {e}")
        return False

    finally:
        if conn:
            conn.close()
            # Commented out to reduce console output
            # print("✅ Database connection closed successfully.")

if __name__ == "__main__":
    check_for_database()
