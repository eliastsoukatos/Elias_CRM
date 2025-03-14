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

from src.companies.src_companies import migrate_social_links
from src.companies.src_companies.clean_ratings import clean_rating_records
from src.companies.src_companies.clean_verifications import clean_verification_records
from src.companies.src_companies.db_initializer import check_for_database

# RUTA HARDCODEADA A LA BASE DE DATOS (ajústala si es necesario)
HARD_CODED_DB_PATH = "/Users/anthonyhurtado/Jobs/personal/others/Elias_CRM/databases/database.db"

# Add phone_dialer directory to path
phone_dialer_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'phone_dialer')
if phone_dialer_dir not in sys.path:
    sys.path.insert(0, phone_dialer_dir)

# Add necessary directories to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
companies_dir = os.path.join(current_dir, 'companies')
src_companies_dir = os.path.join(companies_dir, 'src_companies')
contacts_dir = os.path.join(current_dir, 'contacts')
cognism_dir = os.path.join(contacts_dir, 'cognism_scraper')

for path in [companies_dir, src_companies_dir, contacts_dir, cognism_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import necessary modules


def get_db_path():
    """Retorna la ruta de la base de datos usando la ruta hardcodeada."""
    return HARD_CODED_DB_PATH


def initialize_app():
    """Initialize the application by setting up the database and migrations."""
    print("🔧 Initializing application...")
    db_initialized = check_for_database()
    if not db_initialized:
        print("❌ Database initialization failed.")
        return
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__),
                        'contacts', 'cognism_scraper', 'src', 'utils'))
        from create_database import create_table
        create_table()
        print("✅ Contacts database tables created successfully")
    except Exception as e:
        print(f"⚠️ Contacts database initialization warning: {e}")
    try:
        migrate_social_links()
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")
    try:
        clean_verification_records()
    except Exception as e:
        print(f"⚠️ Verification cleanup warning: {e}")
    try:
        clean_rating_records()
    except Exception as e:
        print(f"⚠️ Rating cleanup warning: {e}")
    print("🚀 Application initialized successfully!")


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
        self.setWindowTitle("CRM System")
        self.setMinimumSize(800, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        header_label = QLabel("CRM SYSTEM")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin: 20px;")
        main_layout.addWidget(header_label)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        # Create screens
        self.main_menu_screen = self.create_main_menu()
        self.companies_menu_screen = self.create_companies_menu()
        self.sourcing_menu_screen = self.create_sourcing_menu()
        self.scraper_selector_screen = self.create_scraper_selector()
        self.clutch_scraper_screen = self.create_clutch_scraper_config()
        self.campaigns_menu_screen = self.create_campaigns_menu()
        self.create_campaign_screen = self.create_campaign_creation_screen()
        self.select_campaign_screen = self.create_campaign_selection_screen()
        self.contacts_menu_screen = self.create_contacts_menu()
        self.contacts_sourcing_menu_screen = self.create_contacts_sourcing_menu()
        self.contacts_scraper_selector_screen = self.create_contacts_scraper_selector()
        self.cognism_scraper_options_screen = self.create_cognism_scraper_options()
        self.cognism_login_screen = self.create_cognism_login_screen()
        self.contacts_campaigns_menu_screen = self.create_contacts_campaigns_menu()
        self.phone_dialer_screen = self.create_phone_dialer_screen()
        self.csv_import_container = QWidget()
        csv_layout = QVBoxLayout(self.csv_import_container)
        self.csv_layout = csv_layout
        back_button = QPushButton("Back to Sourcing Menu")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.SOURCING_MENU))
        csv_layout.addWidget(back_button)
        # Define indices
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
        self.stacked_widget.addWidget(self.main_menu_screen)
        self.stacked_widget.addWidget(self.companies_menu_screen)
        self.stacked_widget.addWidget(self.sourcing_menu_screen)
        self.stacked_widget.addWidget(self.campaigns_menu_screen)
        self.stacked_widget.addWidget(self.scraper_selector_screen)
        self.stacked_widget.addWidget(self.clutch_scraper_screen)
        self.stacked_widget.addWidget(self.csv_import_container)
        self.stacked_widget.addWidget(self.create_campaign_screen)
        self.stacked_widget.addWidget(self.select_campaign_screen)
        self.stacked_widget.addWidget(self.contacts_menu_screen)
        self.stacked_widget.addWidget(self.contacts_sourcing_menu_screen)
        self.stacked_widget.addWidget(self.contacts_scraper_selector_screen)
        self.stacked_widget.addWidget(self.cognism_scraper_options_screen)
        self.stacked_widget.addWidget(self.cognism_login_screen)
        self.stacked_widget.addWidget(self.contacts_campaigns_menu_screen)
        self.stacked_widget.addWidget(self.phone_dialer_screen)
        self.stacked_widget.setCurrentIndex(self.MAIN_MENU)

    def create_main_menu(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        menu_group = QGroupBox("MAIN MENU")
        menu_group.setStyleSheet(
            "QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        companies_button = QPushButton("Companies")
        companies_button.setStyleSheet("font-size: 16px; padding: 15px;")
        companies_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.COMPANIES_MENU))
        menu_layout.addWidget(companies_button)
        contacts_button = QPushButton("Contacts")
        contacts_button.setStyleSheet("font-size: 16px; padding: 15px;")
        contacts_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_MENU))
        menu_layout.addWidget(contacts_button)
        phone_dialer_button = QPushButton("Phone Dialer")
        phone_dialer_button.setStyleSheet("font-size: 16px; padding: 15px;")
        phone_dialer_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.PHONE_DIALER))
        menu_layout.addWidget(phone_dialer_button)
        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("font-size: 16px; padding: 15px;")
        exit_button.clicked.connect(self.close)
        menu_layout.addWidget(exit_button)
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        return widget

    def create_companies_menu(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        menu_group = QGroupBox("COMPANIES MODULE")
        menu_group.setStyleSheet(
            "QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        sourcing_button = QPushButton("Sourcing")
        sourcing_button.setStyleSheet("font-size: 16px; padding: 15px;")
        sourcing_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.SOURCING_MENU))
        menu_layout.addWidget(sourcing_button)
        campaigns_button = QPushButton("Campaigns")
        campaigns_button.setStyleSheet("font-size: 16px; padding: 15px;")
        campaigns_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CAMPAIGNS_MENU))
        menu_layout.addWidget(campaigns_button)
        view_button = QPushButton("View (Coming Soon)")
        view_button.setStyleSheet("font-size: 16px; padding: 15px;")
        view_button.setEnabled(False)
        menu_layout.addWidget(view_button)
        back_button = QPushButton("Back to Main Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.MAIN_MENU))
        menu_layout.addWidget(back_button)
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        return widget

    def create_sourcing_menu(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        menu_group = QGroupBox("COMPANY SOURCING")
        menu_group.setStyleSheet(
            "QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        scraper_button = QPushButton("Select Scraper")
        scraper_button.setStyleSheet("font-size: 16px; padding: 15px;")
        scraper_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.SCRAPER_SELECTOR))
        menu_layout.addWidget(scraper_button)
        csv_button = QPushButton("Import CSV File")
        csv_button.setStyleSheet("font-size: 16px; padding: 15px;")
        csv_button.clicked.connect(self.run_csv_import)
        menu_layout.addWidget(csv_button)
        query_button = QPushButton("Execute Data Query (Coming Soon)")
        query_button.setStyleSheet("font-size: 16px; padding: 15px;")
        query_button.setEnabled(False)
        menu_layout.addWidget(query_button)
        back_button = QPushButton("Back to Companies Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.COMPANIES_MENU))
        menu_layout.addWidget(back_button)
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        return widget

    def create_campaigns_menu(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        menu_group = QGroupBox("COMPANY CAMPAIGNS")
        menu_group.setStyleSheet(
            "QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        create_button = QPushButton("Create New Campaign")
        create_button.setStyleSheet("font-size: 16px; padding: 15px;")
        create_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CREATE_CAMPAIGN))
        menu_layout.addWidget(create_button)
        select_button = QPushButton("Select Existing Campaign")
        select_button.setStyleSheet("font-size: 16px; padding: 15px;")
        select_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.SELECT_CAMPAIGN))
        menu_layout.addWidget(select_button)
        prospector_button = QPushButton("Run Company Prospector")
        prospector_button.setStyleSheet("font-size: 16px; padding: 15px;")
        prospector_button.clicked.connect(self.run_company_prospector)
        menu_layout.addWidget(prospector_button)
        back_button = QPushButton("Back to Companies Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.COMPANIES_MENU))
        menu_layout.addWidget(back_button)
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        return widget

    def create_scraper_selector(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        header_label = QLabel("Available Scrapers")
        header_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        scrapers_group = QGroupBox("Select a Scraper")
        scrapers_layout = QVBoxLayout()
        clutch_button = QPushButton("Clutch Scraper")
        clutch_button.setStyleSheet("font-size: 16px; padding: 20px;")
        clutch_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CLUTCH_SCRAPER))
        scrapers_layout.addWidget(clutch_button)
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
        back_button = QPushButton("Back to Sourcing Menu")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.SOURCING_MENU))
        layout.addWidget(back_button)
        return widget

    def create_clutch_scraper_config(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        header_label = QLabel("Clutch Scraper Configuration")
        header_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        form_group = QGroupBox("Scraper Parameters")
        form_layout = QFormLayout()
        self.companies_spin = QSpinBox()
        self.companies_spin.setMinimum(1)
        self.companies_spin.setMaximum(50000)
        self.companies_spin.setValue(10)
        form_layout.addRow("Number of companies to extract:",
                           self.companies_spin)
        self.portfolio_check = QCheckBox()
        self.portfolio_check.setChecked(True)
        form_layout.addRow("Extract portfolio:", self.portfolio_check)
        self.reviews_check = QCheckBox()
        self.reviews_check.setChecked(True)
        form_layout.addRow("Extract reviews:", self.reviews_check)
        self.reviews_spin = QSpinBox()
        self.reviews_spin.setMinimum(0)
        self.reviews_spin.setMaximum(100)
        self.reviews_spin.setValue(5)
        form_layout.addRow("Number of reviews per company:", self.reviews_spin)
        self.batch_tag = QLineEdit()
        self.batch_tag.setText("clutch_scrape")
        form_layout.addRow("Batch tag:", self.batch_tag)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        url_group = QGroupBox("URLs to Scrape")
        url_layout = QVBoxLayout()
        self.url_list = QListWidget()
        url_layout.addWidget(self.url_list)
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Enter URL (e.g., https://clutch.co/web-developers)")
        url_input_layout.addWidget(self.url_input)
        add_button = QPushButton("Add URL")
        add_button.clicked.connect(self.add_url)
        url_input_layout.addWidget(add_button)
        url_layout.addLayout(url_input_layout)
        remove_button = QPushButton("Remove Selected URL")
        remove_button.clicked.connect(self.remove_url)
        url_layout.addWidget(remove_button)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        self.url_list.addItem("https://clutch.co/web-developers")
        button_layout = QHBoxLayout()
        back_button = QPushButton("Back to Scraper Selection")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.SCRAPER_SELECTOR))
        button_layout.addWidget(back_button)
        run_button = QPushButton("Run Scraper")
        run_button.clicked.connect(self.run_clutch_scraper)
        run_button.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(run_button)
        layout.addLayout(button_layout)
        return widget

    def add_url(self):
        url = self.url_input.text().strip()
        if url:
            if url.startswith("http://") or url.startswith("https://"):
                self.url_list.addItem(url)
                self.url_input.clear()
            else:
                QMessageBox.warning(self, "Invalid URL",
                                    "URL must start with http:// or https://")

    def remove_url(self):
        selected_items = self.url_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            row = self.url_list.row(item)
            self.url_list.takeItem(row)

    def run_clutch_scraper(self):
        try:
            from db_initializer import check_for_database
            if not check_for_database():
                QMessageBox.critical(
                    self, "Error", "Database not found or initialization failed.")
                return
            params = {
                "num_companies": self.companies_spin.value(),
                "extract_portfolio": self.portfolio_check.isChecked(),
                "extract_reviews": self.reviews_check.isChecked(),
                "num_reviews": self.reviews_spin.value(),
                "batch_tag": self.batch_tag.text(),
                "batch_id": str(uuid.uuid4())
            }
            urls = []
            for i in range(self.url_list.count()):
                urls.append(self.url_list.item(i).text())
            params["urls"] = urls
            if not urls:
                QMessageBox.warning(
                    self, "No URLs", "Please add at least one URL to scrape.")
                return
            if not params["batch_tag"]:
                QMessageBox.warning(self, "No Batch Tag",
                                    "Please enter a batch tag.")
                return
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
                import subprocess
                original_dir = os.getcwd()
                try:
                    temp_script = os.path.join(
                        companies_dir, 'temp_clutch_scraper.py')
                    with open(temp_script, 'w') as f:
                        f.write(f"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_companies_dir = os.path.join(current_dir, 'src_companies')
if src_companies_dir not in sys.path:
    sys.path.insert(0, src_companies_dir)

os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.dirname(current_dir))
os.environ['DB_PATH'] = r"{HARD_CODED_DB_PATH}"

