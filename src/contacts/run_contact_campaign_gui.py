import os
import sys
import sqlite3
from datetime import datetime
import uuid
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QWidget, QLabel, QGroupBox, QComboBox,
                           QMessageBox, QTextEdit, QCheckBox, QDialog, QFormLayout,
                           QLineEdit, QSpinBox, QListWidget, QListWidgetItem, QTableWidget,
                           QTableWidgetItem, QHeaderView, QAbstractItemView, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Make the database path accessible - use platform-independent path
def get_db_path():
    """Determine the appropriate database path"""
    # Try multiple potential project root locations
    
    # First try from our file
    file_dir = os.path.dirname(os.path.abspath(__file__))
    contacts_dir = file_dir
    src_dir = os.path.dirname(contacts_dir)
    project_root = os.path.dirname(src_dir)
    
    # Try the project root first
    db_dir = os.path.join(project_root, 'databases')
    db_path = os.path.join(db_dir, 'database.db')
    
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created database directory: {db_dir}")
        except Exception as e:
            print(f"Could not create database directory: {e}")
            
            # Try user's home directory as fallback
            user_home = os.path.expanduser("~")
            db_dir = os.path.join(user_home, 'databases')
            db_path = os.path.join(db_dir, 'database.db')
            
            if not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                    print(f"Created fallback database directory in user home: {db_dir}")
                except Exception as e2:
                    print(f"Error creating fallback directory: {e2}")
    
    print(f"Using database at: {db_path}")
    return db_path

# Get the database path
db_path = get_db_path()

class ContactCampaignWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contact Campaign Management")
        self.setMinimumSize(1000, 700)
        
        # Initialize variables
        self.selected_campaign_id = None
        self.selected_campaign_name = None
        self.selected_batch_id = None
        
        # Create UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create campaign selection section
        campaign_group = QGroupBox("Campaign Selection")
        campaign_layout = QVBoxLayout()
        
        # Campaign list with headers
        self.campaign_list = QTableWidget()
        self.campaign_list.setColumnCount(4)
        self.campaign_list.setHorizontalHeaderLabels(["ID", "Campaign Name", "Created Date", "Total Contacts"])
        self.campaign_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.campaign_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.campaign_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.campaign_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.campaign_list.selectionModel().selectionChanged.connect(self.on_campaign_selected)
        campaign_layout.addWidget(self.campaign_list)
        
        # Campaign stats section
        stats_layout = QHBoxLayout()
        self.total_contacts_label = QLabel("Total Contacts: 0")
        self.approved_contacts_label = QLabel("Approved: 0")
        self.rejected_contacts_label = QLabel("Rejected: 0")
        self.undecided_contacts_label = QLabel("Undecided: 0")
        
        stats_layout.addWidget(self.total_contacts_label)
        stats_layout.addWidget(self.approved_contacts_label)
        stats_layout.addWidget(self.rejected_contacts_label)
        stats_layout.addWidget(self.undecided_contacts_label)
        campaign_layout.addLayout(stats_layout)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Campaign List")
        refresh_button.clicked.connect(self.load_campaigns)
        campaign_layout.addWidget(refresh_button)
        
        campaign_group.setLayout(campaign_layout)
        main_layout.addWidget(campaign_group)
        
        # Actions group
        actions_group = QGroupBox("Contact Actions")
        actions_layout = QVBoxLayout()
        
        # Add contacts to campaign button
        add_contacts_button = QPushButton("Add Contacts to Campaign")
        add_contacts_button.clicked.connect(self.add_contacts_to_campaign)
        add_contacts_button.setEnabled(False)
        actions_layout.addWidget(add_contacts_button)
        
        # View batch tags button
        view_tags_button = QPushButton("View Batch Tags")
        view_tags_button.clicked.connect(self.view_batch_tags)
        view_tags_button.setEnabled(False)
        actions_layout.addWidget(view_tags_button)
        
        # Run contact prospector button
        run_prospector_button = QPushButton("Run Contact Prospector")
        run_prospector_button.clicked.connect(self.run_contact_prospector)
        run_prospector_button.setEnabled(False)
        actions_layout.addWidget(run_prospector_button)
        
        # Add clear campaign button
        clear_campaign_button = QPushButton("Clear Campaign Contacts")
        clear_campaign_button.clicked.connect(self.clear_campaign_contacts)
        clear_campaign_button.setEnabled(False)
        clear_campaign_button.setStyleSheet("background-color: #f44336; color: white;")
        actions_layout.addWidget(clear_campaign_button)
        
        # Store buttons for enabling/disabling
        self.action_buttons = [add_contacts_button, view_tags_button, run_prospector_button, clear_campaign_button]
        
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)
        
        # Load campaigns
        self.load_campaigns()
        
    def load_campaigns(self):
        """Load campaigns from the database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Query campaigns with contact counts
            cursor.execute("""
                SELECT 
                    c.campaign_id, 
                    c.campaign_name, 
                    c.created_at,
                    (SELECT COUNT(*) FROM contacts_campaign cc WHERE cc.campaign_id = c.campaign_id) as contact_count
                FROM campaigns c
                ORDER BY c.created_at DESC
            """)
            
            campaigns = cursor.fetchall()
            conn.close()
            
            # Clear the table
            self.campaign_list.setRowCount(0)
            
            # Add campaigns to the table
            for row, campaign in enumerate(campaigns):
                campaign_id, name, created_at, contact_count = campaign
                
                self.campaign_list.insertRow(row)
                self.campaign_list.setItem(row, 0, QTableWidgetItem(str(campaign_id)))
                self.campaign_list.setItem(row, 1, QTableWidgetItem(name))
                self.campaign_list.setItem(row, 2, QTableWidgetItem(created_at))
                self.campaign_list.setItem(row, 3, QTableWidgetItem(str(contact_count)))
                
            # Adjust column widths
            self.campaign_list.resizeColumnsToContents()
            
            # Reset selection
            self.selected_campaign_id = None
            self.selected_campaign_name = None
            self.update_campaign_stats()
            
            # Disable action buttons
            for button in self.action_buttons:
                button.setEnabled(False)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading campaigns: {str(e)}")
    
    def on_campaign_selected(self):
        """Handle campaign selection."""
        selected_items = self.campaign_list.selectedItems()
        if not selected_items:
            # Disable action buttons when no campaign is selected
            for button in self.action_buttons:
                button.setEnabled(False)
            return
        
        # Get campaign ID from the first column
        row = selected_items[0].row()
        campaign_id_item = self.campaign_list.item(row, 0)
        campaign_name_item = self.campaign_list.item(row, 1)
        
        if campaign_id_item:
            self.selected_campaign_id = int(campaign_id_item.text())
            self.selected_campaign_name = campaign_name_item.text()
            
            # Update campaign stats
            self.update_campaign_stats()
            
            # Enable action buttons
            for button in self.action_buttons:
                button.setEnabled(True)
    
    def update_campaign_stats(self):
        """Update campaign statistics display."""
        if not self.selected_campaign_id:
            # Reset stats
            self.total_contacts_label.setText("Total Contacts: 0")
            self.approved_contacts_label.setText("Approved: 0")
            self.rejected_contacts_label.setText("Rejected: 0")
            self.undecided_contacts_label.setText("Undecided: 0")
            return
        
        try:
            # Get stats from database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Total contacts
            cursor.execute(
                "SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ?", 
                (self.selected_campaign_id,)
            )
            total = cursor.fetchone()[0]
            
            # Approved contacts
            cursor.execute(
                "SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ? AND current_state = 'approved'", 
                (self.selected_campaign_id,)
            )
            approved = cursor.fetchone()[0]
            
            # Rejected contacts
            cursor.execute(
                "SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ? AND current_state = 'rejected'", 
                (self.selected_campaign_id,)
            )
            rejected = cursor.fetchone()[0]
            
            # Undecided contacts
            cursor.execute(
                "SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ? AND current_state = 'undecided'", 
                (self.selected_campaign_id,)
            )
            undecided = cursor.fetchone()[0]
            
            conn.close()
            
            # Update labels
            self.total_contacts_label.setText(f"Total Contacts: {total}")
            self.approved_contacts_label.setText(f"Approved: {approved}")
            self.rejected_contacts_label.setText(f"Rejected: {rejected}")
            self.undecided_contacts_label.setText(f"Undecided: {undecided}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating campaign stats: {str(e)}")
    
    def add_contacts_to_campaign(self):
        """Add contacts to the selected campaign."""
        if not self.selected_campaign_id:
            QMessageBox.warning(self, "No Campaign Selected", "Please select a campaign first.")
            return
        
        # Launch the contact search dialog
        self.search_and_add_contacts_dialog = SearchContactsDialog(self.selected_campaign_id, self.selected_campaign_name)
        self.search_and_add_contacts_dialog.contactsAdded.connect(self.update_campaign_stats)
        self.search_and_add_contacts_dialog.show()
    
    def view_batch_tags(self):
        """View batch tags for the selected campaign."""
        if not self.selected_campaign_id:
            QMessageBox.warning(self, "No Campaign Selected", "Please select a campaign first.")
            return
            
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Query distinct batch tags and their contact counts
            cursor.execute("""
                SELECT 
                    campaign_batch_tag,
                    COUNT(contact_id) as total_contacts,
                    COUNT(CASE WHEN current_state = 'approved' THEN 1 END) as approved_contacts,
                    COUNT(CASE WHEN current_state = 'rejected' THEN 1 END) as rejected_contacts,
                    COUNT(CASE WHEN current_state = 'undecided' THEN 1 END) as undecided_contacts,
                    MIN(added_at) as first_added
                FROM contacts_campaign
                WHERE campaign_id = ?
                GROUP BY campaign_batch_tag
                ORDER BY MIN(added_at) DESC
            """, (self.selected_campaign_id,))
            
            batch_tags = cursor.fetchall()
            conn.close()
            
            if not batch_tags:
                QMessageBox.information(self, "No Batch Tags", "No batch tags found for this campaign.")
                return
                
            # Create a dialog to display the batch tags
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Batch Tags for {self.selected_campaign_name}")
            dialog.setMinimumWidth(800)
            dialog.setMinimumHeight(400)
            
            # Create layout
            layout = QVBoxLayout(dialog)
            
            # Create table for batch tags
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels([
                "Batch Tag", "Total Contacts", "Approved", "Rejected", "Undecided", "Date Added"
            ])
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            layout.addWidget(table)
            
            # Populate table
            table.setRowCount(len(batch_tags))
            for row, tag_data in enumerate(batch_tags):
                tag, total, approved, rejected, undecided, date_added = tag_data
                
                table.setItem(row, 0, QTableWidgetItem(tag))
                table.setItem(row, 1, QTableWidgetItem(str(total)))
                table.setItem(row, 2, QTableWidgetItem(str(approved)))
                table.setItem(row, 3, QTableWidgetItem(str(rejected)))
                table.setItem(row, 4, QTableWidgetItem(str(undecided)))
                table.setItem(row, 5, QTableWidgetItem(date_added))
            
            # Add close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            
            # Show dialog
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error viewing batch tags: {str(e)}")
    
    def run_contact_prospector(self):
        """Launch the contact prospector for the selected campaign."""
        if not self.selected_campaign_id:
            QMessageBox.warning(self, "No Campaign Selected", "Please select a campaign first.")
            return
        
        try:
            # Launch contact prospector as a separate process
            import subprocess
            
            # Path to contact prospector script
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_contact_prospector.py')
            
            # Check if the file exists
            if not os.path.exists(script_path):
                QMessageBox.critical(self, "Error", f"Could not find the contact prospector script at {script_path}")
                return
            
            # Launch the prospector with the campaign ID
            subprocess.Popen([sys.executable, script_path, str(self.selected_campaign_id)])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error launching contact prospector: {str(e)}")
            
    def clear_campaign_contacts(self):
        """Clear all contacts from the selected campaign."""
        if not self.selected_campaign_id:
            QMessageBox.warning(self, "No Campaign Selected", "Please select a campaign first.")
            return
        
        # Confirm with user
        confirm = QMessageBox.question(
            self,
            "Clear Campaign Contacts",
            f"Are you sure you want to remove ALL contacts from campaign '{self.selected_campaign_name}'?\n\n"
            "This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get current count
            cursor.execute(
                "SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ?", 
                (self.selected_campaign_id,)
            )
            count = cursor.fetchone()[0]
            
            # Delete all contacts in the campaign
            cursor.execute(
                "DELETE FROM contacts_campaign WHERE campaign_id = ?",
                (self.selected_campaign_id,)
            )
            
            conn.commit()
            conn.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Campaign Cleared",
                f"Successfully removed {count} contacts from campaign '{self.selected_campaign_name}'."
            )
            
            # Refresh campaign stats
            self.update_campaign_stats()
            self.load_campaigns()  # Reload campaign list to update counts
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error clearing campaign contacts: {str(e)}")


class SearchContactsDialog(QDialog):
    # Define a custom signal that will be emitted when contacts are added
    from PyQt5.QtCore import pyqtSignal
    contactsAdded = pyqtSignal()
    
    def __init__(self, campaign_id, campaign_name):
        super().__init__()
        self.campaign_id = campaign_id
        self.campaign_name = campaign_name
        self.setWindowTitle(f"Add Contacts to Campaign: {campaign_name}")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.load_approved_companies()
        
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"Add Contacts to Campaign: {self.campaign_name}")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header_label)
        
        # SQL Query controls
        query_group = QGroupBox("SQL Query for Contacts")
        query_layout = QVBoxLayout()
        
        # Company info
        self.company_count_label = QLabel("Loading approved companies...")
        query_layout.addWidget(self.company_count_label)
        
        # Contact tag filter
        tag_filter_layout = QHBoxLayout()
        tag_filter_layout.addWidget(QLabel("Filter by Contact Tag:"))
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("All Tags", "all")
        tag_filter_layout.addWidget(self.tag_filter_combo)
        
        load_tags_button = QPushButton("Load Tags")
        load_tags_button.clicked.connect(self.load_contact_tags)
        tag_filter_layout.addWidget(load_tags_button)
        
        query_layout.addLayout(tag_filter_layout)
        
        # SQL Query input
        query_label = QLabel("SQL Query (contacts from approved companies in this campaign):")
        query_layout.addWidget(query_label)
        
        from PyQt5.QtWidgets import QPlainTextEdit
        self.query_input = QPlainTextEdit()
        self.query_input.setMinimumHeight(100)
        self.query_input.setPlaceholderText(
            "SELECT c.contact_id, c.Name, c.Last_Name, c.Role, c.Email, c.LinkedIn_URL, co.name as company_name\n"
            "FROM contacts c\n"
            "JOIN companies co ON c.company_id = co.company_id\n"
            "WHERE c.company_id IN (SELECT company_id FROM companies_campaign WHERE campaign_id = {} AND current_state = 'approved')\n"
            "-- Add additional conditions if needed\n"
            "ORDER BY c.Name, c.Last_Name".format(self.campaign_id)
        )
        query_layout.addWidget(self.query_input)
        
        query_help = QLabel("NOTE: Query must return contact_id, Name, Last_Name, Role, Email, LinkedIn_URL, and company_name.")
        query_help.setStyleSheet("color: gray; font-style: italic;")
        query_layout.addWidget(query_help)
        
        # Apply tag filter button
        apply_tag_button = QPushButton("Apply Tag Filter")
        apply_tag_button.clicked.connect(self.apply_tag_filter)
        query_layout.addWidget(apply_tag_button)
        
        # Run query button
        run_query_button = QPushButton("Run Query")
        run_query_button.clicked.connect(self.run_sql_query)
        run_query_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        query_layout.addWidget(run_query_button)
        
        query_group.setLayout(query_layout)
        layout.addWidget(query_group)
        
        # Results table
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["ID", "Name", "Role", "Email", "Company", "Select"])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Selection controls
        selection_layout = QHBoxLayout()
        
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all_contacts)
        selection_layout.addWidget(select_all_button)
        
        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.clicked.connect(self.deselect_all_contacts)
        selection_layout.addWidget(deselect_all_button)
        
        selection_layout.addStretch()
        
        # Add selected button
        add_selected_button = QPushButton("Add Selected Contacts")
        add_selected_button.clicked.connect(self.add_selected_contacts)
        add_selected_button.setStyleSheet("background-color: #4CAF50; color: white;")
        selection_layout.addWidget(add_selected_button)
        
        layout.addLayout(selection_layout)
        
        # Bottom buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_approved_companies(self):
        """Load approved companies for the selected campaign."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get approved companies for this campaign
            cursor.execute(
                """
                SELECT company_id 
                FROM companies_campaign 
                WHERE campaign_id = ? AND current_state = 'approved'
                """, 
                (self.campaign_id,)
            )
            
            approved_companies = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            self.approved_company_ids = approved_companies
            self.company_count_label.setText(f"Found {len(approved_companies)} approved companies in this campaign.")
            
            if not approved_companies:
                QMessageBox.warning(
                    self, 
                    "No Approved Companies", 
                    "There are no approved companies in this campaign. Please approve companies in the Company Prospector first."
                )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading approved companies: {str(e)}")
    
    def load_contact_tags(self):
        """Load available contact tags"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Query for distinct contact tags
            cursor.execute("""
                SELECT DISTINCT contact_tag, COUNT(*) as count
                FROM contacts_cognism_urls
                JOIN contacts ON contacts_cognism_urls.contact_id = contacts.contact_id
                WHERE contacts.company_id IN ({})
                GROUP BY contact_tag
                ORDER BY contact_tag
            """.format(','.join(['?'] * len(self.approved_company_ids))), self.approved_company_ids)
            
            tags = cursor.fetchall()
            conn.close()
            
            # Clear existing items first (except "All Tags")
            self.tag_filter_combo.clear()
            self.tag_filter_combo.addItem("All Tags", "all")
            
            if not tags:
                QMessageBox.information(self, "No Tags", "No contact tags found for contacts in approved companies.")
                return
                
            # Add tags to combo box
            for tag, count in tags:
                if tag:  # Only add non-empty tags
                    self.tag_filter_combo.addItem(f"{tag} ({count} contacts)", tag)
            
            QMessageBox.information(self, "Tags Loaded", f"Loaded {len(tags)} contact tags.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading contact tags: {str(e)}")
    
    def apply_tag_filter(self):
        """Apply the selected tag filter to the SQL query"""
        selected_tag = self.tag_filter_combo.currentData()
        
        if selected_tag == "all":
            QMessageBox.information(self, "No Filter Applied", "Using all contacts (no tag filter).")
            return
            
        # Get current query text
        current_query = self.query_input.toPlainText().strip()
        
        # Check if there's already a JOIN to contacts_cognism_urls
        has_join = "JOIN contacts_cognism_urls" in current_query
        
        # Create base query template if query is empty
        if not current_query:
            current_query = """SELECT c.contact_id, c.Name, c.Last_Name, c.Role, c.Email, c.LinkedIn_URL, co.name as company_name
