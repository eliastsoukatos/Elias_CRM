import os
import sys
import sqlite3
import webbrowser
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QLabel, QHBoxLayout, 
                           QGroupBox, QStackedWidget, QMessageBox, QComboBox,
                           QFormLayout, QDialog, QTextBrowser)
from PyQt5.QtCore import Qt, QObject, QEvent, pyqtSignal, QThread
from PyQt5.QtGui import QCursor
from send_email import send_project_email



# Try to import pyautogui for automated mouse control
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("pyautogui not available. Please install it with: pip install pyautogui")

# Try to import Selenium for browser automation
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

# Database path - use hardcoded path for Windows
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use hardcoded path for Windows
if os.name == 'nt':  # Windows
    DB_PATH = "C:\\Users\\EliasTsoukatos\\Documents\\software_code\\Elias_CRM\\databases\\database.db"
else:
    # Create the database path for other platforms
    DB_PATH = os.path.join(project_root, 'databases', 'database.db')

# Browser thread for handling URLs
class BrowserThread(QThread):
    """Thread for browser operations to avoid UI freezing"""
    error = pyqtSignal(str)
    ready = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.driver = None
        self.current_linkedin_tab = None
        self.current_website_tab = None
        self.main_window = None
    
    def run(self):
        try:
            if not SELENIUM_AVAILABLE:
                self.error.emit("Selenium not available. Please install it with: pip install selenium webdriver_manager")
                return
                
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            
            # Initialize browser
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Open a blank page in the main window
            self.driver.get("about:blank")
            self.main_window = self.driver.current_window_handle
            
            # Signal that browser is ready
            self.ready.emit(self.driver)
            
        except Exception as e:
            self.error.emit(f"Error initializing browser: {str(e)}")
    
    def open_linkedin_profile(self, linkedin_url):
        """Open a LinkedIn profile in a new tab, closing the previous one if it exists"""
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
            
            # Format URL if needed
            if linkedin_url and not linkedin_url.startswith(('http://', 'https://')):
                linkedin_url = 'https://' + linkedin_url
            
            # Open a new tab with the LinkedIn profile
            if linkedin_url:
                self.driver.execute_script(f"window.open('{linkedin_url}', '_blank');")
                
                # Get window handles and switch to the new tab
                all_handles = self.driver.window_handles
                for handle in all_handles:
                    if handle != self.main_window and handle != self.current_website_tab:
                        self.current_linkedin_tab = handle
                        self.driver.switch_to.window(handle)
                        break
                
                return True
            return False
                
        except Exception as e:
            self.error.emit(f"Error opening LinkedIn profile: {str(e)}")
            return False
    
    def open_website(self, website_url):
        """Open a website in a new tab, closing the previous one if it exists"""
        if not self.driver:
            return False
            
        try:
            # Close the previous website tab if it exists
            if self.current_website_tab:
                try:
                    self.driver.switch_to.window(self.current_website_tab)
                    self.driver.close()
                except:
                    pass  # Previous tab may have been closed already
            
            # Switch back to main window
            self.driver.switch_to.window(self.main_window)
            
            # Format URL if needed
            if website_url and not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            # Open a new tab with the website
            if website_url:
                self.driver.execute_script(f"window.open('{website_url}', '_blank');")
                
                # Get window handles and switch to the new tab
                all_handles = self.driver.window_handles
                for handle in all_handles:
                    if handle != self.main_window and handle != self.current_linkedin_tab:
                        self.current_website_tab = handle
                        self.driver.switch_to.window(handle)
                        break
                
                return True
            return False
                
        except Exception as e:
            self.error.emit(f"Error opening website: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass

# Simple coordinate input dialog
class CoordinateSelector:
    """Simple class to capture screen coordinates"""
    
    def __init__(self, parent=None):
        """Initialize the coordinate selector"""
        self.parent = parent
    
    def get_coordinate(self, coordinate_name="A"):
        """Get coordinates by clicking on the screen"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
        from PyQt5.QtCore import Qt, QTimer, QPoint
        from PyQt5.QtGui import QMouseEvent, QCursor, QScreen, QPixmap, QPainter, QPen, QColor
        
        # Ensure pyautogui is available
        if not PYAUTOGUI_AVAILABLE:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self.parent, 
                "Missing Dependency", 
                "pyautogui is not available. Please install it with: pip install pyautogui"
            )
            # Fall back to manual entry
            return self.get_coordinate_manual(coordinate_name)
            
        # Create a simple overlay app that tracks mouse position and lets user click
        class CoordinateCapture(QDialog):
            def __init__(self, parent=None, coordinate_name="A"):
                super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
                
                # Get primary screen size
                screen = QApplication.primaryScreen()
                self.screen_geometry = screen.geometry()
                
                # Set size to cover the screen
                self.setGeometry(self.screen_geometry)
                
                # Set a semi-transparent background
                self.setAttribute(Qt.WA_TranslucentBackground)
                
                # Setup the UI
                self.coordinate_name = coordinate_name
                self.setup_ui()
                
                # Variables for position tracking
                self.selected_position = None
                
                # Start timer to update position display
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.update_position_label)
                self.timer.start(50)  # Update every 50ms
                
                # Get current position
                self.current_position = QCursor.pos()
                
            def setup_ui(self):
                """Set up the UI elements"""
                layout = QVBoxLayout(self)
                
                # Instructions at the top of the screen
                self.instructions = QLabel(
                    f"<div style='background-color: rgba(0,0,0,0.7); color: white; padding: 10px;'>"
                    f"<h3>Capturing {self.coordinate_name} Coordinate</h3>"
                    f"<p>Move your mouse to the desired position and click to capture.<br>"
                    f"Press ESC to cancel.</p>"
                    f"</div>"
                )
                self.instructions.setAlignment(Qt.AlignTop | Qt.AlignCenter)
                layout.addWidget(self.instructions, 0, Qt.AlignTop)
                
                # Position display at the bottom
                self.position_label = QLabel(
                    "<div style='background-color: rgba(0,0,0,0.7); color: white; padding: 10px;'>"
                    "Current position: X=0, Y=0"
                    "</div>"
                )
                self.position_label.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
                layout.addWidget(self.position_label, 0, Qt.AlignBottom)
                
                # Add stretching to keep the labels at the top and bottom
                layout.insertStretch(1, 1)
                
                # Set up event handling
                self.setMouseTracking(True)
            
            def update_position_label(self):
                """Update the position label with current mouse coordinates"""
                self.current_position = QCursor.pos()
                self.position_label.setText(
                    f"<div style='background-color: rgba(0,0,0,0.7); color: white; padding: 10px;'>"
                    f"Current position: X={self.current_position.x()}, Y={self.current_position.y()}"
                    f"</div>"
                )
                self.update()  # Trigger a repaint
            
            def mousePressEvent(self, event):
                """Handle mouse press to capture coordinate"""
                if event.button() == Qt.LeftButton:
                    self.selected_position = (event.globalX(), event.globalY())
                    self.accept()  # Close dialog with acceptance
            
            def keyPressEvent(self, event):
                """Handle key press events"""
                if event.key() == Qt.Key_Escape:
                    self.reject()  # Close dialog with rejection
            
            def paintEvent(self, event):
                """Paint the overlay with crosshairs at the cursor position"""
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Draw semi-transparent overlay
                painter.fillRect(self.rect(), QColor(0, 0, 0, 50))
                
                # Draw crosshair at cursor position
                if hasattr(self, 'current_position'):
                    x, y = self.current_position.x(), self.current_position.y()
                    
                    # Draw horizontal line
                    pen = QPen(QColor(255, 0, 0))
                    pen.setWidth(1)
                    painter.setPen(pen)
                    painter.drawLine(0, y, self.width(), y)
                    
                    # Draw vertical line
                    painter.drawLine(x, 0, x, self.height())
                    
                    # Draw circle at intersection
                    painter.drawEllipse(QPoint(x, y), 10, 10)
        
        # Create and show the coordinate capture dialog
        try:
            capture_dialog = CoordinateCapture(self.parent, coordinate_name)
            result = capture_dialog.exec_()
            
            if result == QDialog.Accepted and capture_dialog.selected_position:
                return capture_dialog.selected_position
            return None
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self.parent, 
                "Error", 
                f"Error capturing coordinates: {str(e)}\n\nFalling back to manual input."
            )
            # Fall back to manual input on error
            return self.get_coordinate_manual(coordinate_name)
    
    def get_coordinate_manual(self, coordinate_name="A"):
        """Manual coordinate input for fallback"""
        from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
        
        # Show instruction message
        QMessageBox.information(
            self.parent, 
            f"Enter Coordinate {coordinate_name}",
            f"Please enter coordinates for point {coordinate_name} in the format 'X,Y'.\n\n"
            "For example: 100,200"
        )
        
        # Get the coordinates as a string
        text, ok = QInputDialog.getText(
            self.parent,
            f"Enter coordinates for {coordinate_name}",
            "Enter as 'X,Y' (e.g., 100,200):",
            QLineEdit.Normal
        )
        
        if not ok or not text:
            return None
            
        # Parse the coordinates
        try:
            parts = text.split(',')
            if len(parts) != 2:
                raise ValueError("Invalid format. Use X,Y format.")
                
            x = int(parts[0].strip())
            y = int(parts[1].strip())
            
            return (x, y)
        except Exception as e:
            QMessageBox.warning(
                self.parent, 
                "Invalid Input", 
                f"Could not parse coordinates: {str(e)}\n\nPlease use format 'X,Y' (e.g., 100,200)"
            )
            return None

class PhoneDialerApp:
    def __init__(self, parent=None):
        self.parent = parent
        self.contacts_list = []
        self.current_contact_index = -1
        self.driver = None
    
    def on_browser_error(self, error_message):
        """Handle browser errors"""
        if self.parent:
            QMessageBox.warning(self.parent, "Browser Error", error_message)
        else:
            print(f"Browser error: {error_message}")
    
    def on_browser_ready(self, driver):
        """Handle browser ready signal"""
        self.driver = driver
        print("Browser is ready for opening websites and LinkedIn profiles")
        
    def _safe_get_field(self, contact, field_name, default=''):
        """Safely get a field from a contact, with fallbacks for SQLite.Row objects"""
        try:
            # First try direct access
            value = contact[field_name]
            return value if value is not None else default
        except:
            try:
                # Try dict conversion
                contact_dict = dict(contact)
                value = contact_dict.get(field_name)
                return value if value is not None else default
            except:
                return default
    
    def _get_contacts_by_company_id(self, company_id):
        """Safely get indices of contacts from the same company"""
        if not company_id:
            return []
            
        company_contacts_indices = []
        for i, c in enumerate(self.contacts_list):
            try:
                # Direct access approach for company_id
                contact_company_id = None
                
                try:
                    # Try direct access first
                    contact_company_id = str(c['company_id'])
                except:
                    # Fall back to dict conversion
                    try:
                        contact_dict = dict(c)
                        contact_company_id = contact_dict.get('company_id')
                    except:
                        pass
                
                # If found and matches target company_id
                if contact_company_id and contact_company_id == company_id:
                    company_contacts_indices.append(i)
            except Exception as e:
                print(f"Warning: Error processing contact at index {i}: {str(e)}")
                
        return company_contacts_indices
    
    def load_campaigns(self, company_campaign_combo, contact_batch_combo):
        """Load company campaigns and contact batch tags for the phone dialer"""
        try:
            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # First check if company_id column exists in contacts_campaign table
            cursor.execute("PRAGMA table_info(contacts_campaign)")
            columns = [col[1] for col in cursor.fetchall()]
            has_company_id = 'company_id' in columns
            
            if not has_company_id and self.parent:
                QMessageBox.warning(self.parent, "Database Warning", 
                    "The contacts_campaign table doesn't have a company_id column. Please run the database setup script."
                )
            
            # Clear current items
            company_campaign_combo.clear()
            contact_batch_combo.clear()
            
            # Get company campaigns
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
            
            if not campaigns:
                if self.parent:
                    QMessageBox.warning(self.parent, "No Campaigns", "No company campaigns found.")
                conn.close()
                return False
            
            # Add campaigns to combo box
            for campaign in campaigns:
                company_campaign_combo.addItem(
                    f"{campaign['campaign_name']} - {campaign['total_companies']} companies",
                    campaign['campaign_id']
                )
            
            # Get distinct contact batch tags
            cursor.execute("""
                SELECT DISTINCT campaign_batch_tag 
                FROM contacts_campaign
                WHERE campaign_batch_tag IS NOT NULL
                ORDER BY campaign_batch_tag
            """)
            
            batch_tags = cursor.fetchall()
            
            # Add "All" option
            contact_batch_combo.addItem("All Batch Tags", "all")
            
            # Add batch tags to combo box
            for tag in batch_tags:
                contact_batch_combo.addItem(tag['campaign_batch_tag'], tag['campaign_batch_tag'])
            
            conn.close()
            
            if self.parent:
                QMessageBox.information(self.parent, "Campaigns Loaded", "Campaigns and batch tags loaded successfully.")
            
            return True
            
        except Exception as e:
            if self.parent:
                QMessageBox.critical(self.parent, "Error", f"Error loading campaigns: {e}")
            return False
    
    def load_contacts(self, campaign_id, batch_tag):
        """Load contacts for the selected campaign and batch tag"""
        try:
            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get approved contacts for this campaign, filtered by tag if specified
            query = """
                SELECT 
                    c.id,
                    c.contact_id,
                    c.Name,
                    c.Last_Name,
                    c.Role,
                    c.Mobile_Phone,
                    c.Email,
                    c.LinkedIn_URL,
                    co.name as company_name,
                    cc.campaign_batch_tag,
                    c.City,
                    c.State,
                    c.Country,
                    c.Timezone,  -- Added Timezone field here
                    COALESCE(cc.company_id, c.company_id) as company_id,
                    cc.notes,
                    cc.counter,
                    co.website as company_website
                FROM contacts_campaign cc
                LEFT JOIN contacts c ON cc.contact_id = c.contact_id
                LEFT JOIN companies co ON c.company_id = co.company_id
                WHERE cc.campaign_id = ? 
                AND cc.current_state = 'approved'
                AND c.contact_id IS NOT NULL
            """
            
            params = [campaign_id]
            
            # Add tag filter if not "all"
            if batch_tag != "all":
                query += " AND cc.campaign_batch_tag = ?"
                params.append(batch_tag)
                
            query += " ORDER BY c.Name, c.Last_Name"
            
            cursor.execute(query, params)
            contacts = cursor.fetchall()
            
            conn.close()
            
            # Store contacts in list
            self.contacts_list = list(contacts)
            
            if not self.contacts_list and self.parent:
                QMessageBox.warning(self.parent, "No Approved Contacts", 
                    "No approved contacts found with the selected criteria."
                )
                return False
            
            return len(self.contacts_list) > 0
            
        except Exception as e:
            if self.parent:
                QMessageBox.critical(self.parent, "Error", f"Error loading contacts: {e}")
            return False

    def show_contacts_dialog(self, campaign_name, batch_tag):
        """Show dialog with contacts"""
        if not self.contacts_list:
            return
        
        # Initialize coordinate storage
        self.coord_a = None
        self.coord_b = None
        
        # Create coordinate selector
        self.coordinate_selector = CoordinateSelector(self.parent)
        
        # Initialize browser thread for opening websites and LinkedIn profiles
        self.browser_thread = BrowserThread()
        self.browser_thread.error.connect(self.on_browser_error)
        self.browser_thread.ready.connect(self.on_browser_ready)
        self.browser_thread.start()
        
        # Initialize driver reference
        self.driver = None
        
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(f"Phone Dialer - {campaign_name}")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(600)  # Increased height to accommodate notes
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Header with campaign info
        header_layout = QHBoxLayout()
        campaign_label = QLabel(f"Campaign: {campaign_name}")
        campaign_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        header_layout.addWidget(campaign_label)
        
        tag_display = "All Tags" if batch_tag == "all" else batch_tag
        tag_label = QLabel(f"Tag: {tag_display}")
        tag_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        header_layout.addWidget(tag_label)
        
        contacts_count = QLabel(f"Contacts: {len(self.contacts_list)}")
        contacts_count.setStyleSheet("font-weight: bold; font-size: 16px;")
        header_layout.addWidget(contacts_count)
        
        layout.addLayout(header_layout)
        
        # Contact info display
        contact_group = QGroupBox("Contact Information")
        contact_layout = QVBoxLayout()
        
        # Create a horizontal layout for contact info and copy buttons
        contact_info_layout = QHBoxLayout()
        
        contact_info = QTextBrowser()
        contact_info.setMinimumHeight(250)
        contact_info.setStyleSheet("font-size: 14px;")
        contact_info_layout.addWidget(contact_info, 1)  # 1 is the stretch factor
        
        # Create copy buttons layout
        from PyQt5.QtWidgets import QToolButton
        from PyQt5.QtCore import QSize
        
        copy_buttons_layout = QVBoxLayout()
        copy_buttons_layout.setSpacing(2)
        copy_buttons_layout.setContentsMargins(2, 2, 2, 2)
        
        # Add coordinate capture buttons (A and B)
        capture_a_button = QToolButton()
        capture_a_button.setToolTip("Capture coordinate A")
        capture_a_button.setText("A")
        capture_a_button.setStyleSheet("""
            QToolButton {
                background-color: #2196F3;
                color: white;
                border-radius: 3px;
                padding: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #0b7dda;
            }
        """)
        capture_a_button.setFixedSize(QSize(20, 20))
        copy_buttons_layout.addWidget(capture_a_button)
        
        capture_b_button = QToolButton()
        capture_b_button.setToolTip("Capture coordinate B")
        capture_b_button.setText("B")
        capture_b_button.setStyleSheet("""
            QToolButton {
                background-color: #9C27B0;
                color: white;
                border-radius: 3px;
                padding: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #7B1FA2;
            }
        """)
        capture_b_button.setFixedSize(QSize(20, 20))
        copy_buttons_layout.addWidget(capture_b_button)
        
        # Add copy email button
        copy_email_button = QToolButton()
        copy_email_button.setToolTip("Copy Email")
        copy_email_button.setText("📧")  # Email emoji
        copy_email_button.setStyleSheet("""
            QToolButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 3px;
                padding: 3px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #45a049;
            }
        """)
        copy_email_button.setFixedSize(QSize(24, 24))
        copy_buttons_layout.addWidget(copy_email_button)
        
        # --- NUEVO: Agregar botón "Send Email" ---
        send_email_button = QToolButton()
        send_email_button.setToolTip("Send Email")
        send_email_button.setText("✉")  # Emoji de sobre
        send_email_button.setStyleSheet("""
            QToolButton {
                background-color: #673AB7;
                color: white;
                border-radius: 3px;
                padding: 3px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #5E35B1;
            }
        """)
        send_email_button.setFixedSize(QSize(24, 24))
        copy_buttons_layout.addWidget(send_email_button)
        # --- Fin botón "Send Email" ---
        
        # Add the copy buttons layout to the contact info layout
        contact_info_layout.addLayout(copy_buttons_layout)
        
        # Add the contact info layout to the main contact layout
        contact_layout.addLayout(contact_info_layout)
        
        # Notes field
        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        contact_layout.addWidget(notes_label)
        
        from PyQt5.QtWidgets import QTextEdit
        notes_text = QTextEdit()
        notes_text.setMinimumHeight(80)
        notes_text.setPlaceholderText("Add your notes here... (Notes are saved automatically)")
        contact_layout.addWidget(notes_text)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        prev_button = QPushButton("Previous Contact")
        prev_button.setEnabled(False)
        nav_layout.addWidget(prev_button)
        
        counter_label = QLabel(f"Contact 1 of {len(self.contacts_list)}")
        counter_label.setAlignment(Qt.AlignCenter)
        counter_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        nav_layout.addWidget(counter_label)
        
        next_button = QPushButton("Next Contact")
        next_button.setEnabled(len(self.contacts_list) > 1)
        nav_layout.addWidget(next_button)
        
        contact_layout.addLayout(nav_layout)
        
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        remove_button = QPushButton("Remove")
        remove_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: #ff9800; color: white;")
        action_layout.addWidget(remove_button)
        
        remove_all_button = QPushButton("Remove All")
        remove_all_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: #f44336; color: white;")
        action_layout.addWidget(remove_all_button)
        
        opportunity_button = QPushButton("Opportunity")
        opportunity_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: #2196F3; color: white;")
        action_layout.addWidget(opportunity_button)
        
        contact_layout.addLayout(action_layout)
        
        # Phone call buttons
        phone_buttons_layout = QHBoxLayout()
        
        # Green phone button (left)
        green_phone_button = QPushButton("📞")  # Phone emoji
        green_phone_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                min-width: 60px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        phone_buttons_layout.addWidget(green_phone_button)
        
        # Red phone button (right)
        red_phone_button = QPushButton("📞")  # Phone emoji
        red_phone_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                padding: 10px;
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                min-width: 60px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        phone_buttons_layout.addWidget(red_phone_button)
        
        contact_layout.addLayout(phone_buttons_layout)
        
        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.reject)
        layout.addWidget(close_button)
        
        # Set current contact index and prepare for display
        self.current_contact_index = 0
        
        # Wait a moment for browser thread to initialize
        QApplication.processEvents()
        
        # Function to save notes for the current contact
        def save_notes():
            if self.current_contact_index < 0 or self.current_contact_index >= len(self.contacts_list):
                return
                
            contact = self.contacts_list[self.current_contact_index]
            notes_content = notes_text.toPlainText()
            counter = self._safe_get_field(contact, 'counter')
            
            if not counter:
                return
                
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contacts_campaign SET notes = ? WHERE counter = ?",
                    (notes_content, counter)
                )
                conn.commit()
                conn.close()
            except Exception as e:
                if self.parent:
                    QMessageBox.warning(self.parent, "Error", f"Could not save notes: {str(e)}")
            
        # --- NUEVA FUNCIÓN: Enviar Email al contacto actual ---
        def send_email_current_contact():
            if self.current_contact_index < 0 or self.current_contact_index >= len(self.contacts_list):
                return
            contact = self.contacts_list[self.current_contact_index]
            recipient_email = self._safe_get_field(contact, 'Email', '')
            if not recipient_email:
                QMessageBox.warning(self.parent, "Sin Email", "El contacto actual no tiene email.")
                return
            company = self._safe_get_field(contact, 'company_name', 'No Company')
            name_field = self._safe_get_field(contact, 'Name', '')
            last_name_field = self._safe_get_field(contact, 'Last_Name', '')
            recipient_name = f"{name_field} {last_name_field}".strip()
        
            send_project_email(recipient_email, company, recipient_name)
            QMessageBox.information(self.parent, "Email Enviado", f"Se ha enviado un email a {recipient_email}.")
        # Conectar el botón "Send Email" al evento
        send_email_button.clicked.connect(send_email_current_contact)
        # --- FIN NUEVA FUNCIÓN ---
        
        # Function to display the current contact
        def display_contact():
            if self.current_contact_index < 0 or self.current_contact_index >= len(self.contacts_list):
                return
                
            # First save notes from the previous contact if any
            save_notes()
                
            contact = self.contacts_list[self.current_contact_index]
            
            # Format display with HTML - using safe field access
            try:
                city = self._safe_get_field(contact, 'City')
                state = self._safe_get_field(contact, 'State')
                country = self._safe_get_field(contact, 'Country')
                location_parts = list(filter(None, [city, state, country]))
                location = ', '.join(location_parts) if location_parts else 'Not specified'
                
                # Retrieve Timezone field
                timezone = self._safe_get_field(contact, 'Timezone', 'Not specified')
                
                html = f"""
                <div style="font-family: Arial, sans-serif;">
                    <h2>{self._safe_get_field(contact, 'Name')} {self._safe_get_field(contact, 'Last_Name')}</h2>
                    <p><b>Role:</b> {self._safe_get_field(contact, 'Role', 'Not specified')}</p>
                    <hr>
                    <p><b>Phone:</b> {self._safe_get_field(contact, 'Mobile_Phone', 'Not available')}</p>
                    <p><b>Email:</b> {self._safe_get_field(contact, 'Email', 'Not available')}</p>
                    <p><b>LinkedIn:</b> <a href="{self._safe_get_field(contact, 'LinkedIn_URL', '#')}">{self._safe_get_field(contact, 'LinkedIn_URL', 'Not available')}</a></p>
                    <hr>
                    <p><b>Company:</b> {self._safe_get_field(contact, 'company_name', 'Not specified')}</p>
                    <p><b>Location:</b> {location}</p>
                    <p><b>Timezone:</b> {timezone}</p>
                    <p><b>Batch Tag:</b> {self._safe_get_field(contact, 'campaign_batch_tag', 'Not specified')}</p>
                </div>
                """
                
                # Load notes for this contact
                notes_text.setText(self._safe_get_field(contact, 'notes', ''))
                
                # Enable/disable copy email button based on email availability
                email = self._safe_get_field(contact, 'Email', '')
                copy_email_button.setEnabled(bool(email))
                
                # Enable/disable phone buttons based on phone availability
                phone = self._safe_get_field(contact, 'Mobile_Phone', '')
                green_phone_button.setEnabled(bool(phone))
                red_phone_button.setEnabled(bool(phone))
                
                # Set tooltips for phone buttons
                if phone:
                    green_phone_button.setToolTip(f"Call {phone}")
                    red_phone_button.setToolTip(f"Call {phone}")
                else:
                    green_phone_button.setToolTip("No phone number available")
                    red_phone_button.setToolTip("No phone number available")
                
                # Get company website and LinkedIn URLs
                company_website = self._safe_get_field(contact, 'company_website', '')
                linkedin_url = self._safe_get_field(contact, 'LinkedIn_URL', '')
                
                # Auto-open website and LinkedIn URL if available
                if hasattr(self, 'browser_thread') and self.browser_thread is not None:
                    # Open company website if available
                    if company_website:
                        print(f"Opening company website: {company_website}")
                        self.browser_thread.open_website(company_website)
                    
                    # Open LinkedIn profile if available
                    if linkedin_url:
                        print(f"Opening LinkedIn profile: {linkedin_url}")
                        self.browser_thread.open_linkedin_profile(linkedin_url)
                else:
                    # Fallback to basic browser if selenium not available
                    try:
                        if company_website:
                            if not company_website.startswith(('http://', 'https://')):
                                company_website = 'https://' + company_website
                            print(f"Opening website with basic browser: {company_website}")
                            webbrowser.open(company_website)
                        
                        if linkedin_url:
                            if not linkedin_url.startswith(('http://', 'https://')):
                                linkedin_url = 'https://' + linkedin_url
                            print(f"Opening LinkedIn with basic browser: {linkedin_url}")
                            webbrowser.open(linkedin_url)
                    except Exception as e:
                        print(f"Error opening URLs: {e}")
                
            except Exception as e:
                html = f"""
                <div style="font-family: Arial, sans-serif;">
                    <h2>Error displaying contact</h2>
                    <p>There was an error accessing contact fields: {e}</p>
                </div>
                """
                # Disable buttons on error
                copy_email_button.setEnabled(False)
                green_phone_button.setEnabled(False)
                red_phone_button.setEnabled(False)
            
            contact_info.setHtml(html)
            counter_label.setText(f"Contact {self.current_contact_index + 1} of {len(self.contacts_list)}")
            
            prev_button.setEnabled(self.current_contact_index > 0)
            next_button.setEnabled(self.current_contact_index < len(self.contacts_list) - 1)
        
        # Connect navigation buttons
        prev_button.clicked.connect(lambda: self.navigate_contact(-1, display_contact))
        next_button.clicked.connect(lambda: self.navigate_contact(1, display_contact))
        
        # Function to copy email to clipboard
        def copy_email_to_clipboard():
            if self.current_contact_index < 0 or self.current_contact_index >= len(self.contacts_list):
                return
                
            contact = self.contacts_list[self.current_contact_index]
            email = self._safe_get_field(contact, 'Email', '')
            
            if email:
                from PyQt5.QtGui import QGuiApplication
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(email)
                if self.parent:
                    QMessageBox.information(self.parent, "Email Copied", f"Email address copied to clipboard: {email}")
        
        copy_email_button.clicked.connect(copy_email_to_clipboard)
        
        # Functions for coordinate capture buttons
        def capture_coordinate_a():
            coordinates = self.coordinate_selector.get_coordinate("A")
            
            if coordinates:
                x, y = coordinates
                self.coord_a = (x, y)
                
                capture_a_button.setToolTip(f"Coordinate A: ({x}, {y})")
                capture_a_button.setStyleSheet("""
                    QToolButton {
                        background-color: #2196F3;
                        color: white;
                        border-radius: 3px;
                        padding: 3px;
                        font-size: 10px;
                        font-weight: bold;
                        border: 2px solid #FFC107;
                    }
                    QToolButton:hover {
                        background-color: #0b7dda;
                    }
                """)
                print(f"Coordinate A set to: ({x}, {y})")
            
        def capture_coordinate_b():
            coordinates = self.coordinate_selector.get_coordinate("B")
            
            if coordinates:
                x, y = coordinates
                self.coord_b = (x, y)
                
                capture_b_button.setToolTip(f"Coordinate B: ({x}, {y})")
                capture_b_button.setStyleSheet("""
                    QToolButton {
                        background-color: #9C27B0;
                        color: white;
                        border-radius: 3px;
                        padding: 3px;
                        font-size: 10px;
                        font-weight: bold;
                        border: 2px solid #FFC107;
                    }
                    QToolButton:hover {
                        background-color: #7B1FA2;
                    }
                """)
                print(f"Coordinate B set to: ({x}, {y})")
        
        # Connect coordinate capture buttons
        capture_a_button.clicked.connect(capture_coordinate_a)
        capture_b_button.clicked.connect(capture_coordinate_b)
        
        # Handle dialog close event to clean up browser resources
        def on_dialog_closed():
            print("Dialog closing - cleaning up browser resources")
            if hasattr(self, 'browser_thread') and self.browser_thread is not None:
                if hasattr(self.browser_thread, 'cleanup'):
                    self.browser_thread.cleanup()
                self.browser_thread.quit()
                self.browser_thread.wait(3000)  # Wait up to 3 seconds for thread to finish
                
        dialog.finished.connect(on_dialog_closed)
        
        # Functions for phone buttons
        def on_green_phone_click():
            if self.current_contact_index < 0 or self.current_contact_index >= len(self.contacts_list):
                return
                
            save_notes()
            
            contact = self.contacts_list[self.current_contact_index]
            phone = self._safe_get_field(contact, 'Mobile_Phone', '')
            
            if not phone:
                if self.parent:
                    QMessageBox.warning(self.parent, "No Phone Number", "This contact doesn't have a phone number.")
                return
                
            if not hasattr(self, 'coord_a') or not self.coord_a:
                if self.parent:
                    QMessageBox.warning(self.parent, "Coordinate Missing", "Please set coordinate A first by clicking the A button.")
                return
                
            if not hasattr(self, 'coord_b') or not self.coord_b:
                if self.parent:
                    QMessageBox.warning(self.parent, "Coordinate Missing", "Please set coordinate B first by clicking the B button.")
                return
                
            if not PYAUTOGUI_AVAILABLE:
                if self.parent:
                    QMessageBox.critical(self.parent, "Missing Dependency", 
                        "pyautogui is not available. Please install it with: pip install pyautogui")
                return
                
            try:
                from PyQt5.QtGui import QGuiApplication
                
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(phone)
                
                pyautogui.click(self.coord_a[0], self.coord_a[1])
                time.sleep(0.5)
                
                if sys.platform == 'darwin':
                    pyautogui.hotkey('command', 'v')
                else:
                    pyautogui.hotkey('ctrl', 'v')
                
                time.sleep(0.5)
                pyautogui.click(self.coord_b[0], self.coord_b[1])
                
            except Exception as e:
                if self.parent:
                    QMessageBox.critical(self.parent, "Error", f"Error during automatic dialing: {str(e)}")
        
        def on_red_phone_click():
            if self.current_contact_index < 0 or self.current_contact_index >= len(self.contacts_list):
                return
                
            save_notes()
            
            if not hasattr(self, 'coord_b') or not self.coord_b:
                if self.parent:
                    QMessageBox.warning(self.parent, "Coordinate Missing", "Please set coordinate B first by clicking the B button.")
                return
                
            if not PYAUTOGUI_AVAILABLE:
                if self.parent:
                    QMessageBox.critical(self.parent, "Missing Dependency", 
                        "pyautogui is not available. Please install it with: pip install pyautogui")
                return
                
            try:
                pyautogui.click(self.coord_b[0], self.coord_b[1])
                
            except Exception as e:
                if self.parent:
                    QMessageBox.critical(self.parent, "Error", f"Error during automatic hangup: {str(e)}")
        
        green_phone_button.clicked.connect(on_green_phone_click)
        red_phone_button.clicked.connect(on_red_phone_click)
        
        dialog.finished.connect(save_notes)
        
        remove_button.clicked.connect(lambda: [save_notes(), self.remove_contact(display_contact)])
        remove_all_button.clicked.connect(lambda: [save_notes(), self.remove_all_contacts(display_contact)])
        opportunity_button.clicked.connect(lambda: [save_notes(), self.mark_as_opportunity(display_contact)])
        
        display_contact()
        
        dialog.exec_()
    
    def navigate_contact(self, direction, update_function):
        new_index = self.current_contact_index + direction
        if 0 <= new_index < len(self.contacts_list):
            self.current_contact_index = new_index
            update_function()
            
    
    def remove_contact(self, update_function):
        if not self.contacts_list or self.current_contact_index < 0:
            return
            
        contact = self.contacts_list[self.current_contact_index]
        contact_id = None
        counter = None
        notes = None
        
        try:
            contact_id = str(contact['contact_id'])
            counter = self._safe_get_field(contact, 'counter')
            notes = self._safe_get_field(contact, 'notes', '')
        except:
            try:
                contact_id = str(contact['id'])
            except:
                contact_dict = dict(contact)
                contact_id = contact_dict.get('contact_id') or contact_dict.get('id')
                counter = contact_dict.get('counter')
                notes = contact_dict.get('notes', '')
        
        if contact_id:
            contact_id = str(contact_id)
            
        if not contact_id:
            if self.parent:
                QMessageBox.warning(self.parent, "Error", "Contact ID not found despite all attempts to retrieve it.")
            return
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            try:
                from PyQt5.QtWidgets import QTextEdit
                for widget in self.parent.findChildren(QTextEdit):
                    if widget.placeholderText() and "notes" in widget.placeholderText().lower():
                        notes = widget.toPlainText()
                        break
            except:
                pass
            
            if counter:
                cursor.execute(
                    "UPDATE contacts_campaign SET current_state = 'rejected', reason = 'Manually rejected', notes = ? WHERE counter = ?",
                    (notes, counter)
                )
            else:
                cursor.execute(
                    "UPDATE contacts_campaign SET current_state = 'rejected', reason = 'Manually rejected', notes = ? WHERE contact_id = ? AND current_state = 'approved'",
                    (notes, contact_id)
                )
            
            conn.commit()
            conn.close()
            
            self.contacts_list.pop(self.current_contact_index)
            
            if not self.contacts_list:
                if self.parent:
                    QMessageBox.information(self.parent, "All Contacts Processed", 
                        "All contacts have been processed. The dialog will now close."
                    )
                return
            
            if self.current_contact_index >= len(self.contacts_list):
                self.current_contact_index = len(self.contacts_list) - 1
            
            update_function()
            
            if self.parent:
                QMessageBox.information(self.parent, "Contact Removed", 
                    f"Contact {self._safe_get_field(contact, 'Name')} {self._safe_get_field(contact, 'Last_Name')} has been removed."
                )
            
        except Exception as e:
            if self.parent:
                QMessageBox.critical(self.parent, "Error", f"Error removing contact: {str(e)}")
    
    def remove_all_contacts(self, update_function):
        if not self.contacts_list or self.current_contact_index < 0:
            return
            
        try:
            contact = self.contacts_list[self.current_contact_index]
            contact_dict = dict(contact)
            company_id = contact_dict.get('company_id')
            
            if not company_id:
                if self.parent:
                    QMessageBox.warning(self.parent, "Error", "Company ID not found for this contact.")
                return
                
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT campaign_id 
                FROM contacts_campaign 
                WHERE contact_id IN (
                    SELECT contact_id FROM contacts WHERE company_id = ?
                )
                LIMIT 1
            """, (company_id,))
            
            result = cursor.fetchone()
            if not result:
                if self.parent:
                    QMessageBox.warning(self.parent, "Error", "Could not find campaign for these contacts.")
                conn.close()
                return
                
            campaign_id = result[0]
            
            notes = ""
            try:
                from PyQt5.QtWidgets import QTextEdit
                for widget in self.parent.findChildren(QTextEdit):
                    if widget.placeholderText() and "notes" in widget.placeholderText().lower():
                        notes = widget.toPlainText()
                        break
            except:
                pass
                
            cursor.execute("""
                UPDATE contacts_campaign 
                SET current_state = 'rejected', reason = 'All company contacts rejected', notes = ? 
                WHERE contact_id IN (
                    SELECT contact_id FROM contacts WHERE company_id = ?
                )
                AND campaign_id = ? 
                AND current_state = 'approved'
            """, (notes, company_id, campaign_id))
            
            contacts_updated = cursor.rowcount
            
            cursor.execute("""
                UPDATE companies_campaign 
                SET current_state = 'rejected', reason = 'All contacts rejected' 
                WHERE company_id = ? 
                AND campaign_id = ? 
                AND current_state = 'approved'
            """, (company_id, campaign_id))
            
            company_updated = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            indices_to_remove = []
            for i, c in enumerate(self.contacts_list):
                try:
                    c_dict = dict(c)
                    if c_dict.get('company_id') == company_id:
                        indices_to_remove.append(i)
                except:
                    pass
                    
            for i in sorted(indices_to_remove, reverse=True):
                if i < len(self.contacts_list):
                    self.contacts_list.pop(i)
            
            if self.parent:
                QMessageBox.information(
                    self.parent, 
                    "Update Complete", 
                    f"Updated {contacts_updated} contacts and {company_updated} companies to rejected state."
                )
            
            if not self.contacts_list:
                if self.parent:
                    QMessageBox.information(self.parent, "All Contacts Processed", 
                        "All contacts have been processed. The dialog will now close."
                    )
                return
            
            if self.current_contact_index >= len(self.contacts_list):
                self.current_contact_index = len(self.contacts_list) - 1
                
            update_function()
            
        except Exception as e:
            if self.parent:
                QMessageBox.critical(self.parent, "Error", f"Error removing contacts: {str(e)}")
    
    def mark_as_opportunity(self, update_function):
        if not self.contacts_list or self.current_contact_index < 0:
            return
            
        try:
            contact = self.contacts_list[self.current_contact_index]
            contact_dict = dict(contact)
            company_id = contact_dict.get('company_id')
            contact_id = contact_dict.get('contact_id')
            counter = contact_dict.get('counter')
            notes = contact_dict.get('notes', '')
            
            try:
                from PyQt5.QtWidgets import QTextEdit
                for widget in self.parent.findChildren(QTextEdit):
                    if widget.placeholderText() and "notes" in widget.placeholderText().lower():
                        notes = widget.toPlainText()
                        break
            except:
                pass
            
            if not company_id:
                if self.parent:
                    QMessageBox.warning(self.parent, "Error", "Company ID not found for this contact.")
                return
                
            if not contact_id:
                if self.parent:
                    QMessageBox.warning(self.parent, "Error", "Contact ID not found.")
                return
                
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id TEXT,
                    company_id TEXT,
                    name TEXT,
                    last_name TEXT,
                    role TEXT,
                    email TEXT,
                    phone TEXT,
                    linkedin_url TEXT,
                    company_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'new',
                    notes TEXT,
                    FOREIGN KEY (contact_id) REFERENCES contacts(contact_id),
                    FOREIGN KEY (company_id) REFERENCES companies(company_id)
                )
            """)
            
            cursor.execute("""
                SELECT DISTINCT campaign_id 
                FROM contacts_campaign 
                WHERE contact_id IN (
                    SELECT contact_id FROM contacts WHERE company_id = ?
                )
                LIMIT 1
            """, (company_id,))
            
            result = cursor.fetchone()
            if not result:
                if self.parent:
                    QMessageBox.warning(self.parent, "Error", "Could not find campaign for these contacts.")
                conn.close()
                return
                
            campaign_id = result[0]
            
            cursor.execute(
                """
                INSERT INTO opportunities (
                    contact_id, company_id, name, last_name, role, email, phone, linkedin_url, company_name, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contact_id, 
                    company_id,
                    self._safe_get_field(contact, 'Name'),
                    self._safe_get_field(contact, 'Last_Name'),
                    self._safe_get_field(contact, 'Role'),
                    self._safe_get_field(contact, 'Email'),
                    self._safe_get_field(contact, 'Mobile_Phone'),
                    self._safe_get_field(contact, 'LinkedIn_URL'),
                    self._safe_get_field(contact, 'company_name'),
                    notes
                )
            )
            
            cursor.execute("""
                UPDATE contacts_campaign 
                SET current_state = 'rejected', reason = 'Marked as opportunity' 
                WHERE contact_id IN (
                    SELECT contact_id FROM contacts WHERE company_id = ?
                )
                AND campaign_id = ? 
                AND current_state = 'approved'
            """, (company_id, campaign_id))
            
            contacts_updated = cursor.rowcount
            
            cursor.execute("""
                UPDATE companies_campaign 
                SET current_state = 'rejected', reason = 'Marked as opportunity' 
                WHERE company_id = ? 
                AND campaign_id = ? 
                AND current_state = 'approved'
            """, (company_id, campaign_id))
            
            company_updated = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            indices_to_remove = []
            for i, c in enumerate(self.contacts_list):
                try:
                    c_dict = dict(c)
                    if c_dict.get('company_id') == company_id:
                        indices_to_remove.append(i)
                except:
                    pass
                    
            for i in sorted(indices_to_remove, reverse=True):
                if i < len(self.contacts_list):
                    self.contacts_list.pop(i)
            
            if self.parent:
                QMessageBox.information(
                    self.parent, 
                    "Opportunity Created", 
                    f"Contact has been marked as an opportunity.\n\n"
                    f"Updated {contacts_updated} contacts and {company_updated} companies to rejected state."
                )
            
            if not self.contacts_list:
                if self.parent:
                    QMessageBox.information(self.parent, "All Contacts Processed", 
                        "All contacts have been processed. The dialog will now close."
                    )
                return
            
            if self.current_contact_index >= len(self.contacts_list):
                self.current_contact_index = len(self.contacts_list) - 1
                
            update_function()
            
        except Exception as e:
            if self.parent:
                QMessageBox.critical(self.parent, "Error", f"Error marking as opportunity: {str(e)}")

