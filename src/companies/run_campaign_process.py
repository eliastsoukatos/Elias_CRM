import sys
import os
import sqlite3
from sqlite3 import Error
import datetime
import uuid

# Set up path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_companies_dir = os.path.join(current_dir, 'src_companies')
if src_companies_dir not in sys.path:
    sys.path.insert(0, src_companies_dir)

# Set up project root path for database access
project_root = os.path.dirname(os.path.dirname(current_dir))
os.environ['PROJECT_ROOT'] = project_root

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def get_db_connection():
    """
    Create a database connection to the SQLite database.
    """
    # Use platform-independent path using environment variable or construct it
    project_root = os.environ.get('PROJECT_ROOT')
    if not project_root:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    db_path = os.path.join(project_root, 'databases', 'database.db')
    
    print(f"{Colors.CYAN}Using database path: {db_path}{Colors.END}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    except Error as e:
        print(f"{Colors.RED}Error connecting to database: {e}{Colors.END}")
        return None

def list_campaigns():
    """
    List all existing campaigns.
    """
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT campaign_id, campaign_name, created_at FROM campaigns ORDER BY created_at DESC")
        campaigns = cursor.fetchall()
        
        if not campaigns:
            print(f"{Colors.YELLOW}No campaigns found in the database.{Colors.END}")
            return
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}📋 Existing Campaigns:{Colors.END}")
        print("-" * 70)
        print(f"{Colors.BOLD}{'ID':<5} {'Campaign Name':<30} {'Created At':<20}{Colors.END}")
        print("-" * 70)
        
        for campaign in campaigns:
            print(f"{campaign['campaign_id']:<5} {campaign['campaign_name']:<30} {campaign['created_at']:<20}")
        
        print("-" * 70)
        
    except Error as e:
        print(f"{Colors.RED}Error listing campaigns: {e}{Colors.END}")
    finally:
        conn.close()

