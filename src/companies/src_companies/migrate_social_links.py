import sqlite3
import sys
import os

def migrate_social_links():
    """
    Migrates LinkedIn URLs from the companies table to the company_social_links table
    and updates the schema to match the new structure.
    """
    try:
        # Connect to the database at project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(project_root, 'databases', 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Commented out to reduce console output
        # print("Starting social links migration...")
        
        # Check if linkedin_url column exists in companies table
        cursor.execute("PRAGMA table_info(companies)")
        columns = cursor.fetchall()
        linkedin_col_exists = any(col[1] == 'linkedin_url' for col in columns)
        
        if not linkedin_col_exists:
            # Commented out to reduce console output
            # print("LinkedIn URL column not found in companies table. Migration already completed.")
            return
            
        # Check the structure of company_social_links table
        cursor.execute("PRAGMA table_info(company_social_links)")
        social_columns = cursor.fetchall()
        old_structure = any(col[1] == 'platform' for col in social_columns)
        
        if old_structure:
            print("Restructuring company_social_links table...")
            
            # Create a temporary table with the new structure
            cursor.execute("""
            CREATE TABLE company_social_links_new (
                link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id TEXT,
                linkedin TEXT,
                facebook TEXT,
                twitter TEXT,
                instagram TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(company_id),
                UNIQUE(company_id)
            )
            """)
            
            # Drop the old table and rename the new one
            cursor.execute("DROP TABLE company_social_links")
            cursor.execute("ALTER TABLE company_social_links_new RENAME TO company_social_links")
            
            print("Company social links table restructured successfully.")
        
        # Get all companies with LinkedIn URLs
        cursor.execute("SELECT company_id, linkedin_url FROM companies WHERE linkedin_url IS NOT NULL AND linkedin_url != ''")
        companies = cursor.fetchall()
        
        print(f"Found {len(companies)} companies with LinkedIn URLs to migrate.")
        
        # Migrate LinkedIn URLs to the company_social_links table
        for company_id, linkedin_url in companies:
            cursor.execute(
                "INSERT INTO company_social_links (company_id, linkedin) VALUES (?, ?) "
                "ON CONFLICT(company_id) DO UPDATE SET linkedin = ?",
                (company_id, linkedin_url, linkedin_url)
            )
        
        # Create a temporary table without the linkedin_url column
        cursor.execute("""
        CREATE TABLE companies_new (
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
            avg_hourly_rate TEXT
        )
        """)
        
        # Copy data excluding linkedin_url
        cursor.execute("""
        INSERT INTO companies_new 
        SELECT 
            company_id, name, website, domain, headcount, headcount_range, 
            description, revenue, company_type, founded, verification_status, 
            min_project_size, avg_hourly_rate
        FROM companies
        """)
        
        # Drop the old table and rename the new one
        cursor.execute("DROP TABLE companies")
        cursor.execute("ALTER TABLE companies_new RENAME TO companies")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_social_links()