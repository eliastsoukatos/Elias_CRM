import sys
import os
import sqlite3
from sqlite3 import Error
import time
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QWidget, QComboBox)
from PyQt5.QtCore import Qt
import warnings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Removed webdriver_manager import that was causing issues

# Suppress PyQt warnings like "QSocketNotifier: Can only be used with threads started with QThread"
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false;qt.network.*=false"

# Set up logging based on debug mode
debug_mode = os.environ.get("CRM_DEBUG", "0") == "1"
if debug_mode:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    # Filter out warnings in non-debug mode
    warnings.filterwarnings("ignore")

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
    # HARDCODED PATH FOR WINDOWS - TRY THIS FIRST
    windows_path = "C:\\Users\\EliasTsoukatos\\Documents\\software_code\\Elias_CRM\\databases\\database.db"
    print(f"{Colors.CYAN}Trying hardcoded Windows database path: {windows_path}{Colors.END}")
    
    # Try hardcoded path first
    try:
        db_dir = os.path.dirname(windows_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"{Colors.GREEN}Created hardcoded database directory{Colors.END}")
            
        conn = sqlite3.connect(windows_path)
        conn.row_factory = sqlite3.Row
        print(f"{Colors.GREEN}Successfully connected using hardcoded path{Colors.END}")
        # Set the project root for future use
        os.environ['PROJECT_ROOT'] = os.path.dirname(db_dir)
        return conn
    except Exception as e:
        print(f"{Colors.RED}Hardcoded path failed: {e}{Colors.END}")
    
    # Get project root from environment variable
    project_root = os.environ.get('PROJECT_ROOT')
    if not project_root:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    db_path = os.path.join(project_root, 'databases', 'database.db')
    print(f"{Colors.CYAN}Trying environment/calculated path: {db_path}{Colors.END}")
    
    try:
        # Ensure the database directory exists
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"{Colors.GREEN}Created database directory{Colors.END}")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        print(f"{Colors.GREEN}Successfully connected using project path{Colors.END}")
        return conn
    except Error as e:
        print(f"{Colors.RED}Error connecting to database: {e}{Colors.END}")
        
        # Try user's home directory as fallback
        try:
            user_home = os.path.expanduser("~")
            alt_db_path = os.path.join(user_home, 'databases', 'database.db')
            
            # Ensure the directory exists
            alt_db_dir = os.path.dirname(alt_db_path)
            if not os.path.exists(alt_db_dir):
                os.makedirs(alt_db_dir, exist_ok=True)
                print(f"{Colors.GREEN}Created user home database directory{Colors.END}")
            
            print(f"{Colors.YELLOW}Trying alternate database path: {alt_db_path}{Colors.END}")
            conn = sqlite3.connect(alt_db_path)
            conn.row_factory = sqlite3.Row
            print(f"{Colors.GREEN}Successfully connected using home directory path{Colors.END}")
            return conn
        except Exception as e2:
            print(f"{Colors.RED}Home directory database failed: {e2}{Colors.END}")
            
            # Final attempt for Windows - try APPDATA
            if os.name == 'nt':  # Windows
                try:
                    appdata = os.environ.get('APPDATA', '')
                    if appdata:
                        app_db_dir = os.path.join(appdata, 'Elias_CRM', 'databases')
                        if not os.path.exists(app_db_dir):
                            os.makedirs(app_db_dir, exist_ok=True)
                        app_db_path = os.path.join(app_db_dir, 'database.db')
                        print(f"{Colors.YELLOW}Trying APPDATA database path: {app_db_path}{Colors.END}")
                        conn = sqlite3.connect(app_db_path)
                        conn.row_factory = sqlite3.Row
                        print(f"{Colors.GREEN}Successfully connected using APPDATA path{Colors.END}")
                        return conn
                except Exception as e3:
                    print(f"{Colors.RED}APPDATA database failed: {e3}{Colors.END}")
        
        return None