from clutch_scraper import run_clutch_scraper

run_clutch_scraper(
    startUrls={params['urls']},
    maxItems={params['num_companies']},
    excludePortfolio={not params['extract_portfolio']},
    includeReviews={params['extract_reviews']},
    maxReviewsPerCompany={params['num_reviews']},
    batch_tag="{params['batch_tag']}",
    batch_id="{params['batch_id']}"
)

print("\\nScraper completed successfully!")
print("Batch ID: {params['batch_id']}")
input("Press Enter to continue...")
                        """)
                    os.chdir(companies_dir)
                    subprocess.Popen([sys.executable, temp_script],
                                     shell=True if os.name == 'nt' else False)
                    QMessageBox.information(self, "Scraper Running",
                                            "The scraper is running in the background.\n\n"
                                            "Please check the terminal window for progress updates.")
                finally:
                    os.chdir(original_dir)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error running scraper: {str(e)}")

    def run_csv_import(self):
        try:
            import subprocess
            original_dir = os.getcwd()
            try:
                temp_script = os.path.join(companies_dir, 'run_csv_import.py')
                with open(temp_script, 'w') as f:
                    f.write("""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_companies_dir = os.path.join(current_dir, 'src_companies')
if src_companies_dir not in sys.path:
    sys.path.insert(0, src_companies_dir)

os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.dirname(current_dir))
os.environ['DB_PATH'] = r""" + f'"{HARD_CODED_DB_PATH}"' + """

