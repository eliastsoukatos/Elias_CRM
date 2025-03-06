import sys
import os
import uuid
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QLabel, QHBoxLayout, 
                           QGroupBox, QLineEdit, QSpinBox, QCheckBox,
                           QMessageBox, QListWidget, QDialog, QFormLayout)
from PyQt5.QtCore import Qt

# Set up path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the necessary scraper functions
from clutch_scraper import run_clutch_scraper
from db_initializer import check_for_database

class ClutchScraperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clutch Scraper Configuration")
        self.setMinimumWidth(500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create form for parameters
        form_group = QGroupBox("Scraper Parameters")
        form_layout = QFormLayout()
        
        # Number of companies
        self.companies_spin = QSpinBox()
        self.companies_spin.setMinimum(1)
        self.companies_spin.setMaximum(50000)
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
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        run_button = QPushButton("Run Scraper")
        run_button.clicked.connect(self.accept)
        run_button.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(run_button)
        
        layout.addLayout(button_layout)
    
    def add_url(self):
        url = self.url_input.text().strip()
        if url:
            if url.startswith("http://") or url.startswith("https://"):
                self.url_list.addItem(url)
                self.url_input.clear()
            else:
                QMessageBox.warning(self, "Invalid URL", "URL must start with http:// or https://")
    
    def remove_url(self):
        selected_items = self.url_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            row = self.url_list.row(item)
            self.url_list.takeItem(row)
    
    def get_parameters(self):
        # Get all URLs from list
        urls = []
        for i in range(self.url_list.count()):
            urls.append(self.url_list.item(i).text())
        
        # Generate a unique batch ID
        batch_id = str(uuid.uuid4())
        
        return {
            "num_companies": self.companies_spin.value(),
            "extract_portfolio": self.portfolio_check.isChecked(),
            "extract_reviews": self.reviews_check.isChecked(),
            "num_reviews": self.reviews_spin.value(),
            "urls": urls,
            "batch_tag": self.batch_tag.text(),
            "batch_id": batch_id
        }

class ScraperSelectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scraper Selector")
        self.setMinimumSize(600, 400)
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("Available Scrapers")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Scrapers group
        scrapers_group = QGroupBox("Select a Scraper")
        scrapers_layout = QVBoxLayout()
        
        # Clutch Scraper button
        clutch_button = QPushButton("Clutch Scraper")
        clutch_button.setStyleSheet("font-size: 16px; padding: 20px;")
        clutch_button.clicked.connect(self.run_clutch_scraper)
        scrapers_layout.addWidget(clutch_button)
        
        # Future scrapers (disabled)
        future_button1 = QPushButton("LinkedIn Scraper (Coming Soon)")
        future_button1.setStyleSheet("font-size: 16px; padding: 20px;")
        future_button1.setEnabled(False)
        scrapers_layout.addWidget(future_button1)
        
        future_button2 = QPushButton("Twitter Scraper (Coming Soon)")
        future_button2.setStyleSheet("font-size: 16px; padding: 20px;")
        future_button2.setEnabled(False)
        scrapers_layout.addWidget(future_button2)
        
        scrapers_group.setLayout(scrapers_layout)
        main_layout.addWidget(scrapers_group)
        
        # Back button
        back_button = QPushButton("Close")
        back_button.setStyleSheet("font-size: 14px; padding: 10px;")
        back_button.clicked.connect(self.close)
        main_layout.addWidget(back_button)
    
    def run_clutch_scraper(self):
        # Check database first
        if not check_for_database():
            QMessageBox.critical(self, "Error", "Database not found or initialization failed.")
            return
        
        # Open the Clutch scraper configuration dialog
        dialog = ClutchScraperDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            params = dialog.get_parameters()
            
            # Validate parameters
            if not params["urls"]:
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
                try:
                    # Show a progress message
                    progress_msg = QMessageBox(self)
                    progress_msg.setWindowTitle("Scraper Running")
                    progress_msg.setText("The scraper is running. This may take a while.\n\nPlease check the terminal for progress updates.")
                    progress_msg.setStandardButtons(QMessageBox.NoButton)
                    progress_msg.show()
                    
                    # Update the UI
                    QApplication.processEvents()
                    
                    # Run the scraper
                    run_clutch_scraper(
                        startUrls=params['urls'],
                        maxItems=params['num_companies'],
                        excludePortfolio=not params['extract_portfolio'],
                        includeReviews=params['extract_reviews'],
                        maxReviewsPerCompany=params['num_reviews'],
                        batch_tag=params['batch_tag'],
                        batch_id=params['batch_id']
                    )
                    
                    # Close the progress message
                    progress_msg.close()
                    
                    # Show success message
                    QMessageBox.information(self, "Scraper Completed", 
                                         f"Scraper completed successfully!\n\nBatch ID: {params['batch_id']}")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error during scraping: {str(e)}")

def run_scraper_selector():
    app = QApplication(sys.argv)
    window = ScraperSelectorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_scraper_selector()