def get_campaigns():
    """
    Get all campaigns from the database.
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT campaign_id, campaign_name 
            FROM campaigns 
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"{Colors.RED}Error fetching campaigns: {e}{Colors.END}")
        return []
    finally:
        conn.close()

def get_campaign_batches(campaign_id):
    """
    Get all batches for a specific campaign.
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                campaign_batch_tag, 
                campaign_batch_id,
                COUNT(*) as company_count
            FROM companies_campaign
            WHERE campaign_id = ?
            GROUP BY campaign_batch_tag, campaign_batch_id
            ORDER BY added_at DESC
        """, (campaign_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"{Colors.RED}Error fetching campaign batches: {e}{Colors.END}")
        return []
    finally:
        conn.close()

def get_companies_for_campaign(campaign_id, batch_id=None):
    """
    Get all companies for a specific campaign, optionally filtered by batch.
    
    Args:
        campaign_id: The ID of the campaign
        batch_id: Optional batch ID to filter by
        
    Returns:
        List of companies with their details as dictionaries (not sqlite3.Row objects)
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                cc.company_id,
                cc.current_state,
                c.name,
                c.website,
                c.headcount,
                c.revenue,
                c.founded,
                cl.country,
                cl.state,
                cl.city,
                cr.overall_rating,
                cr.review_count
            FROM companies_campaign cc
            JOIN companies c ON cc.company_id = c.company_id
            LEFT JOIN company_locations cl ON cc.company_id = cl.company_id 
                AND (cl.office_type = 'headquarters' OR cl.office_type IS NULL)
            LEFT JOIN company_ratings cr ON cc.company_id = cr.company_id
            WHERE cc.campaign_id = ?
        """
        
        params = [campaign_id]
        
        if batch_id:
            query += " AND cc.campaign_batch_id = ?"
            params.append(batch_id)
            
        query += " ORDER BY cc.added_at DESC"
        
        cursor.execute(query, params)
        
        # Convert sqlite3.Row objects to regular dictionaries so we can modify them
        rows = cursor.fetchall()
        companies = []
        for row in rows:
            company_dict = {key: row[key] for key in row.keys()}
            companies.append(company_dict)
            
        return companies
    except Error as e:
        print(f"{Colors.RED}Error fetching companies: {e}{Colors.END}")
        return []
    finally:
        conn.close()

def update_company_state(company_id, campaign_id, new_state):
    """
    Update the state of a company in a campaign.
    
    Args:
        company_id: The ID of the company
        campaign_id: The ID of the campaign
        new_state: The new state ('approved', 'rejected', or 'undecided')
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE companies_campaign
            SET current_state = ?
            WHERE company_id = ? AND campaign_id = ?
        """, (new_state, company_id, campaign_id))
        
        conn.commit()
        return True
    except Error as e:
        print(f"{Colors.RED}Error updating company state: {e}{Colors.END}")
        return False
    finally:
        conn.close()

class CompanyProspectorWindow(QMainWindow):
    def __init__(self, campaign_id, companies, parent=None):
        super().__init__(parent)
        self.campaign_id = campaign_id
        self.companies = companies
        self.current_index = 0
        self.driver = None
        self.current_tab_index = 1  # Start with index 1 (second tab)
        
        # Find first undecided company
        for i, company in enumerate(self.companies):
            if company['current_state'] == 'undecided':
                self.current_index = i
                break
        
        self.init_ui()
        self.init_browser()
        self.show_current_company()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Company Prospector")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create company info area
        info_layout = QVBoxLayout()
        
        # Add labels for company information
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        
        self.headcount_label = QLabel()
        self.revenue_label = QLabel()
        self.founded_label = QLabel()
        self.location_label = QLabel()
        self.rating_label = QLabel()
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-weight: bold;")
        
        # Add all labels to info layout
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.headcount_label)
        info_layout.addWidget(self.revenue_label)
        info_layout.addWidget(self.founded_label)
        info_layout.addWidget(self.location_label)
        info_layout.addWidget(self.rating_label)
        info_layout.addWidget(self.status_label)
        
        # Add info layout to main layout
        main_layout.addLayout(info_layout)
        
        # Add spacer
        main_layout.addStretch(1)
        
        # Create navigation buttons
        button_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("←")
        self.prev_button.setFixedSize(50, 50)
        self.prev_button.clicked.connect(self.go_to_previous)
        
        self.reject_button = QPushButton("✕")
        self.reject_button.setFixedSize(100, 50)
        self.reject_button.setStyleSheet("background-color: #ff6b6b; color: white; font-size: 20px;")
        self.reject_button.clicked.connect(self.reject_company)
        
        self.approve_button = QPushButton("♥")
        self.approve_button.setFixedSize(100, 50)
        self.approve_button.setStyleSheet("background-color: #4ecdc4; color: white; font-size: 20px;")
        self.approve_button.clicked.connect(self.approve_company)
        
        self.next_button = QPushButton("→")
        self.next_button.setFixedSize(50, 50)
        self.next_button.clicked.connect(self.go_to_next)
        
        # Add buttons to layout
        button_layout.addWidget(self.prev_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.reject_button)
        button_layout.addWidget(self.approve_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.next_button)
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
        
        # Set up counter display
        self.counter_label = QLabel()
        self.counter_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.counter_label)
        
    def init_browser(self):
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            
            # Add additional Chrome options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-features=NetworkService")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Initialize Chrome without ChromeDriverManager since it seems to be causing issues
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as chrome_error:
                if debug_mode:
                    print(f"{Colors.RED}Error initializing Chrome browser: {chrome_error}{Colors.END}")
                logging.error(f"Error initializing Chrome browser: {chrome_error}")
                # In production we would handle this better with fallbacks
                raise  # Re-raise to exit the application
            
            # Open DuckDuckGo in the first tab
            self.driver.get("https://duckduckgo.com")
            
            # Prepare to open company website in a new tab
            if self.companies and self.current_index < len(self.companies):
                company = self.companies[self.current_index]
                website = company['website']
                
                if website and website.strip():
                    # Make sure website has http/https prefix
                    if not website.startswith(('http://', 'https://')):
                        website = 'https://' + website
                    
                    try:
                        # Open the company website in a new tab
                        self.driver.execute_script(f"window.open('{website}');")
                        # Switch to the new tab
                        self.driver.switch_to.window(self.driver.window_handles[1])
                    except Exception as tab_error:
                        if debug_mode:
                            print(f"{Colors.RED}Error opening company website tab: {tab_error}{Colors.END}")
                        logging.error(f"Error opening company website tab: {tab_error}")
                        # Try Google search as fallback
                        company_name = company['name']
                        if company_name:
                            search_url = f"https://www.google.com/search?q={company_name.replace(' ', '+')}"
                            try:
                                self.driver.execute_script(f"window.open('{search_url}');")
                                self.driver.switch_to.window(self.driver.window_handles[1])
                            except Exception as search_error:
                                if debug_mode:
                                    print(f"{Colors.RED}Error opening Google search: {search_error}{Colors.END}")
                                logging.error(f"Error opening Google search: {search_error}")
        except Exception as e:
            if debug_mode:
                print(f"{Colors.RED}Error initializing browser: {e}{Colors.END}")
            logging.error(f"Error initializing browser: {e}")
    
    def show_current_company(self):
        if not self.companies or self.current_index >= len(self.companies):
            self.name_label.setText("No companies available")
            return
        
        company = self.companies[self.current_index]
        
        # Update labels with company information - handle potential None values safely
        name = company['name'] if company['name'] is not None else "Unknown"
        self.name_label.setText(f"{name}")
        
        # Get headcount
        headcount = company['headcount']
        headcount_text = str(headcount) if headcount is not None else "N/A"
        self.headcount_label.setText(f"Headcount: {headcount_text}")
        
        # Format revenue with commas for better readability if present
        revenue = company['revenue']
        if revenue is not None and revenue != "":
            try:
                revenue_int = int(revenue)
                formatted_revenue = f"${revenue_int:,}"
            except (ValueError, TypeError):
                formatted_revenue = str(revenue)
        else:
            formatted_revenue = "N/A"
            
        self.revenue_label.setText(f"Revenue: {formatted_revenue}")
        
        # Get founded year
        founded = company['founded'] if company['founded'] is not None else "N/A"
        self.founded_label.setText(f"Founded: {founded}")
        
        # Compose location - handle potential None values safely
        location_parts = []
        if company['city'] is not None and str(company['city']).strip():
            location_parts.append(str(company['city']))
        if company['state'] is not None and str(company['state']).strip():
            location_parts.append(str(company['state']))
        if company['country'] is not None and str(company['country']).strip():
            location_parts.append(str(company['country']))
        
        location = ", ".join(location_parts) if location_parts else "N/A"
        self.location_label.setText(f"Location: {location}")
        
        # Show rating - handle potential None values safely
        rating = company['overall_rating']
        review_count = company['review_count']
        
        if rating is not None and review_count is not None and rating != "" and review_count != "":
            self.rating_label.setText(f"Rating: {rating} ({review_count} reviews)")
        else:
            self.rating_label.setText("Rating: N/A")
        
        # Show status
        status_text = company['current_state'].capitalize()
        if status_text == "Approved":
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
        elif status_text == "Rejected":
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
        else:
            self.status_label.setStyleSheet("font-weight: bold; color: black;")
        
        self.status_label.setText(f"Status: {status_text}")
        
        # Update counter label
        self.counter_label.setText(f"Company {self.current_index + 1} of {len(self.companies)}")
        
        # Update browser tab
        self.update_browser_tab()
    
    def update_browser_tab(self):
        if not self.driver:
            return
            
        try:
            # Get the current company website
            company = self.companies[self.current_index]
            website = company['website']
            
            if website and website.strip():
                # Make sure website has http/https prefix
                if not website.startswith(('http://', 'https://')):
                    website = 'https://' + website
                
                # Check if we have more than 1 tab open
                if len(self.driver.window_handles) > 1:
                    # Close the company tab if it exists (keep the DuckDuckGo tab)
                    if len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[1])
                        self.driver.close()
                    
                    # Switch back to the first tab
                    self.driver.switch_to.window(self.driver.window_handles[0])
                
                # Open the new company website in a new tab
                try:
                    self.driver.execute_script(f"window.open('{website}');")
                    
                    # Switch to the new tab
                    self.driver.switch_to.window(self.driver.window_handles[1])
                except Exception as e:
                    print(f"Error opening company website: {e}")
                    # If there was an error, try with a Google search instead
                    company_name = company['name']
                    if company_name:
                        search_url = f"https://www.google.com/search?q={company_name.replace(' ', '+')}"
                        try:
                            self.driver.execute_script(f"window.open('{search_url}');")
                            self.driver.switch_to.window(self.driver.window_handles[1])
                        except Exception as e2:
                            print(f"Error opening Google search: {e2}")
        except Exception as e:
            print(f"Error updating browser tab: {e}")
    
    def go_to_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
        else:
            # If at the first company, loop around to the last company
            self.current_index = len(self.companies) - 1
        self.show_current_company()
    
    def go_to_next(self):
        if self.current_index < len(self.companies) - 1:
            self.current_index += 1
        else:
            # If at the last company, loop around to the first company
            self.current_index = 0
        self.show_current_company()
    
    def reject_company(self):
        if not self.companies or self.current_index >= len(self.companies):
            return
            
        company = self.companies[self.current_index]
        
        try:
            # Update state in database
            success = update_company_state(company['company_id'], self.campaign_id, 'rejected')
            
            if success:
                # Update in local data
                self.companies[self.current_index]['current_state'] = 'rejected'
                
                # Show updated info
                self.show_current_company()
                
                # Go to next company
                self.go_to_next()
        except Exception as e:
            if debug_mode:
                print(f"{Colors.RED}Error updating company state: {e}{Colors.END}")
            logging.error(f"Error updating company state when rejecting: {e}")
    
    def approve_company(self):
        if not self.companies or self.current_index >= len(self.companies):
            return
            
        company = self.companies[self.current_index]
        
        try:
            # Update state in database
            success = update_company_state(company['company_id'], self.campaign_id, 'approved')
            
            if success:
                # Update in local data
                self.companies[self.current_index]['current_state'] = 'approved'
                
                # Show updated info
                self.show_current_company()
                
                # Go to next company
                self.go_to_next()
        except Exception as e:
            if debug_mode:
                print(f"{Colors.RED}Error updating company state: {e}{Colors.END}")
            logging.error(f"Error updating company state when approving: {e}")
    
    def closeEvent(self, event):
        # Clean up browser when window is closed
        if self.driver:
            self.driver.quit()
        event.accept()

def run_company_prospector(pre_selected_campaign_id=None, pre_selected_batch_id=None):
    """
    Main function to run the company prospector feature.
    
    Args:
        pre_selected_campaign_id: Optional campaign ID to skip the campaign selection step
        pre_selected_batch_id: Optional batch ID to skip the batch selection step
    """
    # Get all campaigns
    campaigns = get_campaigns()
    
    if not campaigns:
        print(f"{Colors.YELLOW}No campaigns found. Please create a campaign first.{Colors.END}")
        return
    
    # If pre-selected campaign ID is provided, use it
    if pre_selected_campaign_id:
        campaign_id = pre_selected_campaign_id
        # Find selected campaign
        selected_campaign = None
        for campaign in campaigns:
            if campaign['campaign_id'] == campaign_id:
                selected_campaign = campaign
                break
        
        if not selected_campaign:
            print(f"{Colors.RED}Campaign with ID {campaign_id} not found.{Colors.END}")
            return
    else:
        # Display campaigns for selection
        print(f"\n{Colors.BOLD}{Colors.BLUE}📋 Select a Campaign:{Colors.END}")
        print("-" * 50)
        print(f"{Colors.BOLD}{'ID':<5} {'Campaign Name':<30}{Colors.END}")
        print("-" * 50)
        
        for campaign in campaigns:
            print(f"{campaign['campaign_id']:<5} {campaign['campaign_name']:<30}")
        
        print("-" * 50)
        
        # Get campaign selection
        while True:
            campaign_id = input(f"{Colors.BOLD}Enter campaign ID (or 0 to cancel): {Colors.END}").strip()
            
            if campaign_id == '0':
                return
            
            try:
                campaign_id = int(campaign_id)
                
                # Find selected campaign
                selected_campaign = None
                for campaign in campaigns:
                    if campaign['campaign_id'] == campaign_id:
                        selected_campaign = campaign
                        break
                
                if not selected_campaign:
                    print(f"{Colors.RED}Campaign with ID {campaign_id} not found. Please try again.{Colors.END}")
                    continue
                break
            except ValueError:
                print(f"{Colors.RED}Please enter a valid campaign ID.{Colors.END}")
                continue
    
    # Get batches for the selected campaign
    batches = get_campaign_batches(campaign_id)
    
    # If pre-selected batch ID is provided, use it
    if pre_selected_batch_id:
        # If the pre-selected batch is "all", load all companies
        if pre_selected_batch_id == "all":
            companies = get_companies_for_campaign(campaign_id)
            if not companies:
                print(f"{Colors.YELLOW}No companies found in this campaign.{Colors.END}")
                return
            print(f"{Colors.GREEN}Loading all {len(companies)} companies from campaign...{Colors.END}")
        else:
            # Try to find the specified batch
            found_batch = False
            for batch in batches:
                if batch['campaign_batch_id'] == pre_selected_batch_id:
                    companies = get_companies_for_campaign(campaign_id, pre_selected_batch_id)
                    if not companies:
                        print(f"{Colors.YELLOW}No companies found in this batch.{Colors.END}")
                        return
                    print(f"{Colors.GREEN}Loading {len(companies)} companies from batch {batch['campaign_batch_tag']}...{Colors.END}")
                    found_batch = True
                    break
                    
            if not found_batch:
                print(f"{Colors.RED}Batch with ID {pre_selected_batch_id} not found.{Colors.END}")
                return
    else:
        # No pre-selected batch, check if there are any batches
        if not batches:
            print(f"{Colors.YELLOW}No batches found for this campaign.{Colors.END}")
            return
                
        # Display batch selection options
        print(f"\n{Colors.BOLD}{Colors.BLUE}📋 Select a Batch or All Companies:{Colors.END}")
        print("-" * 80)
        print(f"{Colors.BOLD}{'Option':<10} {'Batch Tag':<20} {'Companies':<10} {'Batch ID':<40}{Colors.END}")
        print("-" * 80)
        
        print(f"{'0':<10} {'All Companies':<20} {'-':<10} {'-':<40}")
        
        for i, batch in enumerate(batches, 1):
            print(f"{i:<10} {batch['campaign_batch_tag']:<20} {batch['company_count']:<10} {batch['campaign_batch_id']:<40}")
        
        print("-" * 80)
        
        # Get batch selection
        while True:
            batch_choice = input(f"{Colors.BOLD}Enter option number (or c to cancel): {Colors.END}").strip()
            
            if batch_choice.lower() == 'c':
                return
            
            try:
                batch_choice = int(batch_choice)
                
                if batch_choice == 0:
                    # All companies in campaign
                    companies = get_companies_for_campaign(campaign_id)
                    
                    if not companies:
                        print(f"{Colors.YELLOW}No companies found in this campaign.{Colors.END}")
                        continue
                    
                    print(f"{Colors.GREEN}Loading all {len(companies)} companies from campaign...{Colors.END}")
                    break
                elif 1 <= batch_choice <= len(batches):
                    # Specific batch
                    selected_batch = batches[batch_choice - 1]
                    companies = get_companies_for_campaign(campaign_id, selected_batch['campaign_batch_id'])
                    
                    if not companies:
                        print(f"{Colors.YELLOW}No companies found in this batch.{Colors.END}")
                        continue
                    
                    print(f"{Colors.GREEN}Loading {len(companies)} companies from batch {selected_batch['campaign_batch_tag']}...{Colors.END}")
                    break
                else:
                    print(f"{Colors.RED}Invalid option. Please select a valid option.{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Please enter a valid option number.{Colors.END}")
    
    # Launch PyQt application with error handling
    try:
        # Override sys.excepthook to prevent PyQt from printing error messages
        def custom_excepthook(exctype, value, traceback):
            if debug_mode:
                # Only print tracebacks in debug mode
                sys.__excepthook__(exctype, value, traceback)
            else:
                # In normal mode, just log the exception
                logging.error(f"Uncaught exception: {value}")
        
        # Set custom exception handler
        sys.excepthook = custom_excepthook
        
        # We need sys.argv to be populated for PyQt
        app = QApplication(sys.argv) 
        window = CompanyProspectorWindow(campaign_id, companies)
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        if debug_mode:
            print(f"{Colors.RED}Error launching application: {e}{Colors.END}")
            print(f"{Colors.YELLOW}This may be due to issues with PyQt5 or Selenium. Please check your installation.{Colors.END}")
        logging.error(f"Error launching PyQt application: {e}")
        print("Error occurred when launching the Company Prospector.")
        print("Run with './setup.sh --debug' to see detailed error information.")
        input("Press Enter to continue...")

if __name__ == "__main__":
    # Check if a campaign ID was provided as an argument
    if len(sys.argv) > 1:
        campaign_id = int(sys.argv[1])
        
        # Check if a batch ID was also provided
        if len(sys.argv) > 2:
            batch_id = sys.argv[2]
            run_company_prospector(campaign_id, batch_id)
        else:
            # No batch ID provided, use "all" as default
            run_company_prospector(campaign_id, "all")
    else:
        # No arguments provided, run with interactive mode
        run_company_prospector()