FROM contacts c
JOIN companies co ON c.company_id = co.company_id
WHERE c.company_id IN (SELECT company_id FROM companies_campaign WHERE campaign_id = {} AND current_state = 'approved')
ORDER BY c.Name, c.Last_Name""".format(self.campaign_id)
        
        # Split query into parts to insert the JOIN and WHERE clause
        lines = current_query.split('\n')
        
        # Find the FROM line and WHERE line
        from_index = -1
        where_index = -1
        
        for i, line in enumerate(lines):
            if line.strip().upper().startswith("FROM"):
                from_index = i
            elif line.strip().upper().startswith("WHERE"):
                where_index = i
                
        if from_index == -1 or where_index == -1:
            QMessageBox.warning(self, "Invalid Query", "Could not parse query. Please ensure it has FROM and WHERE clauses.")
            return
            
        # If there's already a JOIN to contacts_cognism_urls, replace the condition
        if has_join:
            for i, line in enumerate(lines):
                if "contacts_cognism_urls.contact_tag" in line:
                    lines[i] = "    AND contacts_cognism_urls.contact_tag = '{}' -- Tag filter".format(selected_tag)
                    break
        else:
            # Insert JOIN after the FROM section
            join_line = "JOIN contacts_cognism_urls ON c.contact_id = contacts_cognism_urls.contact_id -- Tag filter"
            
            # Find the last JOIN line
            last_join_index = from_index
            for i in range(from_index + 1, where_index):
                if "JOIN" in lines[i]:
                    last_join_index = i
                    
            # Insert after the last JOIN
            lines.insert(last_join_index + 1, join_line)
            
            # Add WHERE condition
            where_clause = "    AND contacts_cognism_urls.contact_tag = '{}' -- Tag filter".format(selected_tag)
            lines.insert(where_index + 1, where_clause)
            
        # Rebuild the query
        new_query = '\n'.join(lines)
        
        # Update the query input
        self.query_input.setPlainText(new_query)
        
        QMessageBox.information(self, "Tag Filter Applied", f"Query updated to filter for tag: {selected_tag}")
    
    def run_sql_query(self):
        """Run custom SQL query to find contacts"""
        if not hasattr(self, 'approved_company_ids') or not self.approved_company_ids:
            QMessageBox.warning(self, "No Companies", "No approved companies found for this campaign.")
            return
        
        # Get query from input
        query = self.query_input.toPlainText().strip()
        
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter an SQL query.")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check which contacts are already in the campaign
            cursor.execute(
                """
                SELECT contact_id 
                FROM contacts_campaign 
                WHERE campaign_id = ?
                """, 
                (self.campaign_id,)
            )
            
            existing_contacts = set(row[0] for row in cursor.fetchall())
            
            # Execute the custom query
            cursor.execute(query)
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Check required columns
            required_columns = ['contact_id', 'Name', 'Last_Name', 'Role', 'Email', 'LinkedIn_URL', 'company_name']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                QMessageBox.critical(self, "Invalid Query Results", 
                                    f"Query results are missing required columns: {', '.join(missing_columns)}.\n\n"
                                    f"Query must return: {', '.join(required_columns)}")
                conn.close()
                return
            
            contacts = cursor.fetchall()
            conn.close()
            
            if not contacts:
                QMessageBox.information(self, "No Results", "No contacts found matching your query.")
                return
            
            # Clear the table
            self.results_table.setRowCount(0)
            
            # Get column indices
            id_idx = column_names.index('contact_id')
            name_idx = column_names.index('Name')
            last_name_idx = column_names.index('Last_Name')
            role_idx = column_names.index('Role')
            email_idx = column_names.index('Email')
            company_idx = column_names.index('company_name')
            
            # Add contacts to the table
            for row, contact in enumerate(contacts):
                contact_id = contact[id_idx]
                first_name = contact[name_idx] or ""
                last_name = contact[last_name_idx] or ""
                role = contact[role_idx] or ""
                email = contact[email_idx] or ""
                company_name = contact[company_idx] or ""
                
                # Create full name
                name = f"{first_name} {last_name}" if last_name else first_name
                
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(str(contact_id)))
                self.results_table.setItem(row, 1, QTableWidgetItem(name))
                self.results_table.setItem(row, 2, QTableWidgetItem(role))
                self.results_table.setItem(row, 3, QTableWidgetItem(email))
                self.results_table.setItem(row, 4, QTableWidgetItem(company_name))
                
                # Add checkbox (disabled if contact already in campaign)
                checkbox = QWidget()
                checkbox_layout = QHBoxLayout(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                
                checkbox_item = QCheckBox()
                
                # Disable if contact already in campaign
                if str(contact_id) in existing_contacts:
                    checkbox_item.setEnabled(False)
                    checkbox_item.setChecked(True)
                    checkbox_item.setToolTip("Contact already in campaign")
                
                checkbox_layout.addWidget(checkbox_item)
                self.results_table.setCellWidget(row, 5, checkbox)
            
            # Adjust column widths
            self.results_table.resizeColumnsToContents()
            
            # Show count
            QMessageBox.information(self, "Query Results", f"Found {len(contacts)} contacts matching your query.")
            
        except Exception as e:
            QMessageBox.critical(self, "SQL Error", f"Error executing query: {str(e)}")
            
    def search_contacts(self):
        """Legacy search method - notify user to use SQL query instead"""
        QMessageBox.information(
            self, 
            "Use SQL Query", 
            "Please use the SQL Query feature instead of the simple search.\n\n"
            "You can filter by contact tag and write custom queries."
        )
    
    def select_all_contacts(self):
        """Select all contacts in the results table."""
        for row in range(self.results_table.rowCount()):
            checkbox_widget = self.results_table.cellWidget(row, 5)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isEnabled():
                    checkbox.setChecked(True)
    
    def deselect_all_contacts(self):
        """Deselect all contacts in the results table."""
        for row in range(self.results_table.rowCount()):
            checkbox_widget = self.results_table.cellWidget(row, 5)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isEnabled():
                    checkbox.setChecked(False)
    
    def add_selected_contacts(self):
        """Add selected contacts to the campaign."""
        # Collect selected contact IDs
        selected_contact_ids = []
        
        for row in range(self.results_table.rowCount()):
            checkbox_widget = self.results_table.cellWidget(row, 5)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked() and checkbox.isEnabled():
                    contact_id = self.results_table.item(row, 0).text()
                    selected_contact_ids.append(contact_id)
        
        if not selected_contact_ids:
            QMessageBox.warning(self, "No Contacts Selected", "Please select at least one contact to add.")
            return
        
        # Ask for batch tag
        from PyQt5.QtWidgets import QInputDialog, QLineEdit
        batch_tag, ok = QInputDialog.getText(
            self, 
            "Enter Batch Tag", 
            "Please enter a batch tag to identify this group of contacts:",
            QLineEdit.Normal,
            ""
        )
        
        if not ok:
            return  # User canceled
            
        if not batch_tag.strip():
            # If empty, use a default tag with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_tag = f"manual_add_{timestamp}"
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Generate batch identifier
            batch_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add each contact to the campaign
            added_count = 0
            
            for contact_id in selected_contact_ids:
                try:
                    # Get company_id for this contact
                    cursor.execute(
                        "SELECT company_id FROM contacts WHERE contact_id = ?",
                        (contact_id,)
                    )
                    result = cursor.fetchone()
                    company_id = result[0] if result else None
                    
                    cursor.execute(
                        """
                        INSERT INTO contacts_campaign 
                        (contact_id, campaign_id, campaign_name, campaign_batch_tag, campaign_batch_id, company_id, notes) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (contact_id, self.campaign_id, self.campaign_name, batch_tag, batch_id, company_id, "")
                    )
                    added_count += 1
                except sqlite3.IntegrityError:
                    # Contact already in campaign (should not happen due to disabled checkbox)
                    pass
            
            # Add batch to import logs
            cursor.execute(
                "INSERT INTO import_logs (batch_tag, batch_id, source, timestamp) VALUES (?, ?, ?, ?)",
                (batch_tag, batch_id, "manual_contact_add", timestamp)
            )
            
            conn.commit()
            conn.close()
            
            # Show success message
            QMessageBox.information(
                self, 
                "Contacts Added", 
                f"Successfully added {added_count} contacts to campaign '{self.campaign_name}'.\nBatch Tag: {batch_tag}"
            )
            
            # Emit signal that contacts were added (to update stats)
            self.contactsAdded.emit()
            
            # Close the dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding contacts to campaign: {str(e)}")


def run_contact_campaign_gui():
    """Run the contact campaign GUI application."""
    app = QApplication(sys.argv)
    window = ContactCampaignWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_contact_campaign_gui()