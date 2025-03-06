import os
import sys
import uuid
import importlib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QLabel, QHBoxLayout, 
                           QGroupBox, QStackedWidget, QMessageBox,
                           QLineEdit, QSpinBox, QCheckBox, QListWidget, QListWidgetItem,
                           QFormLayout, QDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap

# Add phone_dialer directory to path
phone_dialer_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phone_dialer')
if phone_dialer_dir not in sys.path:
    sys.path.insert(0, phone_dialer_dir)

# Add necessary directories to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
companies_dir = os.path.join(current_dir, 'companies')
src_companies_dir = os.path.join(companies_dir, 'src_companies')
contacts_dir = os.path.join(current_dir, 'contacts')
cognism_dir = os.path.join(contacts_dir, 'cognism_scraper')

# Add directories to the path
for path in [companies_dir, src_companies_dir, contacts_dir, cognism_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import necessary modules
from db_initializer import check_for_database
from migrate_social_links import migrate_social_links
from clean_verifications import clean_verification_records
from clean_ratings import clean_rating_records


def initialize_app():
    """Initialize the application by setting up the database and migrations."""
    print("🔧 Initializing application...")
    
    # Check and initialize database if needed
    db_initialized = check_for_database()
    if not db_initialized:
        print("❌ Database initialization failed.")
        return
    
    # Initialize contacts database tables
    try:
        # Import the contacts table creation function
        sys.path.append(os.path.join(os.path.dirname(__file__), 'contacts', 'cognism_scraper', 'src', 'utils'))
        from create_database import create_table
        create_table()
        print("✅ Contacts database tables created successfully")
    except Exception as e:
        print(f"⚠️ Contacts database initialization warning: {e}")
    
    # Run social links migration silently
    try:
        migrate_social_links()
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")
        
    # Clean up empty verification records silently
    try:
        clean_verification_records()
    except Exception as e:
        print(f"⚠️ Verification cleanup warning: {e}")
        
    # Clean up empty rating records silently
    try:
        clean_rating_records()
    except Exception as e:
        print(f"⚠️ Rating cleanup warning: {e}")
    
    print("🚀 Application initialized successfully!")
    
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("CRM System")
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        header_label = QLabel("CRM SYSTEM")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        main_layout.addWidget(header_label)
        
        # Create stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create all screens first
        self.main_menu_screen = self.create_main_menu()
        self.companies_menu_screen = self.create_companies_menu()
        self.sourcing_menu_screen = self.create_sourcing_menu()
        self.scraper_selector_screen = self.create_scraper_selector()
        self.clutch_scraper_screen = self.create_clutch_scraper_config()
        self.campaigns_menu_screen = self.create_campaigns_menu()
        
        # Create campaign screens
        self.create_campaign_screen = self.create_campaign_creation_screen()
        self.select_campaign_screen = self.create_campaign_selection_screen()
        
        # Create contacts module screens
        self.contacts_menu_screen = self.create_contacts_menu()
        self.contacts_sourcing_menu_screen = self.create_contacts_sourcing_menu()
        self.contacts_scraper_selector_screen = self.create_contacts_scraper_selector()
        self.cognism_scraper_options_screen = self.create_cognism_scraper_options()
        self.cognism_login_screen = self.create_cognism_login_screen()
        
        # Create contacts campaign screens
        self.contacts_campaigns_menu_screen = self.create_contacts_campaigns_menu()
        
        # Create phone dialer screen
        self.phone_dialer_screen = self.create_phone_dialer_screen()
        
        # Create a container for the CSV import widget
        self.csv_import_container = QWidget()
        csv_layout = QVBoxLayout(self.csv_import_container)
        self.csv_layout = csv_layout  # Keep reference for later
        
        back_button = QPushButton("Back to Sourcing Menu")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.SOURCING_MENU))
        csv_layout.addWidget(back_button)
        
        # Define screen indices as class constants
        self.MAIN_MENU = 0
        self.COMPANIES_MENU = 1
        self.SOURCING_MENU = 2
        self.CAMPAIGNS_MENU = 3
        self.SCRAPER_SELECTOR = 4
        self.CLUTCH_SCRAPER = 5
        self.CSV_IMPORT = 6
        self.CREATE_CAMPAIGN = 7
        self.SELECT_CAMPAIGN = 8
        self.CONTACTS_MENU = 9
        self.CONTACTS_SOURCING_MENU = 10
        self.CONTACTS_SCRAPER_SELECTOR = 11
        self.COGNISM_SCRAPER_OPTIONS = 12
        self.COGNISM_LOGIN_SCREEN = 13
        self.CONTACTS_CAMPAIGNS_MENU = 14
        self.PHONE_DIALER = 15
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.main_menu_screen)                  # index 0
        self.stacked_widget.addWidget(self.companies_menu_screen)             # index 1
        self.stacked_widget.addWidget(self.sourcing_menu_screen)              # index 2
        self.stacked_widget.addWidget(self.campaigns_menu_screen)             # index 3
        self.stacked_widget.addWidget(self.scraper_selector_screen)           # index 4
        self.stacked_widget.addWidget(self.clutch_scraper_screen)             # index 5
        self.stacked_widget.addWidget(self.csv_import_container)              # index 6
        self.stacked_widget.addWidget(self.create_campaign_screen)            # index 7
        self.stacked_widget.addWidget(self.select_campaign_screen)            # index 8
        self.stacked_widget.addWidget(self.contacts_menu_screen)              # index 9
        self.stacked_widget.addWidget(self.contacts_sourcing_menu_screen)     # index 10
        self.stacked_widget.addWidget(self.contacts_scraper_selector_screen)  # index 11
        self.stacked_widget.addWidget(self.cognism_scraper_options_screen)    # index 12
        self.stacked_widget.addWidget(self.cognism_login_screen)              # index 13
        self.stacked_widget.addWidget(self.contacts_campaigns_menu_screen)    # index 14
        self.stacked_widget.addWidget(self.phone_dialer_screen)               # index 15
        
        # Show the main menu
        self.stacked_widget.setCurrentIndex(self.MAIN_MENU)
        
    def create_main_menu(self):
        """Create the main menu screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create menu options
        menu_group = QGroupBox("MAIN MENU")
        menu_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        
        # Companies button
        companies_button = QPushButton("Companies")
        companies_button.setStyleSheet("font-size: 16px; padding: 15px;")
        companies_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.COMPANIES_MENU))
        menu_layout.addWidget(companies_button)
        
        # Contacts button
        contacts_button = QPushButton("Contacts")
        contacts_button.setStyleSheet("font-size: 16px; padding: 15px;")
        contacts_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_MENU))
        menu_layout.addWidget(contacts_button)
        
        # Phone Dialer button
        phone_dialer_button = QPushButton("Phone Dialer")
        phone_dialer_button.setStyleSheet("font-size: 16px; padding: 15px;")
        phone_dialer_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.PHONE_DIALER))
        menu_layout.addWidget(phone_dialer_button)
        
        # Exit button
        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("font-size: 16px; padding: 15px;")
        exit_button.clicked.connect(self.close)
        menu_layout.addWidget(exit_button)
        
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        
        return widget
    
    def create_companies_menu(self):
        """Create the companies menu screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create menu options
        menu_group = QGroupBox("COMPANIES MODULE")
        menu_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        
        # Sourcing button
        sourcing_button = QPushButton("Sourcing")
        sourcing_button.setStyleSheet("font-size: 16px; padding: 15px;")
        sourcing_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.SOURCING_MENU))
        menu_layout.addWidget(sourcing_button)
        
        # Campaigns button
        campaigns_button = QPushButton("Campaigns")
        campaigns_button.setStyleSheet("font-size: 16px; padding: 15px;")
        campaigns_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CAMPAIGNS_MENU))
        menu_layout.addWidget(campaigns_button)
        
        # View button (coming soon)
        view_button = QPushButton("View (Coming Soon)")
        view_button.setStyleSheet("font-size: 16px; padding: 15px;")
        view_button.setEnabled(False)
        menu_layout.addWidget(view_button)
        
        # Back button
        back_button = QPushButton("Back to Main Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.MAIN_MENU))
        menu_layout.addWidget(back_button)
        
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        
        return widget
    
    def create_sourcing_menu(self):
        """Create the company sourcing menu screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create menu options
        menu_group = QGroupBox("COMPANY SOURCING")
        menu_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        
        # Select Scraper button
        scraper_button = QPushButton("Select Scraper")
        scraper_button.setStyleSheet("font-size: 16px; padding: 15px;")
        scraper_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.SCRAPER_SELECTOR))
        menu_layout.addWidget(scraper_button)
        
        # Import CSV button
        csv_button = QPushButton("Import CSV File")
        csv_button.setStyleSheet("font-size: 16px; padding: 15px;")
        csv_button.clicked.connect(self.run_csv_import)
        menu_layout.addWidget(csv_button)
        
        # Execute Data Query button
        query_button = QPushButton("Execute Data Query (Coming Soon)")
        query_button.setStyleSheet("font-size: 16px; padding: 15px;")
        query_button.setEnabled(False)
        menu_layout.addWidget(query_button)
        
        # Back button
        back_button = QPushButton("Back to Companies Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.COMPANIES_MENU))
        menu_layout.addWidget(back_button)
        
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        
        return widget
    
    def create_campaigns_menu(self):
        """Create the company campaigns menu screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create menu options
        menu_group = QGroupBox("COMPANY CAMPAIGNS")
        menu_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        
        # Create New Campaign button
        create_button = QPushButton("Create New Campaign")
        create_button.setStyleSheet("font-size: 16px; padding: 15px;")
        create_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CREATE_CAMPAIGN))
        menu_layout.addWidget(create_button)
        
        # Select Existing Campaign button
        select_button = QPushButton("Select Existing Campaign")
        select_button.setStyleSheet("font-size: 16px; padding: 15px;")
        select_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.SELECT_CAMPAIGN))
        menu_layout.addWidget(select_button)
        
        # Run Company Prospector button
        prospector_button = QPushButton("Run Company Prospector")
        prospector_button.setStyleSheet("font-size: 16px; padding: 15px;")
        prospector_button.clicked.connect(self.run_company_prospector)
        menu_layout.addWidget(prospector_button)
        
        # Back button
        back_button = QPushButton("Back to Companies Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.COMPANIES_MENU))
        menu_layout.addWidget(back_button)
        
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        
        return widget
    
    def create_scraper_selector(self):
        """Create the scraper selector screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("Available Scrapers")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Scrapers group
        scrapers_group = QGroupBox("Select a Scraper")
        scrapers_layout = QVBoxLayout()
        
        # Clutch Scraper button
        clutch_button = QPushButton("Clutch Scraper")
        clutch_button.setStyleSheet("font-size: 16px; padding: 20px;")
        clutch_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CLUTCH_SCRAPER))
        scrapers_layout.addWidget(clutch_button)
        
        # Future scrapers (disabled)
        goodfirms_button = QPushButton("GoodFirms Scraper (Coming Soon)")
        goodfirms_button.setStyleSheet("font-size: 16px; padding: 20px;")
        goodfirms_button.setEnabled(False)
        scrapers_layout.addWidget(goodfirms_button)
        
        linkedin_button = QPushButton("LinkedIn Scraper (Coming Soon)")
        linkedin_button.setStyleSheet("font-size: 16px; padding: 20px;")
        linkedin_button.setEnabled(False)
        scrapers_layout.addWidget(linkedin_button)
        
        twitter_button = QPushButton("Twitter Scraper (Coming Soon)")
        twitter_button.setStyleSheet("font-size: 16px; padding: 20px;")
        twitter_button.setEnabled(False)
        scrapers_layout.addWidget(twitter_button)
        
        scrapers_group.setLayout(scrapers_layout)
        layout.addWidget(scrapers_group)
        
        # Back button
        back_button = QPushButton("Back to Sourcing Menu")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.SOURCING_MENU))
        layout.addWidget(back_button)
        
        return widget
        
    def create_clutch_scraper_config(self):
        """Create the clutch scraper configuration screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("Clutch Scraper Configuration")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Create form for parameters
        form_group = QGroupBox("Scraper Parameters")
        form_layout = QFormLayout()
        
        # Number of companies
        self.companies_spin = QSpinBox()
        self.companies_spin.setMinimum(1)
        self.companies_spin.setMaximum(50000)  # Increased to 50,000 as requested
        self.companies_spin.setValue(10)
        form_layout.addRow("Number of companies to extract:", self.companies_spin)
        
        # Extract portfolio
        self.portfolio_check = QCheckBox()
        self.portfolio_check.setChecked(True)
        form_layout.addRow("Extract portfolio:", self.portfolio_check)
        
        # Extract reviews
        self.reviews_check = QCheckBox()
        self.reviews_check.setChecked(True)
        form_layout.addRow("Extract reviews:", self.reviews_check)
        
        # Number of reviews
        self.reviews_spin = QSpinBox()
        self.reviews_spin.setMinimum(0)
        self.reviews_spin.setMaximum(100)
        self.reviews_spin.setValue(5)
        form_layout.addRow("Number of reviews per company:", self.reviews_spin)
        
        # Batch tag
        self.batch_tag = QLineEdit()
        self.batch_tag.setText("clutch_scrape")
        form_layout.addRow("Batch tag:", self.batch_tag)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # URL list group
        url_group = QGroupBox("URLs to Scrape")
        url_layout = QVBoxLayout()
        
        self.url_list = QListWidget()
        url_layout.addWidget(self.url_list)
        
        # Add URL input
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL (e.g., https://clutch.co/web-developers)")
        url_input_layout.addWidget(self.url_input)
        
        add_button = QPushButton("Add URL")
        add_button.clicked.connect(self.add_url)
        url_input_layout.addWidget(add_button)
        
        url_layout.addLayout(url_input_layout)
        
        # Add remove button
        remove_button = QPushButton("Remove Selected URL")
        remove_button.clicked.connect(self.remove_url)
        url_layout.addWidget(remove_button)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Add default Clutch URL as an example
        self.url_list.addItem("https://clutch.co/web-developers")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        back_button = QPushButton("Back to Scraper Selection")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.SCRAPER_SELECTOR))
        button_layout.addWidget(back_button)
        
        run_button = QPushButton("Run Scraper")
        run_button.clicked.connect(self.run_clutch_scraper)
        run_button.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(run_button)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def add_url(self):
        """Add URL to the list"""
        url = self.url_input.text().strip()
        if url:
            if url.startswith("http://") or url.startswith("https://"):
                self.url_list.addItem(url)
                self.url_input.clear()
            else:
                QMessageBox.warning(self, "Invalid URL", "URL must start with http:// or https://")
    
    def remove_url(self):
        """Remove selected URL from the list"""
        selected_items = self.url_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            row = self.url_list.row(item)
            self.url_list.takeItem(row)
    
    def run_clutch_scraper(self):
        """Run the Clutch scraper with the configured parameters"""
        try:
            # Check database first
            from db_initializer import check_for_database
            if not check_for_database():
                QMessageBox.critical(self, "Error", "Database not found or initialization failed.")
                return
            
            # Get parameters
            params = {
                "num_companies": self.companies_spin.value(),
                "extract_portfolio": self.portfolio_check.isChecked(),
                "extract_reviews": self.reviews_check.isChecked(),
                "num_reviews": self.reviews_spin.value(),
                "batch_tag": self.batch_tag.text(),
                "batch_id": str(uuid.uuid4())
            }
            
            # Get URLs
            urls = []
            for i in range(self.url_list.count()):
                urls.append(self.url_list.item(i).text())
            params["urls"] = urls
            
            # Validate parameters
            if not urls:
                QMessageBox.warning(self, "No URLs", "Please add at least one URL to scrape.")
                return
            
            if not params["batch_tag"]:
                QMessageBox.warning(self, "No Batch Tag", "Please enter a batch tag.")
                return
            
            # Confirm scraper execution
            confirm_msg = f"""
            Please confirm the following settings:
            
            - Companies to extract: {params['num_companies']}
            - Extract portfolio: {params['extract_portfolio']}
            - Extract reviews: {params['extract_reviews']}
            - Reviews per company: {params['num_reviews']}
            - Batch tag: {params['batch_tag']}
            - URLs: {', '.join(params['urls'])}
            
            Proceed with scraping?
            """
            
            confirm = QMessageBox.question(self, "Confirm Scraper Settings", confirm_msg, 
                                        QMessageBox.Yes | QMessageBox.No)
            
            if confirm == QMessageBox.Yes:
                # Launch scraper as a separate process
                import subprocess
                
                # Store the current directory
                original_dir = os.getcwd()
                
                try:
                    # Create a temporary script to run the scraper
                    temp_script = os.path.join(companies_dir, 'temp_clutch_scraper.py')
                    
                    # Write a script to run the scraper with our parameters
                    with open(temp_script, 'w') as f:
                        f.write(f"""
import sys
import os

# Set up path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_companies_dir = os.path.join(current_dir, 'src_companies')
if src_companies_dir not in sys.path:
    sys.path.insert(0, src_companies_dir)

# Set up project root path for database access
project_root = os.path.dirname(os.path.dirname(current_dir))
os.environ['PROJECT_ROOT'] = project_root

# Import the scraper
from clutch_scraper import run_clutch_scraper

# Run the scraper with the specified parameters
run_clutch_scraper(
    startUrls={params['urls']},
    maxItems={params['num_companies']},
    excludePortfolio={not params['extract_portfolio']},
    includeReviews={params['extract_reviews']},
    maxReviewsPerCompany={params['num_reviews']},
    batch_tag="{params['batch_tag']}",
    batch_id="{params['batch_id']}"
)

# Show completion message
print("\\nScraper completed successfully!")
print("Batch ID: {params['batch_id']}")
input("Press Enter to continue...")
                        """)
                    
                    # Change to the companies directory
                    os.chdir(companies_dir)
                    
                    # Execute the script in a new process
                    subprocess.Popen([sys.executable, temp_script])
                    
                    # Show progress message
                    QMessageBox.information(self, "Scraper Running", 
                                         "The scraper is running in the background.\n\n"
                                         "Please check the terminal window for progress updates.")
                    
                finally:
                    # Change back to the original directory
                    os.chdir(original_dir)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running scraper: {str(e)}")
    
    def run_csv_import(self):
        """Run the CSV import tool"""
        try:
            # Launch CSV import GUI as a separate process
            import subprocess
            
            # Store the current directory
            original_dir = os.getcwd()
            
            try:
                # Create a temporary script to run the CSV import GUI
                temp_script = os.path.join(companies_dir, 'run_csv_import.py')
                
                # Write a simple script to run the CSV import GUI
                with open(temp_script, 'w') as f:
                    f.write("""
import sys
import os

# Set up path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_companies_dir = os.path.join(current_dir, 'src_companies')
if src_companies_dir not in sys.path:
    sys.path.insert(0, src_companies_dir)

# Set up project root path for database access
project_root = os.path.dirname(os.path.dirname(current_dir))
os.environ['PROJECT_ROOT'] = project_root

# Run the CSV import GUI
from src_companies.csv_import_gui import run_csv_import_gui
run_csv_import_gui()
                    """)
                
                # Change to the companies directory
                os.chdir(companies_dir)
                
                # Execute the script
                subprocess.Popen([sys.executable, temp_script])
                
            finally:
                # Change back to the original directory
                os.chdir(original_dir)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running CSV import: {str(e)}")
    
    def create_campaign_creation_screen(self):
        """Create the campaign creation screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("Create New Campaign")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Form group
        form_group = QGroupBox("Campaign Details")
        form_layout = QFormLayout()
        
        # Campaign name
        self.campaign_name_input = QLineEdit()
        self.campaign_name_input.setPlaceholderText("Enter a unique campaign name")
        form_layout.addRow("Campaign Name:", self.campaign_name_input)
        
        # SQL Query (using QPlainTextEdit for better support for pasting and code)
        from PyQt5.QtWidgets import QPlainTextEdit
        self.campaign_query_input = QPlainTextEdit()
        self.campaign_query_input.setPlaceholderText("e.g., SELECT company_id FROM companies WHERE headcount > 50")
        self.campaign_query_input.setMinimumHeight(100)     # Provide some space for multi-line queries
        form_layout.addRow("SQL Query:", self.campaign_query_input)
        
        # Query help text
        query_help = QLabel("Query must return company_id field. You can filter companies based on any criteria.")
        query_help.setWordWrap(True)
        query_help.setStyleSheet("color: #666; font-size: 12px;")
        form_layout.addRow("", query_help)
        
        # Number of companies to add
        self.company_count_input = QSpinBox()
        self.company_count_input.setMinimum(0)
        self.company_count_input.setMaximum(10000)
        self.company_count_input.setValue(0)
        self.company_count_input.setToolTip("Enter 0 to add all companies matching the query")
        form_layout.addRow("Number of Companies (0 for all):", self.company_count_input)
        
        # Batch tag
        self.campaign_batch_tag = QLineEdit()
        self.campaign_batch_tag.setText("initial")
        form_layout.addRow("Batch Tag:", self.campaign_batch_tag)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        back_button = QPushButton("Back to Campaigns Menu")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CAMPAIGNS_MENU))
        button_layout.addWidget(back_button)
        
        button_layout.addStretch()
        
        create_button = QPushButton("Create Campaign")
        create_button.clicked.connect(self.create_campaign)
        create_button.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(create_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def create_campaign_selection_screen(self):
        """Create the campaign selection screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("Select Existing Campaign")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Campaign list
        list_group = QGroupBox("Available Campaigns")
        list_layout = QVBoxLayout()
        
        self.campaign_list = QListWidget()
        self.campaign_list.setStyleSheet("font-size: 14px;")
        self.campaign_list.setMinimumHeight(200)
        list_layout.addWidget(self.campaign_list)
        
        # Refresh button for campaign list
        refresh_button = QPushButton("Refresh Campaign List")
        refresh_button.clicked.connect(self.refresh_campaign_list)
        list_layout.addWidget(refresh_button)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Campaign details group
        details_group = QGroupBox("Campaign Actions")
        details_layout = QVBoxLayout()
        
        # Action buttons
        add_companies_button = QPushButton("Add Companies to Campaign")
        add_companies_button.clicked.connect(self.add_companies_to_campaign)
        add_companies_button.setEnabled(False)
        details_layout.addWidget(add_companies_button)
        
        view_batches_button = QPushButton("View Campaign Batches")
        view_batches_button.clicked.connect(self.view_campaign_batches)
        view_batches_button.setEnabled(False)
        details_layout.addWidget(view_batches_button)
        
        run_prospector_button = QPushButton("Run Company Prospector for Campaign")
        run_prospector_button.clicked.connect(self.run_campaign_prospector)
        run_prospector_button.setEnabled(False)
        details_layout.addWidget(run_prospector_button)
        
        # Store buttons for enabling/disabling
        self.campaign_action_buttons = [
            add_companies_button,
            view_batches_button,
            run_prospector_button
        ]
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        back_button = QPushButton("Back to Campaigns Menu")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CAMPAIGNS_MENU))
        button_layout.addWidget(back_button)
        
        layout.addLayout(button_layout)
        
        # Connect selection change
        self.campaign_list.itemSelectionChanged.connect(self.on_campaign_selected)
        
        # Refresh the list initially
        self.refresh_campaign_list()
        
        return widget
    
    def create_campaign(self):
        """Create a new campaign"""
        # Import QMessageBox at the beginning of the method to avoid the UnboundLocalError
        from PyQt5.QtWidgets import QMessageBox
        
        # Get input values
        campaign_name = self.campaign_name_input.text().strip()
        campaign_query = self.campaign_query_input.toPlainText().strip()  # Use toPlainText() for QTextEdit
        batch_tag = self.campaign_batch_tag.text().strip()
        num_companies_requested = self.company_count_input.value()
        
        # Validate input
        if not campaign_name:
            QMessageBox.warning(self, "Missing Information", "Please enter a campaign name.")
            return
            
        if not campaign_query:
            QMessageBox.warning(self, "Missing Information", "Please enter an SQL query.")
            return
            
        if not batch_tag:
            batch_tag = "initial"  # Default value
        
        try:
            # First, test the query to see if it returns results
            import sqlite3
            
            # Connect to database directly
            db_path = "/home/eliastsoukatos/Documents/Python/CRM/databases/database.db"
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.cursor()
            try:
                # Test the query to get result count
                cursor.execute(campaign_query)
                results = cursor.fetchall()
                
                if not results:
                    QMessageBox.warning(self, "Query Error", "This query returned 0 results.")
                    conn.close()
                    return
                
                # Check if company_id is in results
                if 'company_id' not in dict(results[0]):
                    QMessageBox.warning(self, "Query Error", "Query results must include company_id field.")
                    conn.close()
                    return
                
                total_results = len(results)
                
                # Adjust company count if needed
                if num_companies_requested == 0 or num_companies_requested > total_results:
                    num_companies = total_results
                else:
                    num_companies = num_companies_requested
                
                # Confirm with user
                from PyQt5.QtWidgets import QMessageBox
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Question)
                msg.setText(f"Create campaign with {num_companies} companies?")
                msg.setInformativeText(f"Query found {total_results} matching companies. Proceed with creating the campaign?")
                msg.setWindowTitle("Confirm Campaign Creation")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                if msg.exec_() != QMessageBox.Yes:
                    conn.close()
                    return
                
                conn.close()
                
                # Launch campaign creation
                import subprocess
                import tempfile
                
                # Store the current directory
                original_dir = os.getcwd()
                
                try:
                    # Create a temporary script to run the campaign creation with our parameters
                    fd, temp_script = tempfile.mkstemp(suffix='.py')
                    os.close(fd)
                    
                    # Write a script to create the campaign non-interactively
                    with open(temp_script, 'w') as f:
                        f.write(f"""
import sys
import os
import sqlite3
from sqlite3 import Error
import datetime
import uuid

# Set up path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Directly use absolute database path
DB_PATH = "/home/eliastsoukatos/Documents/Python/CRM/databases/database.db"

def get_db_connection():
    try:
        print(f"Connecting to database at: {{DB_PATH}}")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(f"Error connecting to database: {{e}}")
        return None

def create_campaign():
    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        return False
    
    try:
        campaign_name = "{campaign_name}"
        query = "{campaign_query}"
        campaign_batch_tag = "{batch_tag}"
        num_companies_requested = {num_companies}
        
        # Check if campaign name already exists
        cursor = conn.cursor()
        cursor.execute("SELECT campaign_id FROM campaigns WHERE campaign_name = ?", (campaign_name,))
        if cursor.fetchone():
            print(f"A campaign with name '{{campaign_name}}' already exists.")
            return False
        
        # Test the query
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            
            if not results:
                print("Query returned 0 results.")
                return False
            
            # Check if company_id is in results
            if 'company_id' not in dict(results[0]):
                print("Query results must include company_id field.")
                return False
                
            # Get total results and limit to requested number
            companies_to_add = results[:num_companies_requested]
            
            # Generate a unique campaign batch ID
            campaign_batch_id = str(uuid.uuid4())
            
            # Save the campaign to the database
            cursor.execute(
                "INSERT INTO campaigns (campaign_name, query) VALUES (?, ?)",
                (campaign_name, query)
            )
            campaign_id = cursor.lastrowid
            
            # Insert companies into companies_campaign table with batch information
            added_count = 0
            for company in companies_to_add:
                try:
                    cursor.execute(
                        \"\"\"INSERT INTO companies_campaign 
                           (company_id, campaign_id, campaign_name, 
                            campaign_batch_tag, campaign_batch_id) 
                           VALUES (?, ?, ?, ?, ?)\"\"\",
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
                (campaign_batch_tag, campaign_batch_id, f"Campaign: {{campaign_name}}", timestamp)
            )
            
            conn.commit()
            print(f"Campaign '{{campaign_name}}' created successfully with {{added_count}} companies!")
            print(f"Batch Tag: {{campaign_batch_tag}}")
            print(f"Batch ID: {{campaign_batch_id}}")
            return True
            
        except Error as e:
            print(f"Error in SQL query: {{e}}")
            return False
        
    except Error as e:
        conn.rollback()
        print(f"Error creating campaign: {{e}}")
        return False
    finally:
        conn.close()

# Create the campaign
success = create_campaign()
print(f"Campaign creation result: {{success}}")

# Keep window open for viewing results
input("Press Enter to continue...")
                        """)
                    
                    # Change to the companies directory
                    os.chdir(companies_dir)
                    
                    # Execute the script with environment
                    env = os.environ.copy()
                    env['PROJECT_ROOT'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    process = subprocess.Popen([sys.executable, temp_script], env=env)
                    
                    # Show a message
                    QMessageBox.information(
                        self, 
                        "Campaign Creation", 
                        f"Creating campaign '{campaign_name}' with {num_companies} companies...\n\nPlease check the terminal window for results."
                    )
                    
                    # Clear the form
                    self.campaign_name_input.clear()
                    self.campaign_query_input.clear()
                    self.company_count_input.setValue(0)
                    self.campaign_batch_tag.setText("initial")
                    
                finally:
                    # Change back to the original directory
                    os.chdir(original_dir)
                    # Clean up temp file after execution
                    try:
                        os.unlink(temp_script)
                    except:
                        pass
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error in campaign creation script: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error testing query: {str(e)}")
    
    def refresh_campaign_list(self):
        """Refresh the campaign list"""
        try:
            # Get database connection
            import sqlite3
            import os
            
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, 'databases', 'database.db')
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get campaigns
            cursor.execute("""
                SELECT c.campaign_id, c.campaign_name, 
                       COUNT(cc.company_id) as total_companies,
                       c.created_at
                FROM campaigns c
                LEFT JOIN companies_campaign cc ON c.campaign_id = cc.campaign_id
                GROUP BY c.campaign_id
                ORDER BY c.created_at DESC
            """)
            
            campaigns = cursor.fetchall()
            
            # Clear the list
            self.campaign_list.clear()
            
            # Add campaigns to list
            for campaign in campaigns:
                item_text = f"{campaign['campaign_id']}: {campaign['campaign_name']} - {campaign['total_companies']} companies"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, campaign['campaign_id'])  # Store campaign ID
                self.campaign_list.addItem(item)
            
            # Disable action buttons
            for button in self.campaign_action_buttons:
                button.setEnabled(False)
            
            # Close connection
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error refreshing campaign list: {str(e)}")
    
    def on_campaign_selected(self):
        """Handle campaign selection"""
        # Enable action buttons when a campaign is selected
        selected_items = self.campaign_list.selectedItems()
        for button in self.campaign_action_buttons:
            button.setEnabled(len(selected_items) > 0)
    
    def add_companies_to_campaign(self):
        """Add companies to the selected campaign"""
        # Get selected campaign
        selected_items = self.campaign_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        campaign_id = item.data(Qt.UserRole)
        campaign_name = item.text().split(":", 1)[1].split("-")[0].strip()
        
        # Create a dialog for SQL query input
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add Companies to Campaign: {campaign_name}")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # SQL Query input
        query_label = QLabel("SQL Query (must return company_id field):")
        layout.addWidget(query_label)
        
        # Use QPlainTextEdit instead which is better for code and pasting
        from PyQt5.QtWidgets import QPlainTextEdit
        query_input = QPlainTextEdit()
        query_input.setPlaceholderText("e.g., SELECT company_id FROM companies WHERE headcount > 50")
        query_input.setMinimumHeight(100)
        layout.addWidget(query_input)
        
        # Example query help
        query_help = QLabel("Example: SELECT company_id FROM companies WHERE industry = 'Technology'")
        query_help.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(query_help)
        
        # Number of companies to add
        num_companies_layout = QHBoxLayout()
        num_companies_label = QLabel("Number of companies to add (0 for all):")
        num_companies_input = QSpinBox()
        num_companies_input.setMinimum(0)
        num_companies_input.setMaximum(10000)
        num_companies_input.setValue(0)
        num_companies_layout.addWidget(num_companies_label)
        num_companies_layout.addWidget(num_companies_input)
        layout.addLayout(num_companies_layout)
        
        # Batch tag
        batch_layout = QHBoxLayout()
        batch_label = QLabel("Batch Tag:")
        batch_input = QLineEdit("additional")
        batch_layout.addWidget(batch_label)
        batch_layout.addWidget(batch_input)
        layout.addLayout(batch_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        add_button = QPushButton("Add Companies")
        add_button.clicked.connect(dialog.accept)
        add_button.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(add_button)
        layout.addLayout(button_layout)
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # Get user input (use plainText() for QPlainTextEdit)
            query = query_input.toPlainText().strip()
            num_companies = num_companies_input.value()
            batch_tag = batch_input.text().strip()
            
            # Validate input
            if not query:
                QMessageBox.warning(self, "Missing Information", "Please enter an SQL query.")
                return
                
            if not batch_tag:
                batch_tag = "additional"  # Default value
            
            try:
                # Launch campaign addition as a separate process
                import subprocess
                
                # Store the current directory
                original_dir = os.getcwd()
                
                try:
                    # Change to the companies directory
                    os.chdir(companies_dir)
                    
                    # Create a script to add companies to the campaign
                    import tempfile
                    fd, temp_script = tempfile.mkstemp(suffix='.py')
                    os.close(fd)
                    
                    with open(temp_script, 'w') as f:
                        f.write(f"""
import sys
import os
import sqlite3
import uuid
import datetime

# Set up path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up project root path for database access
project_root = os.path.dirname(os.path.dirname(current_dir))
os.environ['PROJECT_ROOT'] = project_root

# Directly use absolute database path
DB_PATH = "/home/eliastsoukatos/Documents/Python/CRM/databases/database.db"

def get_db_connection():
    try:
        print(f"Connecting to database at: {{DB_PATH}}")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to database: {{e}}")
        return None

# Add companies to campaign with specified parameters
def add_companies_to_campaign_with_params():
    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        return False
        
    try:
        # Use the parameters passed from the GUI
        campaign_id = {campaign_id}
        campaign_name = "{campaign_name}"
        query = "{query}"
        num_companies_requested = {num_companies}
        campaign_batch_tag = "{batch_tag}"
        
        # Test the query
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            
            if not results:
                print("Query returned 0 results.")
                return False
                
            # Check if company_id is in results
            if 'company_id' not in dict(results[0]):
                print("Query results must include company_id field.")
                return False
                
            # Get list of companies already in campaign
            cursor.execute("SELECT company_id FROM companies_campaign WHERE campaign_id = ?", (campaign_id,))
            existing_company_ids = set([row['company_id'] for row in cursor.fetchall()])
            
            # Filter query results to exclude companies already in campaign
            all_companies = results
            new_companies = [company for company in all_companies if company['company_id'] not in existing_company_ids]
            
            if not new_companies:
                print("All companies from this query are already in the campaign.")
                return False
                
            print(f"Found {{len(new_companies)}} new companies that are not already in this campaign.")
            
            # Determine how many companies to add
            max_companies = len(new_companies)
            if num_companies_requested == 0 or num_companies_requested > max_companies:
                num_companies = max_companies
            else:
                num_companies = num_companies_requested
                
            print(f"Will add {{num_companies}} companies to the campaign.")
            
            # Generate a unique campaign batch ID
            campaign_batch_id = str(uuid.uuid4())
            
            # Limit to the requested number of companies
            companies_to_add = new_companies[:num_companies]
            
            # Insert companies into companies_campaign table with batch information
            added_count = 0
            for company in companies_to_add:
                try:
                    cursor.execute(
                        \"\"\"INSERT INTO companies_campaign 
                           (company_id, campaign_id, campaign_name, 
                            campaign_batch_tag, campaign_batch_id) 
                           VALUES (?, ?, ?, ?, ?)\"\"\",
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
                (campaign_batch_tag, campaign_batch_id, f"Campaign: {{campaign_name}} (Additional)", timestamp)
            )
            
            conn.commit()
            print(f"Added {{added_count}} new companies to campaign '{{campaign_name}}'!")
            print(f"Batch Tag: {{campaign_batch_tag}}")
            print(f"Batch ID: {{campaign_batch_id}}")
            return True
                
        except Exception as e:
            print(f"Error in SQL query: {{e}}")
            return False
            
    except Exception as e:
        conn.rollback()
        print(f"Error adding companies to campaign: {{e}}")
        return False
    finally:
        conn.close()

# Execute the function
success = add_companies_to_campaign_with_params()
print(f"Adding companies result: {{success}}")

# Keep window open for viewing results
input("\\nPress Enter to continue...")
                        """)
                    
                    # Execute the script with environment
                    env = os.environ.copy()
                    env['PROJECT_ROOT'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    subprocess.Popen([sys.executable, temp_script], env=env)
                    
                    # Show a message
                    QMessageBox.information(
                        self, 
                        "Adding Companies", 
                        f"Adding companies to campaign '{campaign_name}'...\n\nPlease check the terminal window for progress."
                    )
                finally:
                    # Change back to the original directory
                    os.chdir(original_dir)
                    # Clean up temp file after execution
                    try:
                        os.unlink(temp_script)
                    except:
                        pass
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error adding companies to campaign: {str(e)}")
    
    def view_campaign_batches(self):
        """View batches for the selected campaign"""
        # Get selected campaign
        selected_items = self.campaign_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        campaign_id = item.data(Qt.UserRole)
        campaign_name = item.text().split(":", 1)[1].split("-")[0].strip()
        
        try:
            # Create a dialog to display batches
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Campaign Batches: {campaign_name}")
            dialog.setMinimumWidth(800)
            dialog.setMinimumHeight(400)
            
            # Create layout
            layout = QVBoxLayout(dialog)
            
            # Header
            header_label = QLabel(f"Batches for Campaign: {campaign_name}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            layout.addWidget(header_label)
            
            # List widget to display batches
            batch_list = QListWidget()
            batch_list.setAlternatingRowColors(True)
            layout.addWidget(batch_list)
            
            # Get database connection
            import sqlite3
            
            # Connect to database directly
            db_path = "/home/eliastsoukatos/Documents/Python/CRM/databases/database.db"
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # Query to get batches
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
            
            # Fetch batches
            batches = cursor.fetchall()
            
            if not batches:
                # No batches found
                batch_list.addItem("No batches found for this campaign")
            else:
                # Add header item
                header_item = QListWidgetItem("Batch Tag" + " " * 15 + "Batch ID" + " " * 25 + "Companies" + " " * 5 + "Added At")
                header_item.setFlags(Qt.NoItemFlags)  # Make non-selectable
                header_item.setBackground(Qt.lightGray)
                batch_list.addItem(header_item)
                
                # Add batch items
                for batch in batches:
                    item_text = f"{batch['campaign_batch_tag']:<20} {batch['campaign_batch_id']:<40} {batch['company_count']:<10} {batch['added_at']}"
                    batch_list.addItem(item_text)
            
            # Close connection
            conn.close()
            
            # Button to close dialog
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            
            # Show dialog
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error viewing campaign batches: {str(e)}")
    
    def run_campaign_prospector(self):
        """Run the company prospector for the selected campaign"""
        # Get selected campaign
        selected_items = self.campaign_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        campaign_id = item.data(Qt.UserRole)
        campaign_name = item.text().split(":", 1)[1].split("-")[0].strip()
        
        # Create a dialog for batch selection
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox, QListWidget
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Run Prospector for: {campaign_name}")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Select batch to process for campaign: {campaign_name}")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header_label)
        
        # Batch combo box
        batch_label = QLabel("Select a batch:")
        layout.addWidget(batch_label)
        
        batch_combo = QComboBox()
        batch_combo.addItem("All Batches", "all")
        layout.addWidget(batch_combo)
        
        # Get database connection to populate batches
        try:
            import sqlite3
            
            # Connect to database directly
            db_path = "/home/eliastsoukatos/Documents/Python/CRM/databases/database.db"
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # Query to get batches for this campaign
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT 
                    campaign_batch_tag,
                    campaign_batch_id,
                    COUNT(*) as company_count
                FROM companies_campaign
                WHERE campaign_id = ?
                GROUP BY campaign_batch_tag, campaign_batch_id
                ORDER BY campaign_batch_tag
            """, (campaign_id,))
            
            batches = cursor.fetchall()
            
            if batches:
                for batch in batches:
                    batch_combo.addItem(
                        f"{batch['campaign_batch_tag']} - {batch['company_count']} companies", 
                        batch['campaign_batch_id']
                    )
            
            conn.close()
            
        except Exception as e:
            QMessageBox.warning(self, "Batch Load Error", f"Error loading batches: {str(e)}")
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # Get selected batch
            selected_batch = batch_combo.currentData()
            batch_display = batch_combo.currentText()
            
            try:
                # Launch company prospector as a separate process
                import subprocess
                import tempfile
                
                # Store the current directory
                original_dir = os.getcwd()
                
                try:
                    # Change to the companies directory
                    os.chdir(companies_dir)
                    
                    # Create a temporary script
                    fd, temp_script = tempfile.mkstemp(suffix='.py')
                    os.close(fd)
                    
                    # Write script for running company prospector with specific batch
                    with open(temp_script, 'w') as f:
                        f.write(f"""
import sys
import os
import subprocess

# Run directly without any imports - this is simpler and more reliable
campaign_id = {campaign_id}
batch_id = "{selected_batch}"

# Directly call the Python script with the campaign ID and batch ID as arguments
if batch_id == "all":
    command = [sys.executable, "/home/eliastsoukatos/Documents/Python/CRM/src/companies/run_company_prospector.py", str(campaign_id)]
else:
    command = [sys.executable, "/home/eliastsoukatos/Documents/Python/CRM/src/companies/run_company_prospector.py", str(campaign_id), batch_id]

# Execute the process directly
print(f"Starting company prospector for campaign: {campaign_name}")
subprocess.call(command)
                        """)
                    
                    # Execute the company prospector script with proper environment
                    env = os.environ.copy()
                    env['PROJECT_ROOT'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    
                    # Start the process and wait a bit before cleaning up
                    subprocess.Popen([sys.executable, temp_script], env=env)
                    
                    # No message - removed annoying popup
                finally:
                    # Change back to the original directory
                    os.chdir(original_dir)
                    # Don't remove temp file immediately - let the process use it
                    # The OS will clean it up later
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error running company prospector: {str(e)}")
    
    def create_contacts_menu(self):
        """Create the contacts menu screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create menu options
        menu_group = QGroupBox("CONTACTS MODULE")
        menu_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        
        # Sourcing button
        sourcing_button = QPushButton("Sourcing")
        sourcing_button.setStyleSheet("font-size: 16px; padding: 15px;")
        sourcing_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_SOURCING_MENU))
        menu_layout.addWidget(sourcing_button)
        
        # Campaigns button
        campaigns_button = QPushButton("Campaigns")
        campaigns_button.setStyleSheet("font-size: 16px; padding: 15px;")
        campaigns_button.clicked.connect(self.run_contact_campaign_menu)
        menu_layout.addWidget(campaigns_button)
        
        # View button (coming soon)
        view_button = QPushButton("View (Coming Soon)")
        view_button.setStyleSheet("font-size: 16px; padding: 15px;")
        view_button.setEnabled(False)
        menu_layout.addWidget(view_button)
        
        # Back button
        back_button = QPushButton("Back to Main Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.MAIN_MENU))
        menu_layout.addWidget(back_button)
        
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        
        return widget
    
    def create_contacts_sourcing_menu(self):
        """Create the contact sourcing menu screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create menu options
        menu_group = QGroupBox("CONTACT SOURCING")
        menu_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        
        # Select Scraper button
        scraper_button = QPushButton("Select Scraper")
        scraper_button.setStyleSheet("font-size: 16px; padding: 15px;")
        scraper_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_SCRAPER_SELECTOR))
        menu_layout.addWidget(scraper_button)
        
        # Import CSV button (coming soon)
        csv_button = QPushButton("Import CSV File (Coming Soon)")
        csv_button.setStyleSheet("font-size: 16px; padding: 15px;")
        csv_button.setEnabled(False)
        menu_layout.addWidget(csv_button)
        
        # Execute Data Query button (coming soon)
        query_button = QPushButton("Execute Data Query (Coming Soon)")
        query_button.setStyleSheet("font-size: 16px; padding: 15px;")
        query_button.setEnabled(False)
        menu_layout.addWidget(query_button)
        
        # Back button
        back_button = QPushButton("Back to Contacts Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_MENU))
        menu_layout.addWidget(back_button)
        
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        
        return widget
    
    def create_contacts_scraper_selector(self):
        """Create the contact scraper selector screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("Available Contact Scrapers")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Scrapers group
        scrapers_group = QGroupBox("Select a Scraper")
        scrapers_layout = QVBoxLayout()
        
        # Cognism Scraper button
        cognism_button = QPushButton("Cognism Scraper")
        cognism_button.setStyleSheet("font-size: 16px; padding: 20px;")
        cognism_button.clicked.connect(self.show_cognism_scraper_options)
        scrapers_layout.addWidget(cognism_button)
        
        # Future scrapers (disabled)
        apollo_button = QPushButton("Apollo Scraper (Coming Soon)")
        apollo_button.setStyleSheet("font-size: 16px; padding: 20px;")
        apollo_button.setEnabled(False)
        scrapers_layout.addWidget(apollo_button)
        
        zoominfo_button = QPushButton("ZoomInfo Scraper (Coming Soon)")
        zoominfo_button.setStyleSheet("font-size: 16px; padding: 20px;")
        zoominfo_button.setEnabled(False)
        scrapers_layout.addWidget(zoominfo_button)
        
        scrapers_group.setLayout(scrapers_layout)
        layout.addWidget(scrapers_group)
        
        # Back button
        back_button = QPushButton("Back to Sourcing Menu")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_SOURCING_MENU))
        layout.addWidget(back_button)
        
        return widget
    
    def select_companies_for_cognism(self):
        """Select companies for Cognism scraper"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox, QFileDialog
            import sqlite3
            import os
            import csv
            
            # Get the last directory path from settings, if available
            settings_dir = '/home/eliastsoukatos/Documents/Python/CRM/databases'
            settings_file = os.path.join(settings_dir, 'export_settings.txt')
            last_dir = os.path.expanduser('~')  # Default to home directory
            
            if os.path.exists(settings_file):
                try:
                    with open(settings_file, 'r') as f:
                        saved_dir = f.read().strip()
                        if os.path.exists(saved_dir):
                            last_dir = saved_dir
                except:
                    pass
            
            # Create a dialog for campaign and batch selection
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Companies for Cognism")
            dialog.setMinimumWidth(500)
            
            layout = QVBoxLayout(dialog)
            
            # Header
            header_label = QLabel("Select a campaign and batch to extract company domains")
            header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(header_label)
            
            # Campaign selection
            campaign_label = QLabel("Select Campaign:")
            layout.addWidget(campaign_label)
            
            campaign_combo = QComboBox()
            layout.addWidget(campaign_combo)
            
            # Batch selection
            batch_label = QLabel("Select Batch:")
            layout.addWidget(batch_label)
            
            batch_combo = QComboBox()
            batch_combo.addItem("All Batches", "all")
            layout.addWidget(batch_combo)
            
            # Get campaigns from database
            try:
                # Connect to database with debug info - use ABSOLUTE PATH to database
                db_path = '/home/eliastsoukatos/Documents/Python/CRM/databases/database.db'
                print(f"Using absolute path to database: {db_path}")
                
                # Verify the database exists
                if not os.path.exists(db_path):
                    print(f"ERROR: Database file not found at: {db_path}")
                    # Show error to user
                    QMessageBox.critical(self, "Database Error", 
                                      f"Database file not found at: {db_path}\nPlease verify your installation.")
                    conn.close()
                    return
                
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Debug: List tables to verify database structure
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print("Tables in database:")
                for table in tables:
                    print(f"- {table[0]}")
                    
                # Check if campaigns and companies_campaign tables exist
                has_campaigns = any(t[0] == 'campaigns' for t in tables)
                has_companies_campaign = any(t[0] == 'companies_campaign' for t in tables)
                
                print(f"Has campaigns table: {has_campaigns}")
                print(f"Has companies_campaign table: {has_companies_campaign}")
                
                if has_campaigns:
                    # Check campaign count
                    cursor.execute("SELECT COUNT(*) FROM campaigns")
                    campaign_count = cursor.fetchone()[0]
                    print(f"Number of campaigns: {campaign_count}")
                    
                    if campaign_count > 0:
                        # List some campaign names
                        cursor.execute("SELECT campaign_name FROM campaigns LIMIT 3")
                        campaign_names = cursor.fetchall()
                        print("Sample campaign names:")
                        for name in campaign_names:
                            print(f"- {name[0]}")
                
                # Get campaigns directly from companies_campaign
                try:
                    print("Using companies_campaign table directly to find campaigns")
                    
                    # Simplify the query to make it more robust
                    query = """
                        SELECT campaign_id, campaign_name, COUNT(*) as total_companies
                        FROM companies_campaign
                        GROUP BY campaign_id, campaign_name
                    """
                    print(f"Executing query: {query}")
                    cursor.execute(query)
                    
                    # Fetch all results and print for debugging
                    raw_campaigns = cursor.fetchall()
                    print(f"Raw query returned {len(raw_campaigns) if raw_campaigns else 0} rows")
                    
                    if raw_campaigns:
                        for camp in raw_campaigns:
                            print(f"Campaign found: ID={camp[0]}, Name={camp[1]}, Companies={camp[2]}")
                    
                    # Create a list of campaign dictionaries that will work with our UI
                    campaigns = []
                    for camp in raw_campaigns:
                        campaign = {
                            'campaign_id': camp[0],
                            'campaign_name': camp[1],
                            'total_companies': camp[2]
                        }
                        campaigns.append(campaign)
                    
                    if not campaigns:
                        QMessageBox.warning(self, "No Campaigns", 
                                          "No companies have been added to any campaigns. Please create a campaign first.")
                        conn.close()
                        return
                    
                    print(f"Created {len(campaigns)} campaign objects for the UI")
                    
                except Exception as e:
                    print(f"Error getting campaigns from companies_campaign: {e}")
                    QMessageBox.critical(self, "Database Error", f"Error querying campaigns: {str(e)}")
                    conn.close()
                    return
                
                # Add campaigns to combo box
                if isinstance(campaigns, list):
                    # Handle the case where we manually created a list of dict objects
                    for campaign in campaigns:
                        campaign_combo.addItem(
                            f"{campaign['campaign_name']} - {campaign['total_companies']} companies", 
                            campaign['campaign_id']
                        )
                else:
                    # Handle the normal case where campaigns is a sqlite3.Cursor result
                    for campaign in campaigns:
                        campaign_combo.addItem(
                            f"{campaign['campaign_name']} - {campaign['total_companies']} companies", 
                            campaign['campaign_id']
                        )
                
                # Function to update batches when campaign changes
                def update_batches():
                    campaign_id = campaign_combo.currentData()
                    batch_combo.clear()
                    batch_combo.addItem("All Batches", "all")
                    
                    # Get batches for this campaign
                    try:
                        print(f"Getting batches for campaign_id: {campaign_id}")
                        
                        # Simplify the query to make it more robust
                        query = """
                            SELECT DISTINCT 
                                campaign_batch_tag,
                                campaign_batch_id,
                                COUNT(*) as company_count
                            FROM companies_campaign
                            WHERE campaign_id = ?
                            GROUP BY campaign_batch_tag, campaign_batch_id
                        """
                        print(f"Executing query: {query} with campaign_id={campaign_id}")
                        cursor.execute(query, (campaign_id,))
                        
                        # Get raw results for debugging
                        raw_batches = cursor.fetchall()
                        print(f"Raw batch query returned {len(raw_batches) if raw_batches else 0} rows")
                        
                        if raw_batches:
                            for batch in raw_batches:
                                # Print details for debugging
                                print(f"Batch found: Tag={batch[0]}, ID={batch[1]}, Companies={batch[2]}")
                                
                                # Get batch data (we know it's columns 0, 1, 2 now)
                                tag = batch[0] if batch[0] is not None else "Unknown"
                                batch_id = batch[1] if batch[1] is not None else "Unknown"
                                count = batch[2]
                                
                                batch_combo.addItem(
                                    f"{tag} - {count} companies", 
                                    batch_id
                                )
                    except Exception as e:
                        print(f"Error getting batches: {e}")
                        # Continue anyway with just "All Batches"
                
                # Connect signal
                campaign_combo.currentIndexChanged.connect(update_batches)
                
                # Initial update
                update_batches()
                
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Error loading campaigns: {str(e)}")
                return
            
            # Add buttons
            button_box = QDialogButtonBox()
            extract_button = button_box.addButton("Extract Companies", QDialogButtonBox.AcceptRole)
            cancel_button = button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            # Show dialog
            if dialog.exec_() == QDialog.Accepted:
                # Get selected campaign and batch
                campaign_id = campaign_combo.currentData()
                campaign_name = campaign_combo.currentText().split(" - ")[0]
                batch_id = batch_combo.currentData()
                
                # Ask user where to save the file
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Domains CSV",
                    os.path.join(last_dir, f"{campaign_name}_domains.csv"),
                    "CSV Files (*.csv)"
                )
                
                if not file_path:
                    return
                
                # Save the directory for next time
                save_dir = os.path.dirname(file_path)
                if not os.path.exists(settings_dir):
                    os.makedirs(settings_dir, exist_ok=True)
                    
                with open(settings_file, 'w') as f:
                    f.write(save_dir)
                
                # Query to get company domains
                try:
                    # Print campaign/batch info for debugging
                    print(f"Exporting domains for campaign_id: {campaign_id}, batch_id: {batch_id}")
                    
                    # Check if we have any companies in this campaign
                    cursor.execute(
                        "SELECT COUNT(*) FROM companies_campaign WHERE campaign_id = ?", 
                        (campaign_id,)
                    )
                    total_companies = cursor.fetchone()[0]
                    print(f"Total companies in this campaign: {total_companies}")
                    
                    # Check companies table
                    cursor.execute("SELECT COUNT(*) FROM companies")
                    total_all_companies = cursor.fetchone()[0]
                    print(f"Total companies in database: {total_all_companies}")
                    
                    # Check companies with domains
                    cursor.execute("SELECT COUNT(*) FROM companies WHERE domain IS NOT NULL AND domain != ''")
                    companies_with_domains = cursor.fetchone()[0]
                    print(f"Companies with domains: {companies_with_domains}")
                    
                    # Get domains with simpler, more reliable queries, ONLY for "approved" companies
                    if batch_id == "all":
                        # First get company IDs from the campaign - ONLY approved companies
                        cursor.execute(
                            "SELECT company_id FROM companies_campaign WHERE campaign_id = ? AND current_state = 'approved'",
                            (campaign_id,)
                        )
                        company_ids = [row[0] for row in cursor.fetchall()]
                        
                        print(f"Found {len(company_ids)} approved companies in this campaign")
                        
                        if not company_ids:
                            print("No approved company IDs found in this campaign!")
                            domains = []
                        else:
                            # Use parameter substitution with company IDs
                            placeholders = ','.join('?' for _ in company_ids)
                            cursor.execute(
                                f"SELECT DISTINCT domain FROM companies WHERE company_id IN ({placeholders}) AND domain IS NOT NULL AND domain != ''",
                                company_ids
                            )
                            domains = cursor.fetchall()
                    else:
                        # First get company IDs from the specific batch - ONLY approved companies
                        cursor.execute(
                            "SELECT company_id FROM companies_campaign WHERE campaign_id = ? AND campaign_batch_id = ? AND current_state = 'approved'",
                            (campaign_id, batch_id)
                        )
                        company_ids = [row[0] for row in cursor.fetchall()]
                        
                        print(f"Found {len(company_ids)} approved companies in this batch")
                        
                        if not company_ids:
                            print("No approved company IDs found in this batch!")
                            domains = []
                        else:
                            # Use parameter substitution with company IDs
                            placeholders = ','.join('?' for _ in company_ids)
                            cursor.execute(
                                f"SELECT DISTINCT domain FROM companies WHERE company_id IN ({placeholders}) AND domain IS NOT NULL AND domain != ''",
                                company_ids
                            )
                            domains = cursor.fetchall()
                    
                    # Additional debug info
                    print(f"Found {len(domains) if domains else 0} domains for export")
                    
                    # Write domains to CSV (no headers, just values)
                    domain_count = 0
                    with open(file_path, 'w', newline='') as f:
                        if domains:
                            for domain in domains:
                                # Handle both dict-like objects and tuples
                                if hasattr(domain, 'keys'):
                                    # SQLite row object
                                    domain_value = domain['domain']
                                elif isinstance(domain, tuple) and len(domain) > 0:
                                    # Tuple result
                                    domain_value = domain[0]
                                else:
                                    # Unexpected format, try converting to string
                                    domain_value = str(domain)
                                
                                # Only write if we have a valid domain
                                if domain_value and not domain_value.isspace():
                                    f.write(f"{domain_value}\n")
                                    domain_count += 1
                    
                    # Debug info
                    print(f"Exported {domain_count} domains to {file_path}")
                    if domains and domain_count == 0:
                        print(f"First domain item format: {type(domains[0])}")
                        print(f"First domain item content: {domains[0]}")
                    
                    # Show success message
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Successfully exported {domain_count} domains from approved companies to {file_path}"
                    )
                    
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Error exporting domains: {str(e)}")
                finally:
                    conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error selecting companies: {str(e)}")
    
    def create_cognism_scraper_options(self):
        """Create the cognism scraper options screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("Cognism Scraper")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Actions group
        actions_group = QGroupBox("Cognism Scraper Actions")
        actions_layout = QVBoxLayout()
        
        # Select Companies button
        select_button = QPushButton("Select Companies")
        select_button.setStyleSheet("font-size: 16px; padding: 20px;")
        select_button.clicked.connect(self.select_companies_for_cognism)
        actions_layout.addWidget(select_button)
        
        # Run Cognism Scraper button
        run_button = QPushButton("Run Cognism Scraper")
        run_button.setStyleSheet("font-size: 16px; padding: 20px;")
        run_button.clicked.connect(self.run_cognism_scraper)
        actions_layout.addWidget(run_button)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Back button
        back_button = QPushButton("Back to Scraper Selection")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_SCRAPER_SELECTOR))
        layout.addWidget(back_button)
        
        return widget
    
    def show_cognism_scraper_options(self):
        """Show the Cognism scraper options screen"""
        self.stacked_widget.setCurrentIndex(self.COGNISM_SCRAPER_OPTIONS)
    
    def create_cognism_login_screen(self):
        """Create the Cognism login and scraping screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("Cognism Contact Scraper")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Instructions group
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout()
        
        # Instructions labels
        login_instructions = QLabel(
            "1. Credentials will be auto-filled. Complete CAPTCHA and login manually.\n"
            "2. Create a search of contacts on Cognism that you want to scrape.\n"
            "3. Enter a contact tag below and click Run to start scraping."
        )
        login_instructions.setStyleSheet("font-size: 14px; padding: 10px;")
        login_instructions.setWordWrap(True)
        instructions_layout.addWidget(login_instructions)
        
        # Status indicator
        self.cognism_status = QLabel("Ready to start")
        self.cognism_status.setStyleSheet("font-size: 14px; color: blue; font-weight: bold; padding: 10px;")
        self.cognism_status.setAlignment(Qt.AlignCenter)
        instructions_layout.addWidget(self.cognism_status)
        
        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)
        
        # Contact tag input group
        input_group = QGroupBox("Contact Tag Settings")
        input_layout = QFormLayout()
        
        # Tag field
        self.contact_tag_input = QLineEdit()
        self.contact_tag_input.setPlaceholderText("Enter tag for these contacts (e.g., 'tech-vp', 'finance-director')")
        input_layout.addRow("Contact Tag:", self.contact_tag_input)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Action buttons group
        buttons_layout = QHBoxLayout()
        
        # Start button
        self.run_scraper_button = QPushButton("Launch Browser & Start Process")
        self.run_scraper_button.setStyleSheet("font-size: 16px; padding: 15px; background-color: #4CAF50; color: white;")
        self.run_scraper_button.clicked.connect(self.start_cognism_browser)
        buttons_layout.addWidget(self.run_scraper_button)
        
        # Run scraping button (initially disabled)
        self.start_scraping_button = QPushButton("Start Scraping")
        self.start_scraping_button.setStyleSheet("font-size: 16px; padding: 15px; background-color: #2196F3; color: white;")
        self.start_scraping_button.clicked.connect(self.run_cognism_url_scraping)
        self.start_scraping_button.setEnabled(False)
        buttons_layout.addWidget(self.start_scraping_button)
        
        layout.addLayout(buttons_layout)
        
        # Back button
        back_button = QPushButton("Back to Scraper Options")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.COGNISM_SCRAPER_OPTIONS))
        layout.addWidget(back_button)
        
        # Store driver reference
        self.cognism_driver = None
        
        return widget
    
    def run_cognism_scraper(self):
        """Show the Cognism login screen"""
        # Switch to the login screen
        self.stacked_widget.setCurrentIndex(self.COGNISM_LOGIN_SCREEN)
        
        # Reset status and buttons
        self.cognism_status.setText("Ready to start")
        self.cognism_status.setStyleSheet("font-size: 14px; color: blue; font-weight: bold; padding: 10px;")
        self.run_scraper_button.setEnabled(True)
        self.start_scraping_button.setEnabled(False)
    
    def start_cognism_browser(self):
        """Launch the browser and wait for login"""
        try:
            # Import required modules
            import threading
            
            # Path to the Cognism scraper directory - use the correct absolute path
            cognism_dir = '/home/eliastsoukatos/Documents/Python/CRM/src/contacts/cognism_scraper'
            print(f"Using Cognism scraper at: {cognism_dir}")
            
            # Check if the directory exists
            if not os.path.exists(cognism_dir):
                QMessageBox.critical(self, "Error", f"Cognism scraper directory not found at: {cognism_dir}")
                return
            
            # Copy the .env file to the cognism scraper directory if it doesn't exist
            env_file = os.path.join(cognism_dir, '.env')
            if not os.path.exists(env_file):
                root_env_file = '/home/eliastsoukatos/Documents/Python/CRM/.env'
                if os.path.exists(root_env_file):
                    import shutil
                    shutil.copy2(root_env_file, env_file)
                    print(f"Copied .env file from {root_env_file} to {env_file}")
                else:
                    # If no .env file exists, create one from example.env
                    example_env = os.path.join(cognism_dir, 'example.env')
                    if os.path.exists(example_env):
                        import shutil
                        shutil.copy2(example_env, env_file)
                        print(f"Created .env file from example.env")
            
            # Update UI
            self.cognism_status.setText("Opening browser and waiting for login...")
            self.cognism_status.setStyleSheet("font-size: 14px; color: orange; font-weight: bold; padding: 10px;")
            self.run_scraper_button.setEnabled(False)
            
            # Prepare resources before starting thread
            import sys
            original_path = sys.path.copy()
            
            # Fix imports - append proper paths to find modules
            sys.path.append(cognism_dir)
            # Need to import directly without the 'src.' prefix
            sys.path.append(os.path.join(cognism_dir, "src"))
            
            # Launch browser in a separate thread
            def browser_thread():
                try:
                    # Import modules with corrected paths
                    from utils.selenium_setup import initialize_driver
                    from utils.auth import wait_for_manual_login
                    
                    # Update UI
                    self.cognism_status.setText("Opening browser and waiting for login...")
                    
                    # Initialize driver
                    driver = initialize_driver()
                    self.cognism_driver = driver
                    
                    # Open Cognism login page
                    driver.get("https://app.cognism.com/auth/sign-in")
                    
                    # Just fill in the credentials without waiting for login
                    try:
                        # Import directly without the 'utils.' prefix since we're in the utils directory
                        from selenium.webdriver.common.by import By
                        from selenium.webdriver.support.ui import WebDriverWait
                        from selenium.webdriver.support import expected_conditions as EC
                        from config import COGNISM_EMAIL, COGNISM_PASSWORD
                        
                        # Wait for login form elements
                        email_input = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='email']"))
                        )
                        password_input = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='password']"))
                        )
                        
                        # Fill in credentials 
                        email_input.clear()
                        password_input.clear()
                        email_input.send_keys(COGNISM_EMAIL)
                        password_input.send_keys(COGNISM_PASSWORD)
                        
                        # Update UI immediately
                        print("Browser launched, credentials filled")
                    except Exception as e:
                        print(f"Error filling credentials: {str(e)}")
                    
                    # Update UI regardless - enable the button immediately
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
                    
                    # Enable the Start Scraping button
                    self.cognism_status.setText("Browser launched! Complete login if needed. Enter a contact tag and click Start Scraping.")
                    self.cognism_status.setStyleSheet("font-size: 14px; color: green; font-weight: bold; padding: 10px;")
                    self.start_scraping_button.setEnabled(True)
                    
                except Exception as e:
                    print(f"Error during browser setup: {str(e)}")
                    # Update UI with a safer approach
                    self.cognism_status.setText(f"Login failed: {str(e)}")
                    self.cognism_status.setStyleSheet("font-size: 14px; color: red; font-weight: bold; padding: 10px;")
                    self.run_scraper_button.setEnabled(True)
            
            # Start the thread
            threading.Thread(target=browser_thread, daemon=True).start()
            
        except Exception as e:
            self.cognism_status.setText(f"Error: {str(e)}")
            self.cognism_status.setStyleSheet("font-size: 14px; color: red; font-weight: bold; padding: 10px;")
            self.run_scraper_button.setEnabled(True)
    
    def run_cognism_url_scraping(self):
        """Run the URL scraper with the provided tag"""
        try:
            # Get the tag
            contact_tag = self.contact_tag_input.text().strip()
            
            if not contact_tag:
                self.cognism_status.setText("Please enter a contact tag first")
                self.cognism_status.setStyleSheet("font-size: 14px; color: red; font-weight: bold; padding: 10px;")
                return
            
            if not self.cognism_driver:
                self.cognism_status.setText("Browser not initialized. Please start the process again.")
                self.cognism_status.setStyleSheet("font-size: 14px; color: red; font-weight: bold; padding: 10px;")
                self.run_scraper_button.setEnabled(True)
                self.start_scraping_button.setEnabled(False)
                return
            
            # Import required modules
            import threading
            
            # Update UI
            self.cognism_status.setText(f"Scraping contacts with tag: {contact_tag}...")
            self.cognism_status.setStyleSheet("font-size: 14px; color: orange; font-weight: bold; padding: 10px;")
            self.start_scraping_button.setEnabled(False)
            
            # Add necessary paths
            import sys
            cognism_dir = '/home/eliastsoukatos/Documents/Python/CRM/src/contacts/cognism_scraper'
            sys.path.append(cognism_dir)
            sys.path.append(os.path.join(cognism_dir, "src"))
            
            # Run scraper in a separate thread
            def scraper_thread():
                try:
                    # Import the necessary modules directly 
                    try:
                        # First make sure we're completely logged in
                        print("Starting URL scraping with tag:", contact_tag)
                        
                        # Import scraper modules
                        from utils_urls.url_navigation import navigate_and_scrape
                        
                        # Run the URL scraper with the segment tag
                        navigate_and_scrape(self.cognism_driver, contact_tag)
                        
                        # Update UI after URL scraping
                        from PyQt5.QtWidgets import QApplication
                        QApplication.processEvents()
                        self.cognism_status.setText("URLs scraped successfully! Now scraping contact details...")
                        self.cognism_status.setStyleSheet("font-size: 14px; color: blue; font-weight: bold; padding: 10px;")
                        
                        # Now run the contacts scraper without reinitializing the driver
                        print("Starting contact details scraping...")
                        
                        # Import the contacts scraper modules
                        from utils_contacts.database import save_to_db, print_db_path
                        from utils_contacts.scraper import scrape_page
                        from utils_contacts.read_db import get_urls_from_db
                        from utils_contacts.no_duplicates import filter_new_urls
                        from utils_contacts.navigate import open_new_tabs
                        from config import SCRAPING_DELAY
                        import time
                        
                        # Keep the login tab reference
                        login_tab = self.cognism_driver.current_window_handle
                        
                        # Load only new URLs that are not in the database
                        url_entries = filter_new_urls()
                        
                        if not url_entries:
                            print("⚠️ No new URLs found. All entries already exist in the database.")
                        else:
                            urls = [entry["url"] for entry in url_entries]
                            print(f"✅ {len(urls)} new URLs found and ready for processing.")
                            
                            # Process URLs in batches - with better debugging
                            print(f"Starting to process {len(urls)} URLs in batches")
                            
                            # Get the batches generator
                            batches = open_new_tabs(self.cognism_driver, urls)
                            
                            # Process each batch
                            for batch_index, tabs in enumerate(batches):
                                print(f"Processing batch {batch_index+1} with {len(tabs)} tabs")
                                print(f"Current tab handles: {tabs}")
                                for tab_index, tab in enumerate(tabs):
                                    try:
                                        self.cognism_driver.switch_to.window(tab)
                                        
                                        try:
                                            # Calculate the index safely
                                            entry_index = (batch_index * len(tabs)) + tab_index
                                            
                                            # Verify the index is valid before accessing
                                            if entry_index >= len(url_entries):
                                                print(f"⚠️ Index {entry_index} is out of range (max: {len(url_entries)-1})")
                                                continue
                                                
                                            # Get data entry safely
                                            data_entry = url_entries[entry_index]
                                            
                                            # Get the current URL from the browser if possible
                                            current_url = self.cognism_driver.current_url
                                            print(f"Processing tab URL: {current_url}")
                                            
                                            # Update UI with current progress
                                            self.cognism_status.setText(f"Scraping contact {entry_index + 1} of {len(urls)}...")
                                            QApplication.processEvents()
                                            
                                            # Extract data
                                            extracted_data = scrape_page(self.cognism_driver)
                                        except Exception as index_error:
                                            print(f"⚠️ Error accessing data entry: {index_error}")
                                            continue
                                        
                                        if extracted_data and 'data_entry' in locals():
                                            # Merge extracted data with metadata if data_entry is available
                                            extracted_data.update({
                                                "Segment": data_entry.get("segment", "unknown"),
                                                "Timestamp": data_entry.get("timestamp", "unknown"),
                                                "Cognism URL": data_entry.get("url", current_url if 'current_url' in locals() else "unknown")
                                            })
                                            
                                            # Rename keys to match the database column names
                                            corrected_data = {
                                                "Name": extracted_data.get("Name"),
                                                "Last_Name": extracted_data.get("Last Name"),
                                                "Mobile_Phone": extracted_data.get("Mobile Phone"),
                                                "Email": extracted_data.get("Email"),
                                                "Role": extracted_data.get("Role"),
                                                "City": extracted_data.get("City"),
                                                "State": extracted_data.get("State"),
                                                "Country": extracted_data.get("Country"),
                                                "Timezone": extracted_data.get("Timezone"),
                                                "LinkedIn_URL": extracted_data.get("LinkedIn URL"),
                                                "Company_Name": extracted_data.get("Company Name"),
                                                "Website": extracted_data.get("Website"),
                                                "Employees": extracted_data.get("Employees"),
                                                "Founded": extracted_data.get("Founded"),
                                                "Segment": extracted_data.get("Segment"),
                                                "Timestamp": extracted_data.get("Timestamp"),
                                                "Cognism_URL": extracted_data.get("Cognism URL")
                                            }
                                            
                                            # Save data
                                            save_to_db(corrected_data)
                                        else:
                                            print(f"⚠️ No data extracted for URL: {data_entry['url']}")
                                            
                                        time.sleep(SCRAPING_DELAY)
                                        
                                    except Exception as e:
                                        print(f"⚠️ Error processing tab: {e}")
                                
                                # Close processed tabs
                                for tab in tabs:
                                    try:
                                        self.cognism_driver.switch_to.window(tab)
                                        self.cognism_driver.close()
                                    except Exception as e:
                                        print(f"⚠️ Error closing tab: {e}")
                                
                                # Ensure switching back to login tab
                                try:
                                    self.cognism_driver.switch_to.window(login_tab)
                                except Exception as e:
                                    print(f"⚠️ Error switching back to login tab: {e}")
                            
                            print("✅ Contact scraping completed.")
                    
                    except Exception as e:
                        print(f"Error during scraping: {str(e)}")
                        raise # Re-raise to be caught by the outer try/except block
                    
                    # Update UI with a safer approach
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
                    
                    # Update status
                    self.cognism_status.setText("URL and contact scraping completed successfully!")
                    self.cognism_status.setStyleSheet("font-size: 14px; color: green; font-weight: bold; padding: 10px;")
                    self.run_scraper_button.setEnabled(True)
                    self.start_scraping_button.setEnabled(False)
                    
                    # Clean up the driver
                    if self.cognism_driver:
                        try:
                            self.cognism_driver.quit()
                        except:
                            pass
                        self.cognism_driver = None
                    
                except Exception as e:
                    print(f"Error during scraping: {str(e)}")
                    
                    # Update UI with a safer approach
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
                    
                    # Update status
                    self.cognism_status.setText(f"Scraping failed: {str(e)}")
                    self.cognism_status.setStyleSheet("font-size: 14px; color: red; font-weight: bold; padding: 10px;")
                    self.run_scraper_button.setEnabled(True)
                    self.start_scraping_button.setEnabled(True)
                    
                    # Clean up the driver
                    if self.cognism_driver:
                        try:
                            self.cognism_driver.quit()
                        except:
                            pass
                        self.cognism_driver = None
            
            # Start the thread
            threading.Thread(target=scraper_thread, daemon=True).start()
            
        except Exception as e:
            self.cognism_status.setText(f"Error: {str(e)}")
            self.cognism_status.setStyleSheet("font-size: 14px; color: red; font-weight: bold; padding: 10px;")
            self.start_scraping_button.setEnabled(True)
    
    
    def create_contacts_campaigns_menu(self):
        """Create the contacts campaigns menu screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create menu options
        menu_group = QGroupBox("CONTACTS CAMPAIGNS")
        menu_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        
        # Select Existing Campaign button
        select_button = QPushButton("Select Existing Campaign")
        select_button.setStyleSheet("font-size: 16px; padding: 15px;")
        select_button.clicked.connect(self.run_contact_campaign_selector)
        menu_layout.addWidget(select_button)
        
        # Run Contact Prospector button
        prospector_button = QPushButton("Run Contact Prospector")
        prospector_button.setStyleSheet("font-size: 16px; padding: 15px;")
        prospector_button.clicked.connect(self.run_contact_prospector)
        menu_layout.addWidget(prospector_button)
        
        # Back button
        back_button = QPushButton("Back to Contacts Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_MENU))
        menu_layout.addWidget(back_button)
        
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        
        return widget
        
    def run_contact_campaign_menu(self):
        """Show the contact campaigns menu screen"""
        self.stacked_widget.setCurrentIndex(self.CONTACTS_CAMPAIGNS_MENU)
        
    def run_contact_campaign_selector(self):
        """Run the contact campaign GUI selector"""
        try:
            # Launch contact campaign GUI as a separate process
            import subprocess
            
            # Store the current directory
            original_dir = os.getcwd()
            
            try:
                # Path to contact campaign GUI script
                script_path = os.path.join(contacts_dir, 'run_contact_campaign_gui.py')
                
                # Check if the file exists
                if not os.path.exists(script_path):
                    print(f"Error: Could not find the contact campaign GUI script at {script_path}")
                    QMessageBox.critical(self, "Error", f"Could not find the contact campaign GUI script at {script_path}")
                    return
                
                # Change to the contacts directory
                os.chdir(contacts_dir)
                
                # Run the script
                subprocess.Popen([sys.executable, script_path])
                
            finally:
                # Change back to the original directory
                os.chdir(original_dir)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running contact campaign selector: {str(e)}")
    
    def run_contact_prospector(self):
        """Run the contact prospector"""
        try:
            # Launch contact prospector as a separate process
            import subprocess
            
            # Store the current directory
            original_dir = os.getcwd()
            
            try:
                # Path to contact prospector script
                script_path = os.path.join(contacts_dir, 'run_contact_prospector.py')
                
                # Check if the file exists
                if not os.path.exists(script_path):
                    print(f"Error: Could not find the contact prospector script at {script_path}")
                    QMessageBox.critical(self, "Error", f"Could not find the contact prospector script at {script_path}")
                    return
                
                # Change to the contacts directory
                os.chdir(contacts_dir)
                
                # Run the script
                subprocess.Popen([sys.executable, script_path])
                
            finally:
                # Change back to the original directory
                os.chdir(original_dir)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running contact prospector: {str(e)}")
    
    def create_phone_dialer_screen(self):
        """Create the phone dialer screen"""
        from PyQt5.QtWidgets import (QPushButton, QHBoxLayout, QVBoxLayout, 
                                   QWidget, QLabel, QComboBox, QGroupBox, QFormLayout)
        import sqlite3
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("Phone Dialer")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Campaign selection group
        selection_group = QGroupBox("Campaign Selection")
        selection_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; }")
        form_layout = QFormLayout()
        
        # Company campaign dropdown
        self.company_campaign_combo = QComboBox()
        self.company_campaign_combo.setMinimumWidth(300)
        self.company_campaign_combo.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Company Campaign:", self.company_campaign_combo)
        
        # Contact campaign batch tag dropdown
        self.contact_batch_combo = QComboBox()
        self.contact_batch_combo.setMinimumWidth(300)
        self.contact_batch_combo.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Contact Campaign Batch Tag:", self.contact_batch_combo)
        
        # Load campaigns button
        load_btn = QPushButton("Load Campaigns")
        load_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        load_btn.clicked.connect(self.load_phone_dialer_campaigns)
        form_layout.addRow("", load_btn)
        
        selection_group.setLayout(form_layout)
        layout.addWidget(selection_group)
        
        # Proceed button
        proceed_btn = QPushButton("Proceed")
        proceed_btn.setStyleSheet(
            "font-size: 16px; padding: 12px; "
            "background-color: #4CAF50; color: white; "
            "border-radius: 5px; font-weight: bold;"
        )
        proceed_btn.setMinimumWidth(200)
        proceed_btn.clicked.connect(self.start_phone_dialer)
        
        # Center the button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(proceed_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        # Back button
        back_button = QPushButton("Back to Main Menu")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(self.MAIN_MENU))
        layout.addWidget(back_button)
        
        return widget
        
    def load_phone_dialer_campaigns(self):
        """Load company campaigns and contact batch tags for the phone dialer"""
        from phone_dialer import PhoneDialerApp
        
        # Create a phone dialer instance
        self.phone_dialer = PhoneDialerApp(parent=self)
        
        # Use the module to load campaigns
        self.phone_dialer.load_campaigns(self.company_campaign_combo, self.contact_batch_combo)
    
    def start_phone_dialer(self):
        """Start the phone dialer with selected campaign and batch tag"""
        from PyQt5.QtWidgets import QMessageBox
        from phone_dialer import PhoneDialerApp
        
        # Check if we have a phone dialer instance
        if not hasattr(self, 'phone_dialer'):
            self.phone_dialer = PhoneDialerApp(parent=self)
        
        # Get selected campaign
        campaign_id = self.company_campaign_combo.currentData()
        if not campaign_id:
            QMessageBox.warning(self, "No Campaign Selected", "Please select a company campaign first.")
            return
        
        campaign_name = self.company_campaign_combo.currentText().split(" - ")[0]
        
        # Get selected batch tag
        batch_tag = self.contact_batch_combo.currentData()
        if not batch_tag:
            batch_tag = "all"
        
        # Load contacts for this campaign and batch
        if self.phone_dialer.load_contacts(campaign_id, batch_tag):
            # Show the contacts dialog
            self.phone_dialer.show_contacts_dialog(campaign_name, batch_tag)
    
    # All methods related to phone dialer functionality have been removed
    def run_company_prospector(self):
        """Run the company prospector"""
        try:
            # Show dialog to select a campaign
            import sqlite3
            
            # Connect to database directly
            db_path = "/home/eliastsoukatos/Documents/Python/CRM/databases/database.db"
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # Get campaigns for selection
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.campaign_id, c.campaign_name, 
                       COUNT(cc.company_id) as total_companies
                FROM campaigns c
                LEFT JOIN companies_campaign cc ON c.campaign_id = cc.campaign_id
                GROUP BY c.campaign_id
                ORDER BY c.created_at DESC
            """)
            
            campaigns = cursor.fetchall()
            conn.close()
            
            if not campaigns:
                QMessageBox.warning(self, "No Campaigns", "No campaigns found. Please create a campaign first.")
                return
            
            # Show campaign selection dialog
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Campaign for Prospector")
            dialog.setMinimumWidth(500)
            
            layout = QVBoxLayout(dialog)
            
            # Header
            header_label = QLabel("Select a campaign to process with Company Prospector")
            header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(header_label)
            
            # Campaign combo box
            campaign_label = QLabel("Campaign:")
            layout.addWidget(campaign_label)
            
            campaign_combo = QComboBox()
            for campaign in campaigns:
                campaign_combo.addItem(
                    f"{campaign['campaign_name']} - {campaign['total_companies']} companies", 
                    campaign['campaign_id']
                )
            layout.addWidget(campaign_combo)
            
            # Batch combo box
            batch_label = QLabel("Batch (will be populated after selecting campaign):")
            layout.addWidget(batch_label)
            
            batch_combo = QComboBox()
            batch_combo.addItem("All Batches", "all")
            layout.addWidget(batch_combo)
            
            # Update batches when campaign changes
            def update_batches():
                campaign_id = campaign_combo.currentData()
                batch_combo.clear()
                batch_combo.addItem("All Batches", "all")
                
                try:
                    # Connect to database directly
                    db_path = "/home/eliastsoukatos/Documents/Python/CRM/databases/database.db"
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
                    
                    # Query to get batches for this campaign
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT DISTINCT 
                            campaign_batch_tag,
                            campaign_batch_id,
                            COUNT(*) as company_count
                        FROM companies_campaign
                        WHERE campaign_id = ?
                        GROUP BY campaign_batch_tag, campaign_batch_id
                        ORDER BY campaign_batch_tag
                    """, (campaign_id,))
                    
                    batches = cursor.fetchall()
                    
                    if batches:
                        for batch in batches:
                            batch_combo.addItem(
                                f"{batch['campaign_batch_tag']} - {batch['company_count']} companies", 
                                batch['campaign_batch_id']
                            )
                    
                    conn.close()
                    
                except Exception as e:
                    print(f"Error updating batches: {e}")
            
            campaign_combo.currentIndexChanged.connect(update_batches)
            update_batches()  # Initial update
            
            # Buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            # Show dialog
            if dialog.exec_() == QDialog.Accepted:
                # Get selected campaign and batch
                campaign_id = campaign_combo.currentData()
                campaign_name = campaign_combo.currentText().split(" - ")[0]
                selected_batch = batch_combo.currentData()
                batch_display = batch_combo.currentText()
                
                # Launch company prospector as a separate process
                import subprocess
                import tempfile
                
                # Store the current directory
                original_dir = os.getcwd()
                
                try:
                    # Change to the companies directory
                    os.chdir(companies_dir)
                    
                    # Create a temporary script
                    fd, temp_script = tempfile.mkstemp(suffix='.py')
                    os.close(fd)
                    
                    # Write script for running company prospector with specific campaign and batch
                    with open(temp_script, 'w') as f:
                        f.write(f"""
import sys
import os
import subprocess

# Run directly without any imports - this is simpler and more reliable
campaign_id = {campaign_id}
batch_id = "{selected_batch}"

# Directly call the Python script with the campaign ID and batch ID as arguments
if batch_id == "all":
    command = [sys.executable, "/home/eliastsoukatos/Documents/Python/CRM/src/companies/run_company_prospector.py", str(campaign_id)]
else:
    command = [sys.executable, "/home/eliastsoukatos/Documents/Python/CRM/src/companies/run_company_prospector.py", str(campaign_id), batch_id]

# Execute the process directly
print(f"Starting company prospector for campaign: {campaign_name}")
subprocess.call(command)
                        """)
                    
                    # Execute the script with environment
                    env = os.environ.copy()
                    env['PROJECT_ROOT'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    
                    # Start the process and wait a bit before cleaning up
                    subprocess.Popen([sys.executable, temp_script], env=env)
                    
                    # No message - removed annoying popup
                finally:
                    # Change back to the original directory
                    os.chdir(original_dir)
                    # Don't remove temp file immediately - let the process use it
                    # The OS will clean it up later
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running company prospector: {str(e)}")

def start_app_menu():
    """Start the GUI application."""
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


# Legacy console menu functions for backward compatibility
def companies_menu():
    """Display the companies module menu and handle navigation."""
    while True:
        print("\n" + "=" * 50)
        print(f"{Colors.BOLD}{Colors.BLUE}🏢 COMPANIES MODULE{Colors.END}")
        print("=" * 50)
        print("Please select an option:")
        print(f"{Colors.GREEN}1. Sourcing{Colors.END}")
        print(f"{Colors.GREEN}2. Campaigns{Colors.END}")
        print(f"{Colors.YELLOW}3. View (Coming Soon){Colors.END}")
        print(f"{Colors.RED}0. Back to Main Menu{Colors.END}")
        
        choice = input(f"{Colors.BOLD}> {Colors.END}").strip()
        
        if choice == "1":
            # Call the run_company_process function from the run_sourcing_process.py file
            # Use subprocess to run it in a way that avoids import issues
            sourcing_script = os.path.join(companies_dir, 'run_sourcing_process.py')
            
            # Check if the file exists
            if not os.path.exists(sourcing_script):
                print(f"{Colors.RED}Error: Could not find the sourcing script at {sourcing_script}{Colors.END}")
                continue
                
            # Execute the script as a subprocess with the current Python interpreter
            import subprocess
            
            # Store the current directory
            original_dir = os.getcwd()
            
            try:
                # Change to the directory containing the script for proper imports
                os.chdir(os.path.dirname(sourcing_script))
                
                # Run the script
                result = subprocess.run([sys.executable, sourcing_script], 
                                        cwd=os.path.dirname(sourcing_script))
                
                if result.returncode != 0:
                    print(f"{Colors.RED}The sourcing process exited with an error (code {result.returncode}){Colors.END}")
            finally:
                # Change back to the original directory
                os.chdir(original_dir)
        elif choice == "2":
            # Call the campaign management function
            campaigns_script = os.path.join(companies_dir, 'run_campaign_process.py')
            
            # Check if the file exists
            if not os.path.exists(campaigns_script):
                print(f"{Colors.RED}Error: Could not find the campaigns script at {campaigns_script}{Colors.END}")
                continue
                
            # Execute the script as a subprocess with the current Python interpreter
            import subprocess
            
            # Store the current directory
            original_dir = os.getcwd()
            
            try:
                # Change to the directory containing the script for proper imports
                os.chdir(os.path.dirname(campaigns_script))
                
                # Run the script
                result = subprocess.run([sys.executable, campaigns_script], 
                                        cwd=os.path.dirname(campaigns_script))
                
                if result.returncode != 0:
                    print(f"{Colors.RED}The campaign process exited with an error (code {result.returncode}){Colors.END}")
            finally:
                # Change back to the original directory
                os.chdir(original_dir)
        elif choice == "3":
            print(f"\n{Colors.YELLOW}⚠️ This feature is under development and will be available soon.{Colors.END}")
            input("Press Enter to continue...")
        elif choice == "0":
            break
        else:
            print(f"\n{Colors.RED}❌ Invalid option. Please select a valid option.{Colors.END}")