def create_campaign():
    """
    Create a new campaign.
    """
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Ask for campaign name
        while True:
            campaign_name = input(f"{Colors.BOLD}Enter campaign name: {Colors.END}").strip()
            if not campaign_name:
                print(f"{Colors.RED}Campaign name cannot be empty. Please try again.{Colors.END}")
                continue
            
            # Check if campaign name already exists
            cursor = conn.cursor()
            cursor.execute("SELECT campaign_id FROM campaigns WHERE campaign_name = ?", (campaign_name,))
            if cursor.fetchone():
                print(f"{Colors.RED}A campaign with this name already exists. Please choose a different name.{Colors.END}")
                continue
            
            break
        
        # Ask for SQL query to filter companies
        print(f"\n{Colors.BOLD}{Colors.BLUE}📝 Enter an SQLite query to filter companies for this campaign:{Colors.END}")
        print(f"{Colors.YELLOW}(The query must return at least company_id field){Colors.END}")
        print(f"{Colors.YELLOW}Example: SELECT company_id FROM companies WHERE headcount > 50{Colors.END}")
        
        while True:
            query = input(f"\n{Colors.BOLD}Query: {Colors.END}").strip()
            if not query:
                print(f"{Colors.RED}Query cannot be empty. Please try again.{Colors.END}")
                continue
            
            # Validate the query
            try:
                # Make sure query contains SELECT and company_id
                if "SELECT" not in query.upper() or "company_id" not in query.lower():
                    print(f"{Colors.RED}Query must be a SELECT statement and include company_id field.{Colors.END}")
                    continue
                
                # Test run the query
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                
                # Check if any results were returned
                if not results:
                    print(f"{Colors.YELLOW}Warning: This query returned 0 results. Are you sure you want to continue?{Colors.END}")
                    confirm = input(f"{Colors.BOLD}Continue with this query? (y/n): {Colors.END}").strip().lower()
                    if confirm != 'y':
                        continue
                else:
                    # Verify company_id is in results
                    if 'company_id' not in dict(results[0]):
                        print(f"{Colors.RED}Query results must include company_id field.{Colors.END}")
                        continue
                    
                    total_results = len(results)
                    print(f"{Colors.GREEN}Query validated successfully! Found {total_results} matching companies.{Colors.END}")
                
                break
            except Error as e:
                print(f"{Colors.RED}Error in SQL query: {e}{Colors.END}")
                continue
        
        # Ask for number of companies to import
        max_companies = total_results
        while True:
            try:
                num_companies = input(f"{Colors.BOLD}How many companies to import (max {max_companies}, enter 0 for all): {Colors.END}").strip()
                if not num_companies:
                    num_companies = max_companies
                    break
                
                num_companies = int(num_companies)
                if num_companies < 0:
                    print(f"{Colors.RED}Please enter a positive number.{Colors.END}")
                    continue
                elif num_companies == 0:
                    num_companies = max_companies
                    break
                elif num_companies > max_companies:
                    print(f"{Colors.YELLOW}Maximum {max_companies} companies available. Will import all of them.{Colors.END}")
                    num_companies = max_companies
                    break
                else:
                    break
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number.{Colors.END}")
                continue
        
        # Ask for campaign batch tag
        campaign_batch_tag = input(f"{Colors.BOLD}Enter a batch tag (e.g., 'initial', 'follow-up'): {Colors.END}").strip()
        if not campaign_batch_tag:
            campaign_batch_tag = "initial"
            
        # Generate a unique campaign batch ID
        campaign_batch_id = str(uuid.uuid4())
        
        # Save the campaign to the database
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO campaigns (campaign_name, query) VALUES (?, ?)",
            (campaign_name, query)
        )
        campaign_id = cursor.lastrowid
        
        # Insert companies into companies_campaign table with batch information
        cursor.execute(query)
        companies = cursor.fetchall()
        
        # Limit to the requested number of companies
        companies = companies[:num_companies]
        
        added_count = 0
        for company in companies:
            try:
                cursor.execute(
                    """INSERT INTO companies_campaign 
                       (company_id, campaign_id, campaign_name, 
                        campaign_batch_tag, campaign_batch_id) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (company['company_id'], campaign_id, campaign_name, 
                     campaign_batch_tag, campaign_batch_id)
                )
                added_count += 1
            except sqlite3.IntegrityError:
                # Skip duplicates (although there shouldn't be any in a new campaign)
                continue
        
        # Log the import
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO import_logs (batch_tag, batch_id, source, timestamp) VALUES (?, ?, ?, ?)",
            (campaign_batch_tag, campaign_batch_id, f"Campaign: {campaign_name}", timestamp)
        )
        
        conn.commit()
        print(f"\n{Colors.GREEN}✅ Campaign '{campaign_name}' created successfully with {added_count} companies!{Colors.END}")
        print(f"{Colors.CYAN}Batch Tag: {campaign_batch_tag}{Colors.END}")
        print(f"{Colors.CYAN}Batch ID: {campaign_batch_id}{Colors.END}")
        
    except Error as e:
        conn.rollback()
        print(f"{Colors.RED}Error creating campaign: {e}{Colors.END}")
    finally:
        conn.close()

def add_companies_to_campaign(campaign_id, campaign_name):
    """
    Add more companies to an existing campaign.
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        # Ask for SQL query to filter companies
        print(f"\n{Colors.BOLD}{Colors.BLUE}📝 Enter an SQLite query to filter companies to add to this campaign:{Colors.END}")
        print(f"{Colors.YELLOW}(The query must return at least company_id field){Colors.END}")
        print(f"{Colors.YELLOW}Example: SELECT company_id FROM companies WHERE headcount > 50{Colors.END}")
        
        while True:
            query = input(f"\n{Colors.BOLD}Query: {Colors.END}").strip()
            if not query:
                print(f"{Colors.RED}Query cannot be empty. Please try again.{Colors.END}")
                continue
            
            # Validate the query
            try:
                # Make sure query contains SELECT and company_id
                if "SELECT" not in query.upper() or "company_id" not in query.lower():
                    print(f"{Colors.RED}Query must be a SELECT statement and include company_id field.{Colors.END}")
                    continue
                
                # Test run the query
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                
                # Check if any results were returned
                if not results:
                    print(f"{Colors.YELLOW}Warning: This query returned 0 results. Are you sure you want to continue?{Colors.END}")
                    confirm = input(f"{Colors.BOLD}Continue with this query? (y/n): {Colors.END}").strip().lower()
                    if confirm != 'y':
                        continue
                else:
                    # Verify company_id is in results
                    if 'company_id' not in dict(results[0]):
                        print(f"{Colors.RED}Query results must include company_id field.{Colors.END}")
                        continue
                    
                    total_results = len(results)
                    print(f"{Colors.GREEN}Query validated successfully! Found {total_results} matching companies.{Colors.END}")
                
                break
            except Error as e:
                print(f"{Colors.RED}Error in SQL query: {e}{Colors.END}")
                continue
        
        # Get list of companies already in campaign
        cursor = conn.cursor()
        cursor.execute("SELECT company_id FROM companies_campaign WHERE campaign_id = ?", (campaign_id,))
        existing_company_ids = set([row['company_id'] for row in cursor.fetchall()])
        
        # Filter query results to exclude companies already in campaign
        cursor.execute(query)
        all_companies = cursor.fetchall()
        new_companies = [company for company in all_companies if company['company_id'] not in existing_company_ids]
        
        if not new_companies:
            print(f"{Colors.YELLOW}Warning: All companies from this query are already in the campaign.{Colors.END}")
            confirm = input(f"{Colors.BOLD}Do you want to continue anyway? (y/n): {Colors.END}").strip().lower()
            if confirm != 'y':
                return False
        else:
            print(f"{Colors.GREEN}Found {len(new_companies)} new companies that are not already in this campaign.{Colors.END}")
        
        # Ask for number of companies to import
        max_companies = len(new_companies)
        while True:
            try:
                num_companies = input(f"{Colors.BOLD}How many companies to import (max {max_companies}, enter 0 for all): {Colors.END}").strip()
                if not num_companies:
                    num_companies = max_companies
                    break
                
                num_companies = int(num_companies)
                if num_companies < 0:
                    print(f"{Colors.RED}Please enter a positive number.{Colors.END}")
                    continue
                elif num_companies == 0:
                    num_companies = max_companies
                    break
                elif num_companies > max_companies:
                    print(f"{Colors.YELLOW}Maximum {max_companies} companies available. Will import all of them.{Colors.END}")
                    num_companies = max_companies
                    break
                else:
                    break
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number.{Colors.END}")
                continue
        
        # Ask for campaign batch tag
        campaign_batch_tag = input(f"{Colors.BOLD}Enter a batch tag (e.g., 'follow-up', 'additional'): {Colors.END}").strip()
        if not campaign_batch_tag:
            campaign_batch_tag = "additional"
            
        # Generate a unique campaign batch ID
        campaign_batch_id = str(uuid.uuid4())
        
        # Limit to the requested number of companies
        companies_to_add = new_companies[:num_companies]
        
        # Insert companies into companies_campaign table with batch information
        added_count = 0
        for company in companies_to_add:
            try:
                cursor.execute(
                    """INSERT INTO companies_campaign 
                       (company_id, campaign_id, campaign_name, 
                        campaign_batch_tag, campaign_batch_id) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (company['company_id'], campaign_id, campaign_name, 
                     campaign_batch_tag, campaign_batch_id)
                )
                added_count += 1
            except sqlite3.IntegrityError:
                # This should not happen since we filtered out existing companies
                continue
        
        # Log the import
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO import_logs (batch_tag, batch_id, source, timestamp) VALUES (?, ?, ?, ?)",
            (campaign_batch_tag, campaign_batch_id, f"Campaign: {campaign_name} (Additional)", timestamp)
        )
        
        conn.commit()
        print(f"\n{Colors.GREEN}✅ Added {added_count} new companies to campaign '{campaign_name}'!{Colors.END}")
        print(f"{Colors.CYAN}Batch Tag: {campaign_batch_tag}{Colors.END}")
        print(f"{Colors.CYAN}Batch ID: {campaign_batch_id}{Colors.END}")
        return True
        
    except Error as e:
        conn.rollback()
        print(f"{Colors.RED}Error adding companies to campaign: {e}{Colors.END}")
        return False
    finally:
        conn.close()

def view_campaign_batches(campaign_id):
    """
    View all batches for a campaign.
    """
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # View campaign batches
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                campaign_batch_tag, 
                campaign_batch_id, 
                COUNT(*) as company_count, 
                MIN(added_at) as added_at
            FROM companies_campaign
            WHERE campaign_id = ?
            GROUP BY campaign_batch_tag, campaign_batch_id
            ORDER BY added_at DESC
        """, (campaign_id,))
        
        campaign_batches = cursor.fetchall()
        
        if not campaign_batches:
            print(f"{Colors.YELLOW}No batches found for this campaign.{Colors.END}")
        else:
            print(f"\n{Colors.BOLD}{Colors.BLUE}📋 Campaign Batches:{Colors.END}")
            print("-" * 100)
            print(f"{Colors.BOLD}{'Batch Tag':<20} {'Batch ID':<40} {'Companies':<10} {'Added At':<20}{Colors.END}")
            print("-" * 100)
            
            for batch in campaign_batches:
                print(f"{batch['campaign_batch_tag']:<20} {batch['campaign_batch_id']:<40} {batch['company_count']:<10} {batch['added_at']:<20}")
            
            print("-" * 100)
        
    except Error as e:
        print(f"{Colors.RED}Error viewing campaign batches: {e}{Colors.END}")
    finally:
        conn.close()

def select_campaign():
    """
    Select an existing campaign to work with.
    """
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT campaign_id, campaign_name FROM campaigns ORDER BY created_at DESC")
        campaigns = cursor.fetchall()
        
        if not campaigns:
            print(f"{Colors.YELLOW}No campaigns found in the database. Please create a campaign first.{Colors.END}")
            return
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Select a Campaign:{Colors.END}")
        print("-" * 50)
        print(f"{Colors.BOLD}{'ID':<5} {'Campaign Name':<30}{Colors.END}")
        print("-" * 50)
        
        for campaign in campaigns:
            print(f"{campaign['campaign_id']:<5} {campaign['campaign_name']:<30}")
        
        print("-" * 50)
        
        while True:
            campaign_id = input(f"{Colors.BOLD}Enter campaign ID (or 0 to cancel): {Colors.END}").strip()
            
            if campaign_id == '0':
                return
            
            try:
                campaign_id = int(campaign_id)
                cursor.execute("SELECT campaign_id, campaign_name FROM campaigns WHERE campaign_id = ?", (campaign_id,))
                campaign = cursor.fetchone()
                
                if not campaign:
                    print(f"{Colors.RED}Campaign with ID {campaign_id} not found. Please try again.{Colors.END}")
                    continue
                
                # Display campaign statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_companies,
                        SUM(CASE WHEN current_state = 'undecided' THEN 1 ELSE 0 END) as undecided,
                        SUM(CASE WHEN current_state = 'approved' THEN 1 ELSE 0 END) as approved,
                        SUM(CASE WHEN current_state = 'rejected' THEN 1 ELSE 0 END) as rejected
                    FROM companies_campaign
                    WHERE campaign_id = ?
                """, (campaign_id,))
                
                stats = cursor.fetchone()
                
                print(f"\n{Colors.BOLD}{Colors.GREEN}Campaign: {campaign['campaign_name']}{Colors.END}")
                print(f"{Colors.CYAN}Total Companies: {stats['total_companies']}{Colors.END}")
                print(f"{Colors.YELLOW}Undecided: {stats['undecided']}{Colors.END}")
                print(f"{Colors.GREEN}Approved: {stats['approved']}{Colors.END}")
                print(f"{Colors.RED}Rejected: {stats['rejected']}{Colors.END}")
                
                # Display campaign menu
                while True:
                    print("\n" + "-" * 50)
                    print(f"{Colors.BOLD}{Colors.BLUE}Campaign Actions:{Colors.END}")
                    print(f"{Colors.GREEN}1. Add More Companies{Colors.END}")
                    print(f"{Colors.GREEN}2. View Batches{Colors.END}")
                    print(f"{Colors.GREEN}3. Run Company Prospector{Colors.END}")
                    print(f"{Colors.RED}0. Back to Campaign List{Colors.END}")
                    action = input(f"{Colors.BOLD}> {Colors.END}").strip()
                    
                    if action == '1':
                        # Add more companies to the campaign
                        add_companies_to_campaign(campaign_id, campaign['campaign_name'])
                        
                        # Refresh statistics after adding companies
                        cursor.execute("""
                            SELECT 
                                COUNT(*) as total_companies,
                                SUM(CASE WHEN current_state = 'undecided' THEN 1 ELSE 0 END) as undecided,
                                SUM(CASE WHEN current_state = 'approved' THEN 1 ELSE 0 END) as approved,
                                SUM(CASE WHEN current_state = 'rejected' THEN 1 ELSE 0 END) as rejected
                            FROM companies_campaign
                            WHERE campaign_id = ?
                        """, (campaign_id,))
                        
                        stats = cursor.fetchone()
                        
                        print(f"\n{Colors.BOLD}{Colors.GREEN}Updated Campaign: {campaign['campaign_name']}{Colors.END}")
                        print(f"{Colors.CYAN}Total Companies: {stats['total_companies']}{Colors.END}")
                        print(f"{Colors.YELLOW}Undecided: {stats['undecided']}{Colors.END}")
                        print(f"{Colors.GREEN}Approved: {stats['approved']}{Colors.END}")
                        print(f"{Colors.RED}Rejected: {stats['rejected']}{Colors.END}")
                        
                    elif action == '2':
                        # View batches in this campaign
                        view_campaign_batches(campaign_id)
                    elif action == '3':
                        # Run the company prospector for this campaign
                        try:
                            # Import the run_company_prospector module
                            import importlib.util
                            
                            # Construct the path to the module
                            module_path = os.path.join(current_dir, 'run_company_prospector.py')
                            
                            # Check if the file exists
                            if not os.path.exists(module_path):
                                print(f"{Colors.RED}Error: Could not find the company prospector module at {module_path}{Colors.END}")
                                continue
                            
                            # Load the module
                            spec = importlib.util.spec_from_file_location("run_company_prospector", module_path)
                            prospector_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(prospector_module)
                            
                            # Run the company prospector directly with this campaign
                            prospector_module.run_company_prospector(campaign_id)
                            
                        except Exception as e:
                            print(f"{Colors.RED}Error running company prospector: {e}{Colors.END}")
                    elif action == '0':
                        break
                    else:
                        print(f"{Colors.RED}❌ Invalid option. Please select a valid option.{Colors.END}")
                
                break
                
            except ValueError:
                print(f"{Colors.RED}Please enter a valid campaign ID.{Colors.END}")
    
    except Error as e:
        print(f"{Colors.RED}Error selecting campaign: {e}{Colors.END}")
    finally:
        conn.close()

def run_campaign_process():
    """
    Run the campaign management process for companies.
    """
    while True:
        print("\n" + "=" * 50)
        print(f"{Colors.BOLD}{Colors.BLUE}📱 COMPANY CAMPAIGNS{Colors.END}")
        print("=" * 50)
        print("Please select an option:")
        print(f"{Colors.GREEN}1. Create New Campaign{Colors.END}")
        print(f"{Colors.GREEN}2. Select Existing Campaign{Colors.END}")
        print(f"{Colors.GREEN}3. List All Campaigns{Colors.END}")
        print(f"{Colors.RED}0. Back to Companies Menu{Colors.END}")
        option = input(f"{Colors.BOLD}> {Colors.END}").strip()

        if option == '1':
            try:
                create_campaign()
            except Exception as e:
                print(f"{Colors.RED}🚨 Error while creating campaign: {e}{Colors.END}")
        elif option == '2':
            try:
                select_campaign()
            except Exception as e:
                print(f"{Colors.RED}🚨 Error while selecting campaign: {e}{Colors.END}")
        elif option == '3':
            try:
                list_campaigns()
            except Exception as e:
                print(f"{Colors.RED}🚨 Error while listing campaigns: {e}{Colors.END}")
        elif option == '0':
            return
        else:
            print(f"{Colors.RED}❌ Invalid option. Please select a valid option.{Colors.END}")
            
if __name__ == '__main__':
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'create':
            create_campaign()
        elif command == 'select':
            select_campaign()
        elif command == 'list':
            list_campaigns()
        else:
            run_campaign_process()
    else:
        run_campaign_process()