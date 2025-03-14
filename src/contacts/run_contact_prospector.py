import os
import sys
import sqlite3
import webbrowser
import time
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QGroupBox, QComboBox,
                             QMessageBox, QTextEdit, QCheckBox, QDialog, QFormLayout,
                             QLineEdit, QSpinBox, QStyleFactory, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

# Import selenium for browser control
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. Will use basic webbrowser module instead.")

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Make the database path accessible - use absolute path for reliability
db_path = "/Users/anthonyhurtado/Jobs/personal/others/Elias_CRM/databases/database.db"

# Verify database path exists
if not os.path.exists(db_path):
    print(f"ERROR: Database not found at {db_path}")

    # Try to find it using relative path
    fallback_path = os.path.join(project_root, 'databases', 'database.db')
    if os.path.exists(fallback_path):
        print(f"Using fallback database path: {fallback_path}")
        db_path = fallback_path
    else:
        print(f"Fallback database path not found either: {fallback_path}")

print(f"Using database at: {db_path}")


def get_campaigns():
    """Get all campaigns from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT campaign_id, campaign_name, created_at FROM campaigns ORDER BY created_at DESC")
    campaigns = cursor.fetchall()

    conn.close()
    return campaigns


def get_campaign_contacts(campaign_id, state='undecided', batch_id=None):
    """Get all contacts for a given campaign with specified state."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT 
        cc.counter,
        c.id,
        c.Name,
        c.Last_Name,
        c.Role,
        c.Email,
        c.Mobile_Phone,
        c.LinkedIn_URL,
        c.City,
        c.State,
        c.Country,
        co.name as company_name,
        co.website,
        cc.current_state,
        cc.reason,
        cc.campaign_batch_id,
        cc.notes
    FROM contacts_campaign cc
    JOIN contacts c ON cc.contact_id = c.contact_id
    LEFT JOIN companies co ON c.company_id = co.company_id
    WHERE cc.campaign_id = ? AND cc.current_state = ?
    """

    params = [campaign_id, state]

    if batch_id:
        query += " AND cc.campaign_batch_id = ?"
        params.append(batch_id)

    cursor.execute(query, params)
    contacts = cursor.fetchall()

    conn.close()
    return contacts


def get_campaign_batches(campaign_id):
    """Get all batches for a campaign."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT campaign_batch_id, campaign_batch_tag, 
    (SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ? AND campaign_batch_id = cc.campaign_batch_id) as count
    FROM contacts_campaign cc
    WHERE cc.campaign_id = ?
    ORDER BY cc.added_at DESC
    """, (campaign_id, campaign_id))

    batches = cursor.fetchall()

    conn.close()
    return batches


def get_campaign_stats(campaign_id, batch_id=None):
    """Get campaign statistics (approved, rejected, undecided counts)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    stats = {}
    states = ['undecided', 'approved', 'rejected']

    for state in states:
        query = "SELECT COUNT(*) FROM contacts_campaign WHERE campaign_id = ? AND current_state = ?"
        params = [campaign_id, state]

        if batch_id:
            query += " AND campaign_batch_id = ?"
            params.append(batch_id)

        cursor.execute(query, params)
        stats[state] = cursor.fetchone()[0]

    conn.close()
    return stats