from src_companies.csv_import_gui import run_csv_import_gui
run_csv_import_gui()
                    """)
                os.chdir(companies_dir)
                subprocess.Popen([sys.executable, temp_script])
            finally:
                os.chdir(original_dir)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error running CSV import: {str(e)}")

    def create_campaign_creation_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        header_label = QLabel("Create New Campaign")
        header_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        form_group = QGroupBox("Campaign Details")
        form_layout = QFormLayout()
        self.campaign_name_input = QLineEdit()
        self.campaign_name_input.setPlaceholderText(
            "Enter a unique campaign name")
        form_layout.addRow("Campaign Name:", self.campaign_name_input)
        from PyQt5.QtWidgets import QPlainTextEdit
        self.campaign_query_input = QPlainTextEdit()
        self.campaign_query_input.setPlaceholderText(
            "e.g., SELECT company_id FROM companies WHERE headcount > 50")
        self.campaign_query_input.setMinimumHeight(100)
        form_layout.addRow("SQL Query:", self.campaign_query_input)
        query_help = QLabel(
            "Query must return company_id field. You can filter companies based on any criteria.")
        query_help.setWordWrap(True)
        query_help.setStyleSheet("color: #666; font-size: 12px;")
        form_layout.addRow("", query_help)
        self.company_count_input = QSpinBox()
        self.company_count_input.setMinimum(0)
        self.company_count_input.setMaximum(10000)
        self.company_count_input.setValue(0)
        self.company_count_input.setToolTip(
            "Enter 0 to add all companies matching the query")
        form_layout.addRow("Number of Companies (0 for all):",
                           self.company_count_input)
        self.campaign_batch_tag = QLineEdit()
        self.campaign_batch_tag.setText("initial")
        form_layout.addRow("Batch Tag:", self.campaign_batch_tag)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        button_layout = QHBoxLayout()
        back_button = QPushButton("Back to Campaigns Menu")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CAMPAIGNS_MENU))
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
        widget = QWidget()
        layout = QVBoxLayout(widget)
        header_label = QLabel("Select Existing Campaign")
        header_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        list_group = QGroupBox("Available Campaigns")
        list_layout = QVBoxLayout()
        self.campaign_list = QListWidget()
        self.campaign_list.setStyleSheet("font-size: 14px;")
        self.campaign_list.setMinimumHeight(200)
        list_layout.addWidget(self.campaign_list)
        refresh_button = QPushButton("Refresh Campaign List")
        refresh_button.clicked.connect(self.refresh_campaign_list)
        list_layout.addWidget(refresh_button)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        details_group = QGroupBox("Campaign Actions")
        details_layout = QVBoxLayout()
        add_companies_button = QPushButton("Add Companies to Campaign")
        add_companies_button.clicked.connect(self.add_companies_to_campaign)
        add_companies_button.setEnabled(False)
        details_layout.addWidget(add_companies_button)
        view_batches_button = QPushButton("View Campaign Batches")
        view_batches_button.clicked.connect(self.view_campaign_batches)
        view_batches_button.setEnabled(False)
        details_layout.addWidget(view_batches_button)
        run_prospector_button = QPushButton(
            "Run Company Prospector for Campaign")
        run_prospector_button.clicked.connect(self.run_company_prospector)
        run_prospector_button.setEnabled(False)
        details_layout.addWidget(run_prospector_button)
        self.campaign_action_buttons = [
            add_companies_button, view_batches_button, run_prospector_button]
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        button_layout = QHBoxLayout()
        back_button = QPushButton("Back to Campaigns Menu")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CAMPAIGNS_MENU))
        button_layout.addWidget(back_button)
        layout.addLayout(button_layout)
        self.campaign_list.itemSelectionChanged.connect(
            self.on_campaign_selected)
        self.refresh_campaign_list()
        return widget

    def create_campaign(self):
        from PyQt5.QtWidgets import QMessageBox
        campaign_name = self.campaign_name_input.text().strip()
        campaign_query = self.campaign_query_input.toPlainText().strip()
        batch_tag = self.campaign_batch_tag.text().strip()
        num_companies_requested = self.company_count_input.value()
        if not campaign_name:
            QMessageBox.warning(self, "Missing Information",
                                "Please enter a campaign name.")
            return
        if not campaign_query:
            QMessageBox.warning(self, "Missing Information",
                                "Please enter an SQL query.")
            return
        if not batch_tag:
            batch_tag = "initial"
        try:
            import sqlite3
            conn = sqlite3.connect(HARD_CODED_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute(campaign_query)
                results = cursor.fetchall()
                if not results:
                    QMessageBox.warning(self, "Query Error",
                                        "This query returned 0 results.")
                    conn.close()
                    return
                if 'company_id' not in dict(results[0]):
                    QMessageBox.warning(
                        self, "Query Error", "Query results must include company_id field.")
                    conn.close()
                    return
                total_results = len(results)
                if num_companies_requested == 0 or num_companies_requested > total_results:
                    num_companies = total_results
                else:
                    num_companies = num_companies_requested
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Question)
                msg.setText(f"Create campaign with {num_companies} companies?")
                msg.setInformativeText(
                    f"Query found {total_results} matching companies. Proceed with creating the campaign?")
                msg.setWindowTitle("Confirm Campaign Creation")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                if msg.exec_() != QMessageBox.Yes:
                    conn.close()
                    return
                conn.close()
                import subprocess
                import tempfile
                original_dir = os.getcwd()
                try:
                    fd, temp_script = tempfile.mkstemp(suffix='.py')
                    os.close(fd)
                    with open(temp_script, 'w') as f:
                        f.write(f"""
import sys
import os
import sqlite3
from sqlite3 import Error
import datetime
import uuid

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

DB_PATH = r"{HARD_CODED_DB_PATH}"

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
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            if not results:
                print("Query returned 0 results.")
                return False
            if 'company_id' not in dict(results[0]):
                print("Query results must include company_id field.")
                return False
            companies_to_add = results[:num_companies_requested]
            campaign_batch_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO campaigns (campaign_name, query) VALUES (?, ?)",
                           (campaign_name, query))
            campaign_id = cursor.lastrowid
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
                    continue
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