# For standalone testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Phone Dialer")
    window.setMinimumSize(800, 600)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Create layout
    layout = QVBoxLayout(central_widget)
    
    # Create header
    header_label = QLabel("Phone Dialer Test")
    header_label.setAlignment(Qt.AlignCenter)
    header_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
    layout.addWidget(header_label)
    
    # For demonstration purposes, we'll create a dummy combo box for campaigns and batches
    from PyQt5.QtWidgets import QComboBox, QPushButton
    campaign_combo = QComboBox()
    batch_combo = QComboBox()
    layout.addWidget(campaign_combo)
    layout.addWidget(batch_combo)
    
    # Instantiate PhoneDialerApp
    dialer_app = PhoneDialerApp(window)
    
    # Dummy load campaigns into the combo boxes (this assumes that load_campaigns works without actual database data)
    dialer_app.load_campaigns(campaign_combo, batch_combo)
    
    # Dummy button to load contacts and show dialog (for testing)
    def show_dialog():
        campaign_id = campaign_combo.itemData(campaign_combo.currentIndex())
        batch_tag = batch_combo.itemData(batch_combo.currentIndex())
        if dialer_app.load_contacts(campaign_id, batch_tag):
            dialer_app.show_contacts_dialog(campaign_combo.currentText(), batch_tag)
    
    test_button = QPushButton("Show Contacts Dialog")
    test_button.clicked.connect(show_dialog)
    layout.addWidget(test_button)
    
    # Show window
    window.show()
    
    sys.exit(app.exec_())