def update_contact_state(counter, new_state, reason=None, notes=None):
    """Update a contact's state in a campaign."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if reason and notes:
        cursor.execute(
            "UPDATE contacts_campaign SET current_state = ?, reason = ?, notes = ? WHERE counter = ?",
            (new_state, reason, notes, counter)
        )
    elif reason:
        cursor.execute(
            "UPDATE contacts_campaign SET current_state = ?, reason = ? WHERE counter = ?",
            (new_state, reason, counter)
        )
    elif notes:
        cursor.execute(
            "UPDATE contacts_campaign SET current_state = ?, notes = ? WHERE counter = ?",
            (new_state, notes, counter)
        )
    else:
        cursor.execute(
            "UPDATE contacts_campaign SET current_state = ? WHERE counter = ?",
            (new_state, counter)
        )

    conn.commit()
    conn.close()
    return True


class BrowserThread(QThread):
    """Thread for browser operations to avoid UI freezing."""
    error = pyqtSignal(str)
    ready = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.driver = None
        self.current_linkedin_tab = None
        self.main_window = None

    def run(self):
        try:
            if not SELENIUM_AVAILABLE:
                self.error.emit(
                    "Selenium not available. Please install it with: pip install selenium webdriver_manager")
                return

            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")

            # Initialize browser
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(
                service=service, options=chrome_options)

            # Open LinkedIn in the main window
            self.driver.get("https://www.linkedin.com")
            self.main_window = self.driver.current_window_handle

            # Signal that browser is ready
            self.ready.emit(self.driver)

        except Exception as e:
            self.error.emit(f"Error initializing browser: {str(e)}")

    def open_linkedin_profile(self, linkedin_url):
        """Open a LinkedIn profile in a new tab, closing the previous one if it exists."""
        if not self.driver:
            return False

        try:
            # Close the previous LinkedIn tab if it exists
            if self.current_linkedin_tab:
                try:
                    self.driver.switch_to.window(self.current_linkedin_tab)
                    self.driver.close()
                except:
                    pass  # Previous tab may have been closed already

            # Switch back to main window
            self.driver.switch_to.window(self.main_window)

            # Open a new tab with the LinkedIn profile
            self.driver.execute_script(
                f"window.open('{linkedin_url}', '_blank');")

            # Get window handles and switch to the new tab
            all_handles = self.driver.window_handles
            for handle in all_handles:
                if handle != self.main_window:
                    self.current_linkedin_tab = handle
                    self.driver.switch_to.window(handle)
                    break

            return True

        except Exception as e:
            self.error.emit(f"Error opening LinkedIn profile: {str(e)}")
            return False

    def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass


class ContactProspectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contact Prospector")
        self.setMinimumSize(1000, 700)

        # Apply fusion style for modern look
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        self.current_campaign_id = None
        self.current_campaign_name = None
        self.current_batch_id = None
        self.contacts = []
        self.current_index = 0

        # Initialize browser thread
        self.browser_thread = BrowserThread()
        self.browser_thread.error.connect(self.on_browser_error)
        self.browser_thread.ready.connect(self.on_browser_ready)
        self.browser_thread.start()

        self.driver = None  # Will be set when browser is ready

        self.init_ui()
        self.load_campaigns()

    def on_browser_error(self, error_message):
        """Handle browser errors."""
        QMessageBox.warning(self, "Browser Error", error_message)

    def on_browser_ready(self, driver):
        """Handle browser ready signal."""
        self.driver = driver

    def init_ui(self):
        """Initialize the user interface."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Campaign selection area
        campaign_group = QGroupBox("Campaign Selection")
        campaign_layout = QHBoxLayout()

        self.campaign_combo = QComboBox()
        self.campaign_combo.setMinimumWidth(400)
        self.campaign_combo.currentIndexChanged.connect(
            self.on_campaign_changed)
        campaign_layout.addWidget(self.campaign_combo)

        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_contacts)
        campaign_layout.addWidget(load_button)

        self.batch_combo = QComboBox()
        self.batch_combo.setMinimumWidth(250)
        campaign_layout.addWidget(self.batch_combo)

        campaign_group.setLayout(campaign_layout)
        main_layout.addWidget(campaign_group)

        # Stats area
        stats_group = QGroupBox("Campaign Statistics")
        stats_layout = QHBoxLayout()

        self.total_label = QLabel("Total: 0")
        self.undecided_label = QLabel("Undecided: 0")
        self.approved_label = QLabel("Approved: 0")
        self.rejected_label = QLabel("Rejected: 0")

        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.undecided_label)
        stats_layout.addWidget(self.approved_label)
        stats_layout.addWidget(self.rejected_label)

        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

        # Contact details area
        details_group = QGroupBox("Contact Details")
        details_layout = QVBoxLayout()

        # Contact header
        header_layout = QHBoxLayout()
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.name_label)

        self.state_label = QLabel()
        self.state_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.state_label)
        header_layout.addStretch(1)

        details_layout.addLayout(header_layout)

        # Contact info
        info_layout = QFormLayout()

        self.role_label = QLabel()
        info_layout.addRow("Role:", self.role_label)

        self.email_label = QLabel()
        info_layout.addRow("Email:", self.email_label)

        self.phone_label = QLabel()
        info_layout.addRow("Phone:", self.phone_label)

        self.location_label = QLabel()
        info_layout.addRow("Location:", self.location_label)

        self.company_label = QLabel()
        info_layout.addRow("Company:", self.company_label)

        self.website_label = QLabel()
        info_layout.addRow("Website:", self.website_label)

        details_layout.addLayout(info_layout)

        # Notes area
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Add notes here...")
        self.notes_edit.setMaximumHeight(100)
        details_layout.addWidget(self.notes_edit)

        details_group.setLayout(details_layout)
        main_layout.addWidget(details_group)

        # Controls area
        controls_group = QGroupBox("Actions")
        controls_layout = QHBoxLayout()

        # Navigation controls
        nav_layout = QVBoxLayout()

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_contact)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_contact)
        nav_layout.addWidget(self.next_button)

        # Add counters
        counter_layout = QHBoxLayout()
        counter_layout.addWidget(QLabel("Position:"))
        self.position_label = QLabel("0 / 0")
        counter_layout.addWidget(self.position_label)
        nav_layout.addLayout(counter_layout)

        controls_layout.addLayout(nav_layout)

        # LinkedIn button
        self.linkedin_button = QPushButton("Open LinkedIn Profile")
        self.linkedin_button.clicked.connect(self.open_linkedin)
        self.linkedin_button.setMinimumHeight(80)
        self.linkedin_button.setStyleSheet(
            "font-size: 14px; font-weight: bold;")
        controls_layout.addWidget(self.linkedin_button)

        # Decision buttons
        decision_layout = QVBoxLayout()

        self.approve_button = QPushButton("♥ Approve")
        self.approve_button.clicked.connect(
            lambda: self.update_state('approved'))
        self.approve_button.setStyleSheet(
            "color: white; background-color: #4CAF50; font-size: 16px;")
        self.approve_button.setMinimumHeight(40)
        decision_layout.addWidget(self.approve_button)

        self.reject_button = QPushButton("✕ Reject")
        self.reject_button.clicked.connect(
            lambda: self.update_state('rejected'))
        self.reject_button.setStyleSheet(
            "color: white; background-color: #F44336; font-size: 16px;")
        self.reject_button.setMinimumHeight(40)
        decision_layout.addWidget(self.reject_button)

        controls_layout.addLayout(decision_layout)

        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)

        # Initialize UI to disabled state
        self.set_ui_enabled(False)

    def load_campaigns(self):
        """Load campaigns into the combo box."""
        campaigns = get_campaigns()

        if not campaigns:
            QMessageBox.warning(
                self, "No Campaigns", "No campaigns found. Please create campaigns first.")
            return

        self.campaign_combo.clear()
        for campaign_id, name, created_at in campaigns:
            self.campaign_combo.addItem(
                f"{name} (Created: {created_at})", campaign_id)

    def on_campaign_changed(self):
        """Handle campaign selection change."""
        if self.campaign_combo.currentIndex() < 0:
            return

        self.current_campaign_id = self.campaign_combo.currentData()
        self.current_campaign_name = self.campaign_combo.currentText().split(
            " (Created:")[0]

        # Load batches for this campaign
        self.load_batches()

    def load_batches(self):
        """Load batches for the selected campaign."""
        if not self.current_campaign_id:
            return

        batches = get_campaign_batches(self.current_campaign_id)

        self.batch_combo.clear()
        self.batch_combo.addItem("All Batches", None)

        for batch_id, batch_tag, count in batches:
            self.batch_combo.addItem(f"{batch_tag} (Count: {count})", batch_id)

    def load_contacts(self):
        """Load contacts for the selected campaign and batch."""
        if not self.current_campaign_id:
            QMessageBox.warning(self, "No Campaign",
                                "Please select a campaign first.")
            return

        self.current_batch_id = self.batch_combo.currentData()

        # Load campaign stats
        self.update_stats()

        # Create state selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Contact State")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout(dialog)

        state_group = QGroupBox("Select which contacts to load:")
        state_layout = QVBoxLayout()

        undecided_checkbox = QCheckBox("Undecided")
        undecided_checkbox.setChecked(True)
        state_layout.addWidget(undecided_checkbox)

        approved_checkbox = QCheckBox("Approved")
        state_layout.addWidget(approved_checkbox)

        rejected_checkbox = QCheckBox("Rejected")
        state_layout.addWidget(rejected_checkbox)

        state_group.setLayout(state_layout)
        layout.addWidget(state_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Show dialog
        if dialog.exec_() != QDialog.Accepted:
            return

        # Get selected states
        selected_states = []
        if undecided_checkbox.isChecked():
            selected_states.append('undecided')
        if approved_checkbox.isChecked():
            selected_states.append('approved')
        if rejected_checkbox.isChecked():
            selected_states.append('rejected')

        if not selected_states:
            QMessageBox.warning(self, "No States Selected",
                                "Please select at least one state.")
            return

        # Load contacts with all selected states
        self.contacts = []
        for state in selected_states:
            contacts = get_campaign_contacts(
                self.current_campaign_id,
                state=state,
                batch_id=self.current_batch_id
            )
            self.contacts.extend(contacts)

        if not self.contacts:
            QMessageBox.information(
                self,
                "No Contacts",
                "No contacts found in this campaign/batch with the selected states."
            )
            self.set_ui_enabled(False)
            return

        self.current_index = 0
        self.display_current_contact()
        self.set_ui_enabled(True)

    def update_stats(self):
        """Update the campaign statistics display."""
        if not self.current_campaign_id:
            return

        stats = get_campaign_stats(
            self.current_campaign_id, self.current_batch_id)

        total = stats['undecided'] + stats['approved'] + stats['rejected']
        self.total_label.setText(f"Total: {total}")
        self.undecided_label.setText(f"Undecided: {stats['undecided']}")
        self.approved_label.setText(f"Approved: {stats['approved']}")
        self.rejected_label.setText(f"Rejected: {stats['rejected']}")

    def display_current_contact(self):
        """Display the current contact's details."""
        if not self.contacts or self.current_index >= len(self.contacts):
            self.clear_contact_display()
            return

        contact = self.contacts[self.current_index]

        # Handle the case where the notes field might be missing in older records
        # by unpacking only the expected number of values
        if len(contact) == 16:  # Old format without notes
            counter, contact_id, first_name, last_name, role, email, phone, linkedin, city, state, country, company, website, current_state, reason, batch_id = contact
            notes = ""  # Default empty notes
        else:  # New format with notes
            counter, contact_id, first_name, last_name, role, email, phone, linkedin, city, state, country, company, website, current_state, reason, batch_id, notes = contact

        # Update name and state
        full_name = f"{first_name} {last_name}" if last_name else first_name
        self.name_label.setText(full_name)

        if current_state == 'approved':
            self.state_label.setText("✅ Approved")
            self.state_label.setStyleSheet("color: green; font-weight: bold;")
        elif current_state == 'rejected':
            self.state_label.setText("❌ Rejected")
            self.state_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.state_label.setText("⏳ Undecided")
            self.state_label.setStyleSheet("color: gray; font-weight: bold;")

        # Update contact details
        self.role_label.setText(role or "N/A")
        self.email_label.setText(email or "N/A")
        self.phone_label.setText(phone or "N/A")

        location_parts = [p for p in [city, state, country] if p]
        location = ", ".join(location_parts) if location_parts else "N/A"
        self.location_label.setText(location)

        self.company_label.setText(company or "N/A")
        self.website_label.setText(website or "N/A")

        # Update notes (prioritize notes field if it exists, otherwise use reason)
        self.notes_edit.setText(notes or reason or "")

        # Update position indicator
        self.position_label.setText(
            f"{self.current_index + 1} / {len(self.contacts)}")

        # Update LinkedIn button state
        has_linkedin = bool(linkedin)
        self.linkedin_button.setEnabled(has_linkedin)

        # Open LinkedIn profile in browser
        if has_linkedin and self.browser_thread and hasattr(self.browser_thread, 'open_linkedin_profile'):
            self.browser_thread.open_linkedin_profile(linkedin)

    def clear_contact_display(self):
        """Clear the contact display."""
        self.name_label.setText("")
        self.state_label.setText("")
        self.role_label.setText("")
        self.email_label.setText("")
        self.phone_label.setText("")
        self.location_label.setText("")
        self.company_label.setText("")
        self.website_label.setText("")
        self.notes_edit.setText("")
        self.position_label.setText("0 / 0")
        self.linkedin_button.setEnabled(False)

    def set_ui_enabled(self, enabled):
        """Enable or disable UI elements based on whether contacts are loaded."""
        self.prev_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
        self.approve_button.setEnabled(enabled)
        self.reject_button.setEnabled(enabled)
        self.notes_edit.setEnabled(enabled)

    def prev_contact(self):
        """Navigate to the previous contact."""
        if not self.contacts or self.current_index <= 0:
            return

        self.current_index -= 1
        self.display_current_contact()

    def next_contact(self):
        """Navigate to the next contact."""
        if not self.contacts or self.current_index >= len(self.contacts) - 1:
            return

        self.current_index += 1
        self.display_current_contact()

    def open_linkedin(self):
        """Open the current contact's LinkedIn profile."""
        if not self.contacts or self.current_index >= len(self.contacts):
            return

        # LinkedIn URL index
        linkedin_url = self.contacts[self.current_index][7]

        if linkedin_url:
            try:
                # Use Selenium browser if available
                if hasattr(self, 'browser_thread') and self.browser_thread is not None:
                    if hasattr(self.browser_thread, 'open_linkedin_profile'):
                        success = self.browser_thread.open_linkedin_profile(
                            linkedin_url)
                        if success:
                            return

                # Fallback to basic webbrowser
                webbrowser.open(linkedin_url)
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Could not open LinkedIn URL: {str(e)}")

    def closeEvent(self, event):
        """Clean up resources when window is closed."""
        try:
            # Clean up browser thread
            if hasattr(self, 'browser_thread') and self.browser_thread is not None:
                if hasattr(self.browser_thread, 'cleanup'):
                    self.browser_thread.cleanup()
                self.browser_thread.quit()
                # Wait up to 3 seconds for thread to finish
                self.browser_thread.wait(3000)
        except Exception as e:
            print(f"Error cleaning up resources: {e}")

        # Accept the close event
        event.accept()

    def update_state(self, new_state):
        """Update the current contact's state."""
        if not self.contacts or self.current_index >= len(self.contacts):
            return

        # Get the counter from the contact
        # Counter index is always 0
        counter = self.contacts[self.current_index][0]

        # Get notes from the text edit
        notes = self.notes_edit.toPlainText().strip()

        # Update the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE contacts_campaign SET current_state = ?, notes = ? WHERE counter = ?",
            (new_state, notes, counter)
        )
        conn.commit()
        conn.close()

        # Update the display - handle both formats (with or without notes)
        contact_list = list(self.contacts[self.current_index])

        if len(contact_list) == 16:  # Old format without notes
            # Add notes to the end of the tuple
            contact_list[13] = new_state  # Update state
            contact_list.append(notes)    # Add notes at the end
        else:  # New format with notes
            contact_list[13] = new_state  # Update state
            contact_list[16] = notes      # Update notes

        # Update the contact in the list
        self.contacts[self.current_index] = tuple(contact_list)

        # Display the updated contact
        self.display_current_contact()

        # Update stats
        self.update_stats()

        # Automatically move to next contact if available
        if self.current_index < len(self.contacts) - 1:
            self.next_contact()
        else:
            # Get unique states from loaded contacts
            unique_states = set()
            for contact in self.contacts:
                state = contact[13]  # current_state index
                unique_states.add(state)

            # Reload contacts based on the same states we previously loaded
            self.contacts = []
            for state in unique_states:
                contacts = get_campaign_contacts(
                    self.current_campaign_id,
                    state=state,
                    batch_id=self.current_batch_id
                )
                self.contacts.extend(contacts)

            if not self.contacts:
                QMessageBox.information(
                    self,
                    "All Contacts Processed",
                    "All contacts have been processed in this campaign/batch."
                )
                self.set_ui_enabled(False)
                self.clear_contact_display()
                return

            self.current_index = 0
            self.display_current_contact()


def run_contact_prospector():
    """Run the contact prospector application."""
    app = QApplication(sys.argv)
    window = ContactProspectorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_contact_prospector()