success = create_campaign()
print(f"Campaign creation result: {{success}}")
input("Press Enter to continue...")
                        """)
                    os.chdir(companies_dir)
                    env = os.environ.copy()
                    env['PROJECT_ROOT'] = os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__)))
                    env['DB_PATH'] = HARD_CODED_DB_PATH
                    subprocess.Popen([sys.executable, temp_script], env=env)
                    QMessageBox.information(
                        self,
                        "Campaign Creation",
                        f"Creating campaign '{campaign_name}' with {num_companies} companies...\n\nPlease check the terminal window for results."
                    )
                    self.campaign_name_input.clear()
                    self.campaign_query_input.clear()
                    self.company_count_input.setValue(0)
                    self.campaign_batch_tag.setText("initial")
                finally:
                    os.chdir(original_dir)
                    try:
                        os.unlink(temp_script)
                    except:
                        pass
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error in campaign creation script: {str(e)}")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error testing query: {str(e)}")

    def refresh_campaign_list(self):
        try:
            import sqlite3
            conn = sqlite3.connect(HARD_CODED_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
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
            self.campaign_list.clear()
            for campaign in campaigns:
                item_text = f"{campaign['campaign_id']}: {campaign['campaign_name']} - {campaign['total_companies']} companies"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, campaign['campaign_id'])
                self.campaign_list.addItem(item)
            for button in self.campaign_action_buttons:
                button.setEnabled(False)
            conn.close()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error refreshing campaign list: {str(e)}")

    def on_campaign_selected(self):
        selected_items = self.campaign_list.selectedItems()
        for button in self.campaign_action_buttons:
            button.setEnabled(len(selected_items) > 0)

    def add_companies_to_campaign(self):
        selected_items = self.campaign_list.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        campaign_id = item.data(Qt.UserRole)
        campaign_name = item.text().split(":", 1)[1].split("-")[0].strip()
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add Companies to Campaign: {campaign_name}")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        layout = QVBoxLayout(dialog)
        query_label = QLabel("SQL Query (must return company_id field):")
        layout.addWidget(query_label)
        from PyQt5.QtWidgets import QPlainTextEdit
        query_input = QPlainTextEdit()
        query_input.setPlaceholderText(
            "e.g., SELECT company_id FROM companies WHERE headcount > 50")
        query_input.setMinimumHeight(100)
        layout.addWidget(query_input)
        query_help = QLabel(
            "Example: SELECT company_id FROM companies WHERE industry = 'Technology'")
        query_help.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(query_help)
        num_companies_layout = QHBoxLayout()
        num_companies_label = QLabel("Number of companies to add (0 for all):")
        num_companies_input = QSpinBox()
        num_companies_input.setMinimum(0)
        num_companies_input.setMaximum(10000)
        num_companies_input.setValue(0)
        num_companies_layout.addWidget(num_companies_label)
        num_companies_layout.addWidget(num_companies_input)
        layout.addLayout(num_companies_layout)
        batch_layout = QHBoxLayout()
        batch_label = QLabel("Batch Tag:")
        batch_input = QLineEdit("additional")
        batch_layout.addWidget(batch_label)
        batch_layout.addWidget(batch_input)
        layout.addLayout(batch_layout)
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        add_button = QPushButton("Add Companies")
        add_button.clicked.connect(dialog.accept)
        add_button.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(add_button)
        layout.addLayout(button_layout)
        if dialog.exec_() == QDialog.Accepted:
            query = query_input.toPlainText().strip()
            num_companies = num_companies_input.value()
            batch_tag = batch_input.text().strip()
            if not query:
                QMessageBox.warning(self, "Missing Information",
                                    "Please enter an SQL query.")
                return
            if not batch_tag:
                batch_tag = "additional"
            try:
                import subprocess
                original_dir = os.getcwd()
                try:
                    os.chdir(companies_dir)
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

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

project_root = os.path.dirname(os.path.dirname(current_dir))
os.environ['PROJECT_ROOT'] = project_root

if os.environ.get("DB_PATH") and os.name == 'nt':
    DB_PATH = os.environ.get("DB_PATH")
else:
    DB_PATH = r"{HARD_CODED_DB_PATH}"

def get_db_connection():
    try:
        print(f"Connecting to database at: {{DB_PATH}}")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to database: {{e}}")
        return None

def add_companies_to_campaign_with_params():
    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        return False
    try:
        campaign_id = {campaign_id}
        campaign_name = "{campaign_name}"
        query = "{query}"
        num_companies_requested = {num_companies}
        campaign_batch_tag = "{batch_tag}"
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            if not results:
                print("Query returned 0 results.")
                return False
            if 'company_id' not in dict(results[0]):
                print("Query results must include company_id field.")
                return False
            cursor.execute("SELECT company_id FROM companies_campaign WHERE campaign_id = ?", (campaign_id,))
            existing_company_ids = set([row['company_id'] for row in cursor.fetchall()])
            all_companies = results
            new_companies = [company for company in all_companies if company['company_id'] not in existing_company_ids]
            if not new_companies:
                print("All companies from this query are already in the campaign.")
                return False
            print(f"Found {{len(new_companies)}} new companies that are not already in this campaign.")
            max_companies = len(new_companies)
            if num_companies_requested == 0 or num_companies_requested > max_companies:
                num_companies = max_companies
            else:
                num_companies = num_companies_requested
            print(f"Will add {{num_companies}} companies to the campaign.")
            campaign_batch_id = str(uuid.uuid4())
            companies_to_add = new_companies[:num_companies]
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
                    continue
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

success = add_companies_to_campaign_with_params()
print(f"Adding companies result: {{success}}")
input("\\nPress Enter to continue...")
                        """)
                    env = os.environ.copy()
                    env['PROJECT_ROOT'] = os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__)))
                    env['DB_PATH'] = HARD_CODED_DB_PATH
                    subprocess.Popen([sys.executable, temp_script], env=env)
                    QMessageBox.information(
                        self,
                        "Adding Companies",
                        f"Adding companies to campaign '{campaign_name}'...\n\nPlease check the terminal window for progress."
                    )
                finally:
                    os.chdir(original_dir)
                    try:
                        os.unlink(temp_script)
                    except:
                        pass
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error adding companies to campaign: {str(e)}")

    def view_campaign_batches(self):
        selected_items = self.campaign_list.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        campaign_id = item.data(Qt.UserRole)
        campaign_name = item.text().split(":", 1)[1].split("-")[0].strip()
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Campaign Batches: {campaign_name}")
            dialog.setMinimumWidth(800)
            dialog.setMinimumHeight(400)
            layout = QVBoxLayout(dialog)
            header_label = QLabel(f"Batches for Campaign: {campaign_name}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            layout.addWidget(header_label)
            batch_list = QListWidget()
            batch_list.setAlternatingRowColors(True)
            layout.addWidget(batch_list)
            import sqlite3
            conn = sqlite3.connect(HARD_CODED_DB_PATH)
            conn.row_factory = sqlite3.Row
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
            batches = cursor.fetchall()
            if not batches:
                batch_list.addItem("No batches found for this campaign")
            else:
                header_item = QListWidgetItem(
                    "Batch Tag" + " " * 15 + "Batch ID" + " " * 25 + "Companies" + " " * 5 + "Added At")
                header_item.setFlags(Qt.NoItemFlags)
                header_item.setBackground(Qt.lightGray)
                batch_list.addItem(header_item)
                for batch in batches:
                    item_text = f"{batch['campaign_batch_tag']:<20} {batch['campaign_batch_id']:<40} {batch['company_count']:<10} {batch['added_at']}"
                    batch_list.addItem(item_text)
            conn.close()
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error viewing campaign batches: {str(e)}")

    def run_company_prospector(self):
        """Run the company prospector for the selected campaign"""
        selected_items = self.campaign_list.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        campaign_id = item.data(Qt.UserRole)
        campaign_name = item.text().split(":", 1)[1].split("-")[0].strip()
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Run Prospector for: {campaign_name}")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        header_label = QLabel(
            f"Select batch to process for campaign: {campaign_name}")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header_label)
        batch_label = QLabel("Select a batch:")
        layout.addWidget(batch_label)
        batch_combo = QComboBox()
        batch_combo.addItem("All Batches", "all")
        layout.addWidget(batch_combo)
        try:
            import sqlite3
            conn = sqlite3.connect(HARD_CODED_DB_PATH)
            conn.row_factory = sqlite3.Row
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
            QMessageBox.warning(self, "Batch Load Error",
                                f"Error loading batches: {str(e)}")
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog.exec_() == QDialog.Accepted:
            selected_batch = batch_combo.currentData()
            try:
                import subprocess
                import tempfile
                original_dir = os.getcwd()
                try:
                    os.chdir(companies_dir)
                    fd, temp_script = tempfile.mkstemp(suffix='.py')
                    os.close(fd)
                    with open(temp_script, 'w') as f:
                        f.write(fr"""
import sys
import os
import subprocess

campaign_id = {campaign_id}
batch_id = "{selected_batch}"

if batch_id == "all":
    command = [sys.executable, r"/Users/anthonyhurtado/Jobs/personal/others/Elias_CRM/src/companies/run_company_prospector.py", str(campaign_id)]
else:
    command = [sys.executable, r"/Users/anthonyhurtado/Jobs/personal/others/Elias_CRM/src/companies/run_company_prospector.py", str(campaign_id), batch_id]

print(f"Starting company prospector for campaign: {campaign_name}")
subprocess.call(command)
                        """)
                    env = os.environ.copy()
                    env['PROJECT_ROOT'] = os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__)))
                    subprocess.Popen([sys.executable, temp_script], env=env)
                finally:
                    os.chdir(original_dir)
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error running company prospector: {str(e)}")

    def create_contacts_menu(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        menu_group = QGroupBox("CONTACTS MODULE")
        menu_group.setStyleSheet(
            "QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        sourcing_button = QPushButton("Sourcing")
        sourcing_button.setStyleSheet("font-size: 16px; padding: 15px;")
        sourcing_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_SOURCING_MENU))
        menu_layout.addWidget(sourcing_button)
        campaigns_button = QPushButton("Campaigns")
        campaigns_button.setStyleSheet("font-size: 16px; padding: 15px;")
        campaigns_button.clicked.connect(self.run_contact_campaign_menu)
        menu_layout.addWidget(campaigns_button)
        view_button = QPushButton("View (Coming Soon)")
        view_button.setStyleSheet("font-size: 16px; padding: 15px;")
        view_button.setEnabled(False)
        menu_layout.addWidget(view_button)
        back_button = QPushButton("Back to Main Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.MAIN_MENU))
        menu_layout.addWidget(back_button)
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        return widget

    def create_contacts_sourcing_menu(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        menu_group = QGroupBox("CONTACT SOURCING")
        menu_group.setStyleSheet(
            "QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        scraper_button = QPushButton("Select Scraper")
        scraper_button.setStyleSheet("font-size: 16px; padding: 15px;")
        scraper_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_SCRAPER_SELECTOR))
        menu_layout.addWidget(scraper_button)
        csv_button = QPushButton("Import CSV File (Coming Soon)")
        csv_button.setStyleSheet("font-size: 16px; padding: 15px;")
        csv_button.setEnabled(False)
        menu_layout.addWidget(csv_button)
        query_button = QPushButton("Execute Data Query (Coming Soon)")
        query_button.setStyleSheet("font-size: 16px; padding: 15px;")
        query_button.setEnabled(False)
        menu_layout.addWidget(query_button)
        back_button = QPushButton("Back to Contacts Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_MENU))
        menu_layout.addWidget(back_button)
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        return widget

    def create_contacts_scraper_selector(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        header_label = QLabel("Available Contact Scrapers")
        header_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        scrapers_group = QGroupBox("Select a Scraper")
        scrapers_layout = QVBoxLayout()
        cognism_button = QPushButton("Cognism Scraper")
        cognism_button.setStyleSheet("font-size: 16px; padding: 20px;")
        cognism_button.clicked.connect(self.show_cognism_scraper_options)
        scrapers_layout.addWidget(cognism_button)
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
        back_button = QPushButton("Back to Sourcing Menu")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_SOURCING_MENU))
        layout.addWidget(back_button)
        return widget

    def select_companies_for_cognism(self):
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox, QFileDialog
            import sqlite3
            import os
            import csv
            project_root = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            settings_dir = os.path.join(project_root, 'databases')
            settings_file = os.path.join(settings_dir, 'export_settings.txt')
            last_dir = os.path.expanduser('~')
            if os.path.exists(settings_file):
                try:
                    with open(settings_file, 'r') as f:
                        saved_dir = f.read().strip()
                        if os.path.exists(saved_dir):
                            last_dir = saved_dir
                except:
                    pass
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Companies for Cognism")
            dialog.setMinimumWidth(500)
            layout = QVBoxLayout(dialog)
            header_label = QLabel(
                "Select a campaign and batch to extract company domains")
            header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(header_label)
            campaign_label = QLabel("Select Campaign:")
            layout.addWidget(campaign_label)
            campaign_combo = QComboBox()
            layout.addWidget(campaign_combo)
            batch_label = QLabel("Select Batch:")
            layout.addWidget(batch_label)
            batch_combo = QComboBox()
            batch_combo.addItem("All Batches", "all")
            layout.addWidget(batch_combo)
            try:
                conn = sqlite3.connect(HARD_CODED_DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print("Tables in database:")
                for table in tables:
                    print(f"- {table[0]}")
                has_campaigns = any(t[0] == 'campaigns' for t in tables)
                has_companies_campaign = any(
                    t[0] == 'companies_campaign' for t in tables)
                print(f"Has campaigns table: {has_campaigns}")
                print(
                    f"Has companies_campaign table: {has_companies_campaign}")
                if has_campaigns:
                    cursor.execute("SELECT COUNT(*) FROM campaigns")
                    campaign_count = cursor.fetchone()[0]
                    print(f"Number of campaigns: {campaign_count}")
                    if campaign_count > 0:
                        cursor.execute(
                            "SELECT campaign_name FROM campaigns LIMIT 3")
                        campaign_names = cursor.fetchall()
                        print("Sample campaign names:")
                        for name in campaign_names:
                            print(f"- {name[0]}")
                try:
                    print("Using companies_campaign table directly to find campaigns")
                    query = """
                        SELECT campaign_id, campaign_name, COUNT(*) as total_companies
                        FROM companies_campaign
                        GROUP BY campaign_id, campaign_name
                    """
                    print(f"Executing query: {query}")
                    cursor.execute(query)
                    raw_campaigns = cursor.fetchall()
                    print(
                        f"Raw query returned {len(raw_campaigns) if raw_campaigns else 0} rows")
                    campaigns = []
                    for camp in raw_campaigns:
                        campaign = {
                            'campaign_id': camp[0],
                            'campaign_name': camp[1],
                            'total_companies': camp[2]
                        }
                        campaigns.append(campaign)
                    if not campaigns:
                        QMessageBox.warning(
                            self, "No Campaigns", "No companies have been added to any campaigns. Please create a campaign first.")
                        conn.close()
                        return
                    print(
                        f"Created {len(campaigns)} campaign objects for the UI")
                except Exception as e:
                    print(
                        f"Error getting campaigns from companies_campaign: {e}")
                    QMessageBox.critical(
                        self, "Database Error", f"Error querying campaigns: {str(e)}")
                    conn.close()
                    return
                if isinstance(campaigns, list):
                    for campaign in campaigns:
                        campaign_combo.addItem(
                            f"{campaign['campaign_name']} - {campaign['total_companies']} companies",
                            campaign['campaign_id']
                        )
                else:
                    for campaign in campaigns:
                        campaign_combo.addItem(
                            f"{campaign['campaign_name']} - {campaign['total_companies']} companies",
                            campaign['campaign_id']
                        )

                def update_batches():
                    campaign_id = campaign_combo.currentData()
                    batch_combo.clear()
                    batch_combo.addItem("All Batches", "all")
                    try:
                        print(
                            f"Getting batches for campaign_id: {campaign_id}")
                        query = """
                            SELECT DISTINCT 
                                campaign_batch_tag,
                                campaign_batch_id,
                                COUNT(*) as company_count
                            FROM companies_campaign
                            WHERE campaign_id = ?
                            GROUP BY campaign_batch_tag, campaign_batch_id
                        """
                        print(
                            f"Executing query: {query} with campaign_id={campaign_id}")
                        cursor.execute(query, (campaign_id,))
                        raw_batches = cursor.fetchall()
                        print(
                            f"Raw batch query returned {len(raw_batches) if raw_batches else 0} rows")
                        if raw_batches:
                            for batch in raw_batches:
                                print(
                                    f"Batch found: Tag={batch[0]}, ID={batch[1]}, Companies={batch[2]}")
                                tag = batch[0] if batch[0] is not None else "Unknown"
                                batch_id = batch[1] if batch[1] is not None else "Unknown"
                                count = batch[2]
                                batch_combo.addItem(
                                    f"{tag} - {count} companies",
                                    batch_id
                                )
                    except Exception as e:
                        print(f"Error getting batches: {e}")
                campaign_combo.currentIndexChanged.connect(update_batches)
                update_batches()
            except Exception as e:
                QMessageBox.critical(self, "Database Error",
                                     f"Error loading campaigns: {str(e)}")
                return
            button_box = QDialogButtonBox()
            extract_button = button_box.addButton(
                "Extract Companies", QDialogButtonBox.AcceptRole)
            cancel_button = button_box.addButton(
                "Cancel", QDialogButtonBox.RejectRole)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            if dialog.exec_() == QDialog.Accepted:
                campaign_id = campaign_combo.currentData()
                campaign_name = campaign_combo.currentText().split(" - ")[0]
                batch_id = batch_combo.currentData()
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Domains CSV",
                    os.path.join(last_dir, f"{campaign_name}_domains.csv"),
                    "CSV Files (*.csv)"
                )
                if not file_path:
                    return
                save_dir = os.path.dirname(file_path)
                if not os.path.exists(settings_dir):
                    os.makedirs(settings_dir, exist_ok=True)
                with open(settings_file, 'w') as f:
                    f.write(save_dir)
                try:
                    print(
                        f"Exporting domains for campaign_id: {campaign_id}, batch_id: {batch_id}")
                    cursor.execute(
                        "SELECT COUNT(*) FROM companies_campaign WHERE campaign_id = ?", (campaign_id,))
                    total_companies = cursor.fetchone()[0]
                    print(
                        f"Total companies in this campaign: {total_companies}")
                    cursor.execute("SELECT COUNT(*) FROM companies")
                    total_all_companies = cursor.fetchone()[0]
                    print(
                        f"Total companies in database: {total_all_companies}")
                    cursor.execute(
                        "SELECT COUNT(*) FROM companies WHERE domain IS NOT NULL AND domain != ''")
                    companies_with_domains = cursor.fetchone()[0]
                    print(f"Companies with domains: {companies_with_domains}")
                    if batch_id == "all":
                        cursor.execute(
                            "SELECT company_id FROM companies_campaign WHERE campaign_id = ? AND current_state = 'approved'",
                            (campaign_id,)
                        )
                        company_ids = [row[0] for row in cursor.fetchall()]
                        print(
                            f"Found {len(company_ids)} approved companies in this campaign")
                        if not company_ids:
                            print("No approved company IDs found in this campaign!")
                            domains = []
                        else:
                            placeholders = ','.join('?' for _ in company_ids)
                            cursor.execute(
                                f"SELECT DISTINCT domain FROM companies WHERE company_id IN ({placeholders}) AND domain IS NOT NULL AND domain != ''",
                                company_ids
                            )
                            domains = cursor.fetchall()
                    else:
                        cursor.execute(
                            "SELECT company_id FROM companies_campaign WHERE campaign_id = ? AND campaign_batch_id = ? AND current_state = 'approved'",
                            (campaign_id, batch_id)
                        )
                        company_ids = [row[0] for row in cursor.fetchall()]
                        print(
                            f"Found {len(company_ids)} approved companies in this batch")
                        if not company_ids:
                            print("No approved company IDs found in this batch!")
                            domains = []
                        else:
                            placeholders = ','.join('?' for _ in company_ids)
                            cursor.execute(
                                f"SELECT DISTINCT domain FROM companies WHERE company_id IN ({placeholders}) AND domain IS NOT NULL AND domain != ''",
                                company_ids
                            )
                            domains = cursor.fetchall()
                    print(
                        f"Found {len(domains) if domains else 0} domains for export")
                    domain_count = 0
                    with open(file_path, 'w', newline='') as f:
                        if domains:
                            for domain in domains:
                                if hasattr(domain, 'keys'):
                                    domain_value = domain['domain']
                                elif isinstance(domain, tuple) and len(domain) > 0:
                                    domain_value = domain[0]
                                else:
                                    domain_value = str(domain)
                                if domain_value and not domain_value.isspace():
                                    f.write(f"{domain_value}\n")
                                    domain_count += 1
                    print(f"Exported {domain_count} domains to {file_path}")
                    if domains and domain_count == 0:
                        print(f"First domain item format: {type(domains[0])}")
                        print(f"First domain item content: {domains[0]}")
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Successfully exported {domain_count} domains from approved companies to {file_path}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self, "Export Error", f"Error exporting domains: {str(e)}")
                finally:
                    conn.close()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error selecting companies: {str(e)}")

    def create_cognism_scraper_options(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        header_label = QLabel("Cognism Scraper")
        header_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        actions_group = QGroupBox("Cognism Scraper Actions")
        actions_layout = QVBoxLayout()
        select_button = QPushButton("Select Companies")
        select_button.setStyleSheet("font-size: 16px; padding: 20px;")
        select_button.clicked.connect(self.select_companies_for_cognism)
        actions_layout.addWidget(select_button)
        run_button = QPushButton("Run Cognism Scraper")
        run_button.setStyleSheet("font-size: 16px; padding: 20px;")
        run_button.clicked.connect(self.run_cognism_scraper)
        actions_layout.addWidget(run_button)
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        back_button = QPushButton("Back to Scraper Selection")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_SCRAPER_SELECTOR))
        layout.addWidget(back_button)
        return widget

    def show_cognism_scraper_options(self):
        self.stacked_widget.setCurrentIndex(self.COGNISM_SCRAPER_OPTIONS)

    def create_cognism_login_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        header_label = QLabel("Cognism Contact Scraper")
        header_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout()
        login_instructions = QLabel(
            "1. Credentials will be auto-filled. Complete CAPTCHA and login manually.\n"
            "2. Create a search of contacts on Cognism that you want to scrape.\n"
            "3. Enter a contact tag below and click Run to start scraping."
        )
        login_instructions.setStyleSheet("font-size: 14px; padding: 10px;")
        login_instructions.setWordWrap(True)
        instructions_layout.addWidget(login_instructions)
        self.cognism_status = QLabel("Ready to start")
        self.cognism_status.setStyleSheet(
            "font-size: 14px; color: blue; font-weight: bold; padding: 10px;")
        self.cognism_status.setAlignment(Qt.AlignCenter)
        instructions_layout.addWidget(self.cognism_status)
        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)
        input_group = QGroupBox("Contact Tag Settings")
        input_layout = QFormLayout()
        self.contact_tag_input = QLineEdit()
        self.contact_tag_input.setPlaceholderText(
            "Enter tag for these contacts (e.g., 'tech-vp', 'finance-director')")
        input_layout.addRow("Contact Tag:", self.contact_tag_input)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        buttons_layout = QHBoxLayout()
        self.run_scraper_button = QPushButton("Launch Browser & Start Process")
        self.run_scraper_button.setStyleSheet(
            "font-size: 16px; padding: 15px; background-color: #4CAF50; color: white;")
        self.run_scraper_button.clicked.connect(self.start_cognism_browser)
        buttons_layout.addWidget(self.run_scraper_button)
        self.start_scraping_button = QPushButton("Start Scraping")
        self.start_scraping_button.setStyleSheet(
            "font-size: 16px; padding: 15px; background-color: #2196F3; color: white;")
        self.start_scraping_button.clicked.connect(
            self.run_cognism_url_scraping)
        self.start_scraping_button.setEnabled(False)
        buttons_layout.addWidget(self.start_scraping_button)
        layout.addLayout(buttons_layout)
        back_button = QPushButton("Back to Scraper Options")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.COGNISM_SCRAPER_OPTIONS))
        layout.addWidget(back_button)
        self.cognism_driver = None
        return widget

    def run_cognism_scraper(self):
        self.stacked_widget.setCurrentIndex(self.COGNISM_LOGIN_SCREEN)
        self.cognism_status.setText("Ready to start")
        self.cognism_status.setStyleSheet(
            "font-size: 14px; color: blue; font-weight: bold; padding: 10px;")
        self.run_scraper_button.setEnabled(True)
        self.start_scraping_button.setEnabled(False)

    def start_cognism_browser(self):
        try:
            import threading
            project_root = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            cognism_dir = os.path.join(
                project_root, 'src', 'contacts', 'cognism_scraper')
            print(f"Using Cognism scraper at: {cognism_dir}")
            if not os.path.exists(cognism_dir):
                QMessageBox.critical(
                    self, "Error", f"Cognism scraper directory not found at: {cognism_dir}")
                return
            env_file = os.path.join(cognism_dir, '.env')
            if not os.path.exists(env_file):
                project_root = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))
                root_env_file = os.path.join(project_root, '.env')
                if os.path.exists(root_env_file):
                    import shutil
                    shutil.copy2(root_env_file, env_file)
                    print(
                        f"Copied .env file from {root_env_file} to {env_file}")
                else:
                    example_env = os.path.join(cognism_dir, 'example.env')
                    if os.path.exists(example_env):
                        import shutil
                        shutil.copy2(example_env, env_file)
                        print(f"Created .env file from example.env")
            self.cognism_status.setText(
                "Opening browser and waiting for login...")
            self.cognism_status.setStyleSheet(
                "font-size: 14px; color: orange; font-weight: bold; padding: 10px;")
            self.run_scraper_button.setEnabled(False)
            import sys
            original_path = sys.path.copy()
            sys.path.append(cognism_dir)
            sys.path.append(os.path.join(cognism_dir, "src"))

            def browser_thread():
                try:
                    from utils.selenium_setup import initialize_driver
                    from utils.auth import wait_for_manual_login
                    self.cognism_status.setText(
                        "Opening browser and waiting for login...")
                    driver = initialize_driver()
                    self.cognism_driver = driver
                    driver.get("https://app.cognism.com/auth/sign-in")
                    try:
                        from selenium.webdriver.common.by import By
                        from selenium.webdriver.support.ui import WebDriverWait
                        from selenium.webdriver.support import expected_conditions as EC
                        from config import COGNISM_EMAIL, COGNISM_PASSWORD
                        email_input = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//input[@formcontrolname='email']"))
                        )
                        password_input = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//input[@formcontrolname='password']"))
                        )
                        email_input.clear()
                        password_input.clear()
                        email_input.send_keys(COGNISM_EMAIL)
                        password_input.send_keys(COGNISM_PASSWORD)
                        print("Browser launched, credentials filled")
                    except Exception as e:
                        print(f"Error filling credentials: {str(e)}")
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
                    self.cognism_status.setText(
                        "Browser launched! Complete login if needed. Enter a contact tag and click Start Scraping.")
                    self.cognism_status.setStyleSheet(
                        "font-size: 14px; color: green; font-weight: bold; padding: 10px;")
                    self.start_scraping_button.setEnabled(True)
                except Exception as e:
                    print(f"Error during browser setup: {str(e)}")
                    self.cognism_status.setText(f"Login failed: {str(e)}")
                    self.cognism_status.setStyleSheet(
                        "font-size: 14px; color: red; font-weight: bold; padding: 10px;")
                    self.run_scraper_button.setEnabled(True)
            threading.Thread(target=browser_thread, daemon=True).start()
        except Exception as e:
            self.cognism_status.setText(f"Error: {str(e)}")
            self.cognism_status.setStyleSheet(
                "font-size: 14px; color: red; font-weight: bold; padding: 10px;")
            self.run_scraper_button.setEnabled(True)

    def run_cognism_url_scraping(self):
        try:
            contact_tag = self.contact_tag_input.text().strip()
            if not contact_tag:
                self.cognism_status.setText("Please enter a contact tag first")
                self.cognism_status.setStyleSheet(
                    "font-size: 14px; color: red; font-weight: bold; padding: 10px;")
                return
            if not self.cognism_driver:
                self.cognism_status.setText(
                    "Browser not initialized. Please start the process again.")
                self.cognism_status.setStyleSheet(
                    "font-size: 14px; color: red; font-weight: bold; padding: 10px;")
                self.run_scraper_button.setEnabled(True)
                self.start_scraping_button.setEnabled(False)
                return
            import threading
            self.cognism_status.setText(
                f"Scraping contacts with tag: {contact_tag}...")
            self.cognism_status.setStyleSheet(
                "font-size: 14px; color: orange; font-weight: bold; padding: 10px;")
            self.start_scraping_button.setEnabled(False)
            import sys
            project_root = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            cognism_dir = os.path.join(
                project_root, 'src', 'contacts', 'cognism_scraper')
            sys.path.append(cognism_dir)
            sys.path.append(os.path.join(cognism_dir, "src"))

            def scraper_thread():
                try:
                    try:
                        print("Starting URL scraping with tag:", contact_tag)
                        from utils_urls.url_navigation import navigate_and_scrape
                        navigate_and_scrape(self.cognism_driver, contact_tag)
                        from PyQt5.QtWidgets import QApplication
                        QApplication.processEvents()
                        self.cognism_status.setText(
                            "URLs scraped successfully! Now scraping contact details...")
                        self.cognism_status.setStyleSheet(
                            "font-size: 14px; color: blue; font-weight: bold; padding: 10px;")
                        print("Starting contact details scraping...")
                        from utils_contacts.database import save_to_db, print_db_path
                        from utils_contacts.scraper import scrape_page
                        from utils_contacts.read_db import get_urls_from_db
                        from utils_contacts.no_duplicates import filter_new_urls
                        from utils_contacts.navigate import open_new_tabs
                        from config import SCRAPING_DELAY
                        import time
                        login_tab = self.cognism_driver.current_window_handle
                        url_entries = filter_new_urls(contact_tag)
                        if not url_entries:
                            print(
                                "⚠️ No new URLs found. All entries already exist in the database.")
                        else:
                            urls = [entry["url"] for entry in url_entries]
                            print(
                                f"✅ {len(urls)} new URLs found and ready for processing.")
                            print(
                                f"Starting to process {len(urls)} URLs in batches")
                            batches = open_new_tabs(self.cognism_driver, urls)
                            for batch_index, tabs in enumerate(batches):
                                print(
                                    f"Processing batch {batch_index+1} with {len(tabs)} tabs")
                                print(f"Current tab handles: {tabs}")
                                for tab_index, tab in enumerate(tabs):
                                    try:
                                        self.cognism_driver.switch_to.window(
                                            tab)
                                        try:
                                            entry_index = (
                                                batch_index * len(tabs)) + tab_index
                                            if entry_index >= len(url_entries):
                                                print(
                                                    f"⚠️ Index {entry_index} is out of range (max: {len(url_entries)-1})")
                                                continue
                                            data_entry = url_entries[entry_index]
                                            current_url = self.cognism_driver.current_url
                                            print(
                                                f"Processing tab URL: {current_url}")
                                            self.cognism_status.setText(
                                                f"Scraping contact {entry_index + 1} of {len(urls)}...")
                                            QApplication.processEvents()
                                            extracted_data = scrape_page(
                                                self.cognism_driver)
                                        except Exception as index_error:
                                            print(
                                                f"⚠️ Error accessing data entry: {index_error}")
                                            continue
                                        if extracted_data and 'data_entry' in locals():
                                            extracted_data.update({
                                                "Segment": data_entry.get("segment", "unknown"),
                                                "Timestamp": data_entry.get("timestamp", "unknown"),
                                                "Cognism URL": data_entry.get("url", current_url if 'current_url' in locals() else "unknown")
                                            })
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
                                            save_to_db(corrected_data)
                                        else:
                                            print(
                                                f"⚠️ No data extracted for URL: {data_entry['url']}")
                                        time.sleep(SCRAPING_DELAY)
                                    except Exception as e:
                                        print(f"⚠️ Error processing tab: {e}")
                                for tab in tabs:
                                    try:
                                        self.cognism_driver.switch_to.window(
                                            tab)
                                        self.cognism_driver.close()
                                    except Exception as e:
                                        print(f"⚠️ Error closing tab: {e}")
                                try:
                                    self.cognism_driver.switch_to.window(
                                        login_tab)
                                except Exception as e:
                                    print(
                                        f"⚠️ Error switching back to login tab: {e}")
                            print("✅ Contact scraping completed.")
                    except Exception as e:
                        print(f"Error during scraping: {str(e)}")
                        raise
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
                    self.cognism_status.setText(
                        "URL and contact scraping completed successfully!")
                    self.cognism_status.setStyleSheet(
                        "font-size: 14px; color: green; font-weight: bold; padding: 10px;")
                    self.run_scraper_button.setEnabled(True)
                    self.start_scraping_button.setEnabled(False)
                    if self.cognism_driver:
                        try:
                            self.cognism_driver.quit()
                        except:
                            pass
                        self.cognism_driver = None
                except Exception as e:
                    print(f"Error during scraping: {str(e)}")
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
                    self.cognism_status.setText(f"Scraping failed: {str(e)}")
                    self.cognism_status.setStyleSheet(
                        "font-size: 14px; color: red; font-weight: bold; padding: 10px;")
                    self.run_scraper_button.setEnabled(True)
                    self.start_scraping_button.setEnabled(True)
                    if self.cognism_driver:
                        try:
                            self.cognism_driver.quit()
                        except:
                            pass
                        self.cognism_driver = None
            threading.Thread(target=scraper_thread, daemon=True).start()
        except Exception as e:
            self.cognism_status.setText(f"Error: {str(e)}")
            self.cognism_status.setStyleSheet(
                "font-size: 14px; color: red; font-weight: bold; padding: 10px;")
            self.start_scraping_button.setEnabled(True)

    def create_contacts_campaigns_menu(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        menu_group = QGroupBox("CONTACTS CAMPAIGNS")
        menu_group.setStyleSheet(
            "QGroupBox { font-size: 18px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        select_button = QPushButton("Select Existing Campaign")
        select_button.setStyleSheet("font-size: 16px; padding: 15px;")
        select_button.clicked.connect(self.run_contact_campaign_selector)
        menu_layout.addWidget(select_button)
        prospector_button = QPushButton("Run Contact Prospector")
        prospector_button.setStyleSheet("font-size: 16px; padding: 15px;")
        prospector_button.clicked.connect(self.run_contact_prospector)
        menu_layout.addWidget(prospector_button)
        back_button = QPushButton("Back to Contacts Menu")
        back_button.setStyleSheet("font-size: 16px; padding: 15px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.CONTACTS_MENU))
        menu_layout.addWidget(back_button)
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        return widget

    def run_contact_campaign_menu(self):
        self.stacked_widget.setCurrentIndex(self.CONTACTS_CAMPAIGNS_MENU)

    def run_contact_campaign_selector(self):
        try:
            import subprocess
            original_dir = os.getcwd()
            try:
                script_path = os.path.join(
                    contacts_dir, 'run_contact_campaign_gui.py')
                if not os.path.exists(script_path):
                    print(
                        f"Error: Could not find the contact campaign GUI script at {script_path}")
                    QMessageBox.critical(
                        self, "Error", f"Could not find the contact campaign GUI script at {script_path}")
                    return
                os.chdir(contacts_dir)
                subprocess.Popen([sys.executable, script_path])
            finally:
                os.chdir(original_dir)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error running contact campaign selector: {str(e)}")

    def run_contact_prospector(self):
        try:
            import subprocess
            original_dir = os.getcwd()
            try:
                script_path = os.path.join(
                    contacts_dir, 'run_contact_prospector.py')
                if not os.path.exists(script_path):
                    print(
                        f"Error: Could not find the contact prospector script at {script_path}")
                    QMessageBox.critical(
                        self, "Error", f"Could not find the contact prospector script at {script_path}")
                    return
                os.chdir(contacts_dir)
                subprocess.Popen([sys.executable, script_path])
            finally:
                os.chdir(original_dir)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error running contact prospector: {str(e)}")

    def create_phone_dialer_screen(self):
        from PyQt5.QtWidgets import (QPushButton, QHBoxLayout, QVBoxLayout,
                                     QWidget, QLabel, QComboBox, QGroupBox, QFormLayout)
        import sqlite3
        widget = QWidget()
        layout = QVBoxLayout(widget)
        header_label = QLabel("Phone Dialer")
        header_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin: 20px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        selection_group = QGroupBox("Campaign Selection")
        selection_group.setStyleSheet(
            "QGroupBox { font-size: 16px; font-weight: bold; }")
        form_layout = QFormLayout()
        self.company_campaign_combo = QComboBox()
        self.company_campaign_combo.setMinimumWidth(300)
        self.company_campaign_combo.setStyleSheet(
            "font-size: 14px; padding: 8px;")
        form_layout.addRow("Company Campaign:", self.company_campaign_combo)
        self.contact_batch_combo = QComboBox()
        self.contact_batch_combo.setMinimumWidth(300)
        self.contact_batch_combo.setStyleSheet(
            "font-size: 14px; padding: 8px;")
        form_layout.addRow("Contact Campaign Batch Tag:",
                           self.contact_batch_combo)
        load_btn = QPushButton("Load Campaigns")
        load_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        load_btn.clicked.connect(self.load_phone_dialer_campaigns)
        form_layout.addRow("", load_btn)
        selection_group.setLayout(form_layout)
        layout.addWidget(selection_group)
        proceed_btn = QPushButton("Proceed")
        proceed_btn.setStyleSheet(
            "font-size: 16px; padding: 12px; "
            "background-color: #4CAF50; color: white; "
            "border-radius: 5px; font-weight: bold;"
        )
        proceed_btn.setMinimumWidth(200)
        proceed_btn.clicked.connect(self.start_phone_dialer)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(proceed_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()
        back_button = QPushButton("Back to Main Menu")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.MAIN_MENU))
        layout.addWidget(back_button)
        return widget

    def load_phone_dialer_campaigns(self):
        from phone_dialer import PhoneDialerApp
        self.phone_dialer = PhoneDialerApp(parent=self)
        self.phone_dialer.load_campaigns(
            self.company_campaign_combo, self.contact_batch_combo)

    def start_phone_dialer(self):
        from PyQt5.QtWidgets import QMessageBox
        from phone_dialer import PhoneDialerApp
        if not hasattr(self, 'phone_dialer'):
            self.phone_dialer = PhoneDialerApp(parent=self)
        campaign_id = self.company_campaign_combo.currentData()
        if not campaign_id:
            QMessageBox.warning(self, "No Campaign Selected",
                                "Please select a company campaign first.")
            return
        campaign_name = self.company_campaign_combo.currentText().split(
            " - ")[0]
        batch_tag = self.contact_batch_combo.currentData()
        if not batch_tag:
            batch_tag = "all"
        if self.phone_dialer.load_contacts(campaign_id, batch_tag):
            self.phone_dialer.show_contacts_dialog(campaign_name, batch_tag)


def start_app_menu():
    """Start the GUI application."""
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    initialize_app()
    start_app_menu()
