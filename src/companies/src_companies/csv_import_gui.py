import sys
import os
import pandas as pd
import json
import uuid
import sqlite3
from sqlite3 import Error
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                            QTableWidget, QTableWidgetItem, QComboBox, QMessageBox,
                            QHeaderView, QDialog, QLineEdit, QFormLayout, QGroupBox,
                            QRadioButton, QButtonGroup, QScrollArea, QProgressBar,
                            QSplitter, QTabWidget, QFrame, QStatusBar, QProgressDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

# Import local modules
from db_initializer import check_for_database
from preprocessor import preprocessor, clean_url
from csv_parser import get_db_columns, load_previous_mappings, save_mappings, create_new_column, create_new_table

# ANSI color codes for console output if needed
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

class NewColumnDialog(QDialog):
    """Dialog for creating a new column in an existing table"""
    def __init__(self, db_tables, parent=None):
        super().__init__(parent)
        self.db_tables = db_tables
        self.result_table = None
        self.result_column = None
        self.result_type = None
        
        self.setWindowTitle("Create New Column")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Table selection
        table_group = QGroupBox("Select Table")
        table_layout = QVBoxLayout()
        
        self.table_combo = QComboBox()
        self.table_combo.addItems(sorted(db_tables.keys()))
        table_layout.addWidget(self.table_combo)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Column name
        column_group = QGroupBox("New Column Details")
        column_layout = QFormLayout()
        
        self.column_name = QLineEdit()
        column_layout.addRow("Column Name:", self.column_name)
        
        self.column_type = QComboBox()
        self.column_type.addItems(["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"])
        column_layout.addRow("Column Type:", self.column_type)
        
        column_group.setLayout(column_layout)
        layout.addWidget(column_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create Column")
        self.create_button.clicked.connect(self.accept_column)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def accept_column(self):
        self.result_table = self.table_combo.currentText()
        self.result_column = self.column_name.text()
        self.result_type = self.column_type.currentText()
        
        if not self.result_column:
            QMessageBox.warning(self, "Error", "Please enter a column name")
            return
            
        # Check if column already exists
        if self.result_column in self.db_tables[self.result_table]:
            QMessageBox.warning(self, "Error", 
                               f"Column '{self.result_column}' already exists in table '{self.result_table}'")
            return
        
        self.accept()

class NewTableDialog(QDialog):
    """Dialog for creating a new table"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_table = None
        self.result_columns = []
        
        self.setWindowTitle("Create New Table")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Table name
        table_group = QGroupBox("New Table Details")
        table_layout = QFormLayout()
        
        self.table_name = QLineEdit()
        table_layout.addRow("Table Name:", self.table_name)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Columns
        column_group = QGroupBox("Columns (company_id will be added automatically)")
        column_layout = QVBoxLayout()
        
        self.columns_widget = QWidget()
        self.columns_layout = QVBoxLayout(self.columns_widget)
        
        # Initial column row
        self.add_column_row()
        
        column_scroll = QScrollArea()
        column_scroll.setWidgetResizable(True)
        column_scroll.setWidget(self.columns_widget)
        
        column_layout.addWidget(column_scroll)
        
        # Add another column button
        add_column_button = QPushButton("+ Add Another Column")
        add_column_button.clicked.connect(self.add_column_row)
        column_layout.addWidget(add_column_button)
        
        column_group.setLayout(column_layout)
        layout.addWidget(column_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create Table")
        self.create_button.clicked.connect(self.accept_table)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_column_row(self):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        
        column_name = QLineEdit()
        column_name.setPlaceholderText("Column Name")
        
        column_type = QComboBox()
        column_type.addItems(["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"])
        
        delete_button = QPushButton("✕")
        delete_button.setFixedWidth(30)
        delete_button.clicked.connect(lambda: self.delete_column_row(row_widget))
        
        row_layout.addWidget(column_name)
        row_layout.addWidget(column_type)
        row_layout.addWidget(delete_button)
        
        self.columns_layout.addWidget(row_widget)
    
    def delete_column_row(self, row_widget):
        # Make sure we don't delete the last row
        if self.columns_layout.count() > 1:
            row_widget.deleteLater()
    
    def accept_table(self):
        self.result_table = self.table_name.text()
        
        if not self.result_table:
            QMessageBox.warning(self, "Error", "Please enter a table name")
            return
        
        # Get all columns
        self.result_columns = []
        for i in range(self.columns_layout.count()):
            row_widget = self.columns_layout.itemAt(i).widget()
            if row_widget:
                row_layout = row_widget.layout()
                
                name_widget = row_layout.itemAt(0).widget()
                type_widget = row_layout.itemAt(1).widget()
                
                column_name = name_widget.text()
                column_type = type_widget.currentText()
                
                if column_name:
                    self.result_columns.append((column_name, column_type))
        
        if not self.result_columns:
            QMessageBox.warning(self, "Error", "Please add at least one column")
            return
        
        # Check for duplicate columns
        column_names = [col[0] for col in self.result_columns]
        if len(column_names) != len(set(column_names)):
            QMessageBox.warning(self, "Error", "Duplicate column names detected")
            return
        
        self.accept()

class StepByStepMappingDialog(QMainWindow):
    """Dialog for step-by-step field mapping with buttons for each table/field"""
    # Add a custom signal to emulate the finished signal that QDialog has
    finished = None
    def __init__(self, csv_columns, db_tables, previous_mappings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Column Mapping")
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        
        # Store parameters
        self.csv_columns = csv_columns
        self.db_tables = db_tables
        self.previous_mappings = previous_mappings or {}
        
        # Current state
        self.current_column_index = 0
        self.mappings = {}  # Will store final mappings
        
        # First ask if user wants to use previous mappings
        if self.previous_mappings:
            self.ask_for_previous_mappings()
        else:
            # Setup mapping UI
            self.init_ui()
            # Show first column
            self.show_current_column()

    def ask_for_previous_mappings(self):
        # Create central widget for previous mappings question
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add message
        message_label = QLabel("Company Mapping")
        message_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        message_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(message_label)
        
        # Add description
        desc_label = QLabel(f"We found {len(self.previous_mappings)} previously mapped columns for this file format.")
        desc_label.setStyleSheet("font-size: 14px; margin-bottom: 30px;")
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        previous_button = QPushButton("Use Previous Mappings")
        previous_button.setStyleSheet("font-size: 14px; padding: 15px; background-color: #4CAF50; color: white; font-weight: bold;")
        previous_button.clicked.connect(self.use_previous_mappings)
        button_layout.addWidget(previous_button)
        
        new_button = QPushButton("Create New Mappings")
        new_button.setStyleSheet("font-size: 14px; padding: 15px;")
        new_button.clicked.connect(self.create_new_mappings)
        button_layout.addWidget(new_button)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
    def use_previous_mappings(self):
        """Use the previous mappings"""
        self.mappings = self.previous_mappings.copy()
        
        # Debug output
        print(f"Using previous mappings: {self.mappings}")
        
        # When using previous mappings, we jump straight to batch tag entry
        self.parent().batch_group.setVisible(True)
        self.parent().batch_tag_input.setFocus()
        self.parent().import_button.setVisible(True)
        
        self.close()
        
    def create_new_mappings(self):
        """Start the mapping process from scratch"""
        # Setup mapping UI
        self.init_ui()
        # Show first column
        self.show_current_column()
        
    def init_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Current column area
        self.column_group = QGroupBox("Current Column")
        column_layout = QVBoxLayout()
        
        # Column name and sample data
        self.column_name_label = QLabel()
        self.column_name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        column_layout.addWidget(self.column_name_label)
        
        self.column_data_label = QLabel()
        self.column_data_label.setWordWrap(True)
        self.column_data_label.setStyleSheet("color: #555; margin-bottom: 10px;")
        column_layout.addWidget(self.column_data_label)
        
        # Field mapping area
        self.fields_area = QScrollArea()
        self.fields_area.setWidgetResizable(True)
        self.fields_widget = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_widget)
        
        # Add skip button at the top
        skip_group = QGroupBox("Skip This Field")
        skip_layout = QVBoxLayout()
        skip_button = QPushButton("Skip this column")
        skip_button.setStyleSheet("font-size: 14px; padding: 10px;")
        skip_button.clicked.connect(lambda: self.select_mapping("skip"))
        skip_layout.addWidget(skip_button)
        skip_group.setLayout(skip_layout)
        self.fields_layout.addWidget(skip_group)
        
        # Add groups for each table with buttons for fields
        for table_name in sorted(self.db_tables.keys()):
            group = QGroupBox(table_name)
            table_layout = QHBoxLayout()
            table_layout.setSpacing(5)
            table_layout.setAlignment(Qt.AlignLeft)
            
            # Flow layout container for buttons
            flow_widget = QWidget()
            flow_layout = QHBoxLayout(flow_widget)
            flow_layout.setSpacing(5)
            flow_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add buttons for each column in this table
            buttons_added = 0
            for column in sorted(self.db_tables[table_name]):
                # Skip special columns
                if column in ['company_id', 'location_id', 'phone_id', 'tech_id', 
                             'industry_id', 'identifier_id', 'link_id', 'event_id', 
                             'verification_id', 'rating_id', 'review_id']:
                    continue
                
                # Create button
                button = QPushButton(column)
                button.setStyleSheet("padding: 8px; font-size: 13px;")
                button.clicked.connect(lambda _, t=table_name, c=column: self.select_mapping(f"{t}.{c}"))
                
                # Add to flow layout
                flow_layout.addWidget(button)
                buttons_added += 1
                
                # Add a line break every 4-5 buttons
                if buttons_added % 4 == 0:
                    flow_layout.addStretch()
            
            # Add the flow widget to table layout
            table_layout.addWidget(flow_widget)
            table_layout.addStretch()
            
            # Only add tables that have valid columns
            if buttons_added > 0:
                group.setLayout(table_layout)
                self.fields_layout.addWidget(group)
            
        # Add create new options at the bottom
        create_group = QGroupBox("Create New")
        create_layout = QVBoxLayout()
        
        create_column_button = QPushButton("Create New Column")
        create_column_button.setStyleSheet("font-size: 14px; padding: 10px;")
        create_column_button.clicked.connect(self.create_new_column)
        create_layout.addWidget(create_column_button)
        
        create_table_button = QPushButton("Create New Table")
        create_table_button.setStyleSheet("font-size: 14px; padding: 10px;")
        create_table_button.clicked.connect(self.create_new_table)
        create_layout.addWidget(create_table_button)
        
        create_group.setLayout(create_layout)
        self.fields_layout.addWidget(create_group)
        
        # Add the fields widget to the scroll area
        self.fields_area.setWidget(self.fields_widget)
        column_layout.addWidget(self.fields_area)
        
        self.column_group.setLayout(column_layout)
        main_layout.addWidget(self.column_group)
        
        # Progress area
        progress_group = QGroupBox("Mapping Progress")
        progress_layout = QVBoxLayout()
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(self.csv_columns))
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        # Add progress label
        self.progress_label = QLabel()
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Add navigation buttons
        button_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("← Previous Column")
        self.prev_button.clicked.connect(self.prev_column)
        button_layout.addWidget(self.prev_button)
        
        button_layout.addStretch()
        
        self.finish_button = QPushButton("Finish Mapping")
        self.finish_button.clicked.connect(self.accept)
        self.finish_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.finish_button)
        
        main_layout.addLayout(button_layout)
        
        # Set up status bar
        self.statusBar().showMessage("Select a mapping for the current column")
        
    def show_current_column(self):
        """Display the current column for mapping"""
        # Check if we've reached the end
        if self.current_column_index >= len(self.csv_columns):
            # We're done with mapping
            self.column_group.setVisible(False)
            self.finish_button.setText("Import Data")
            self.statusBar().showMessage("All columns mapped. Click 'Import Data' to continue.")
            return
        
        # Get current column
        column_name = self.csv_columns[self.current_column_index]
        
        # Update UI
        self.column_name_label.setText(f"Column: {column_name}")
        
        # We're no longer showing sample values to save space
        self.column_data_label.setText("")
        
        # Calculate percentage of total mapping progress (not including company tag)
        # This ensures the progress bar reaches 100% when all columns are mapped
        progress_percentage = int((self.current_column_index / len(self.csv_columns)) * 100)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(progress_percentage)
        self.progress_label.setText(f"Mapping column {self.current_column_index + 1} of {len(self.csv_columns)} ({progress_percentage}%)")
        
        # Disable prev button if we're at the first column
        self.prev_button.setEnabled(self.current_column_index > 0)
    
    def select_mapping(self, mapping):
        """When a mapping is selected for the current column"""
        # Get current column
        if self.current_column_index >= len(self.csv_columns):
            return
            
        column_name = self.csv_columns[self.current_column_index]
        
        # Save mapping
        if mapping != "skip":
            self.mappings[column_name] = mapping
            self.statusBar().showMessage(f"Mapped '{column_name}' to '{mapping}'")
        else:
            # Skip this column (remove any existing mapping)
            if column_name in self.mappings:
                del self.mappings[column_name]
            self.statusBar().showMessage(f"Skipped column '{column_name}'")
        
        # Go to next column
        self.current_column_index += 1
        self.show_current_column()
        
    def create_new_column(self):
        """Show dialog to create a new column"""
        dialog = NewColumnDialog(self.db_tables, self)
        if dialog.exec_():
            try:
                # Create the new column in the database
                table_name = dialog.result_table
                column_name = dialog.result_column
                column_type = dialog.result_type
                
                create_new_column(table_name, column_name_db=column_name, column_type=column_type)
                
                # Update our database schema
                self.db_tables = get_db_columns()
                
                # Refresh the UI to include the new column
                central_widget = self.centralWidget()
                central_widget.deleteLater()
                self.init_ui()
                self.show_current_column()
                
                # Select this mapping for the current column
                mapping = f"{table_name}.{column_name}"
                self.select_mapping(mapping)
                
                # Show success message
                self.statusBar().showMessage(f"Created new column {column_name} in table {table_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create new column: {str(e)}")
    
    def create_new_table(self):
        """Show dialog to create a new table"""
        dialog = NewTableDialog(self)
        if dialog.exec_():
            try:
                # Create the new table in the database
                table_name = dialog.result_table
                columns = dialog.result_columns
                
                # Convert columns to the format expected by create_new_table
                column_defs = {}
                for col_name, col_type in columns:
                    column_defs[col_name] = col_type
                
                create_new_table(table_name, column_defs)
                
                # Update our database schema
                self.db_tables = get_db_columns()
                
                # Refresh the UI to include the new table
                central_widget = self.centralWidget()
                central_widget.deleteLater()
                self.init_ui()
                self.show_current_column()
                
                # Select the first column of the new table for the current CSV column
                mapping = f"{table_name}.{columns[0][0]}"
                self.select_mapping(mapping)
                
                # Show success message
                self.statusBar().showMessage(f"Created new table {table_name} with {len(columns)} columns")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create new table: {str(e)}")
    
    def prev_column(self):
        """Go to the previous column"""
        if self.current_column_index > 0:
            self.current_column_index -= 1
            self.show_current_column()
    
    def accept(self):
        """Finish mapping and return the mappings"""
        if self.current_column_index < len(self.csv_columns):
            # We still have columns to map
            confirm = QMessageBox.question(
                self, 
                "Incomplete Mapping", 
                f"You still have {len(self.csv_columns) - self.current_column_index} columns to map. Are you sure you want to finish?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return
        
        # Set progress to 100% when user finishes mapping
        self.progress_bar.setValue(100)
        self.progress_label.setText("Mapping complete (100%)")
        
        self.close()


class CSVImportWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize instance variables
        self.csv_file_path = None
        self.df = None
        self.db_tables = None
        self.mappings = {}
        self.previous_mappings = None
        self.batch_tag = None
        
        # Set up UI
        self.init_ui()
        
        # Verify database
        self.verify_database()
    
    def init_ui(self):
        self.setWindowTitle("CSV Import Tool")
        self.setMinimumSize(700, 400)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # File selection area
        file_group = QGroupBox("CSV File Selection")
        file_layout = QHBoxLayout()
        
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("padding: 5px;")
        file_layout.addWidget(self.file_path_label, 1)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_button)
        
        file_group.setLayout(file_layout)
        self.main_layout.addWidget(file_group)
        
        # Previous mappings area
        self.prev_mappings_group = QGroupBox("Previous Mappings")
        self.prev_mappings_group.setVisible(False)
        prev_mappings_layout = QVBoxLayout()
        
        self.prev_mappings_label = QLabel("Previous column mappings found for this file format.")
        prev_mappings_layout.addWidget(self.prev_mappings_label)
        
        prev_buttons_layout = QHBoxLayout()
        self.use_prev_button = QPushButton("Use Previous Mappings")
        self.use_prev_button.clicked.connect(self.use_previous_mappings)
        self.use_prev_button.setStyleSheet("background-color: #4CAF50; color: white;")
        
        self.remap_button = QPushButton("Remap Columns")
        self.remap_button.clicked.connect(self.start_mapping)
        
        prev_buttons_layout.addWidget(self.use_prev_button)
        prev_buttons_layout.addWidget(self.remap_button)
        
        prev_mappings_layout.addLayout(prev_buttons_layout)
        self.prev_mappings_group.setLayout(prev_mappings_layout)
        self.main_layout.addWidget(self.prev_mappings_group)
        
        # Batch area
        self.batch_group = QGroupBox("Batch Information")
        self.batch_group.setVisible(False)
        batch_layout = QFormLayout()
        
        self.batch_tag_input = QLineEdit()
        self.batch_tag_input.setPlaceholderText("e.g., initial, follow-up, test")
        batch_layout.addRow("Batch Tag:", self.batch_tag_input)
        
        self.batch_group.setLayout(batch_layout)
        self.main_layout.addWidget(self.batch_group)
        
        # Button area
        self.button_layout = QHBoxLayout()
        
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.back_button)
        
        self.button_layout.addStretch()
        
        self.start_mapping_button = QPushButton("Start Mapping")
        self.start_mapping_button.clicked.connect(self.start_mapping)
        self.start_mapping_button.setVisible(False)
        self.start_mapping_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.button_layout.addWidget(self.start_mapping_button)
        
        self.import_button = QPushButton("Import Data")
        self.import_button.clicked.connect(self.import_data)
        self.import_button.setVisible(False)
        self.import_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.button_layout.addWidget(self.import_button)
        
        self.main_layout.addLayout(self.button_layout)
        
        # Add space at the bottom
        self.main_layout.addStretch()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Start by selecting a CSV file.")
    
    def verify_database(self):
        """Verify database connection and get table schemas"""
        try:
            # Check database connection
            if not check_for_database():
                QMessageBox.critical(self, "Database Error", 
                                   "Database check failed. Please make sure the database is properly initialized.")
                self.close()
                return
            
            # Get database tables and columns
            self.db_tables = get_db_columns()
            
            # Set status message
            self.status_bar.showMessage("Database verified. Ready to import CSV data.")
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error verifying database: {str(e)}")
            self.close()
    
    def browse_file(self):
        """Open file dialog to select CSV file"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        
        if file_path:
            self.csv_file_path = file_path
            self.file_path_label.setText(file_path)
            self.status_bar.showMessage(f"Selected file: {file_path}")
            
            # Try to load the CSV file
            try:
                self.df = pd.read_csv(file_path)
                
                # Check if file has at least one row
                if len(self.df) == 0:
                    QMessageBox.warning(self, "Empty File", "The selected CSV file is empty.")
                    return
                
                # Check if previous mappings exist using the file path
                self.previous_mappings = load_previous_mappings(file_path)
                
                # Hide batch group until mapping is complete
                self.batch_group.setVisible(False)
                
                # Go directly to mapping screen
                self.start_mapping()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")
    
    def use_previous_mappings(self):
        """Use previously saved mappings for this file"""
        if not self.previous_mappings:
            return
            
        # Use the previous mappings directly
        self.mappings = self.previous_mappings.copy()
        
        # Debug output
        print(f"Using previous mappings: {self.mappings}")
        
        # Hide the previous mappings group and show import button
        self.prev_mappings_group.setVisible(False)
        self.start_mapping_button.setVisible(False)
        self.import_button.setVisible(True)
        
        # Show success message
        self.status_bar.showMessage(f"Using previous mappings with {len(self.mappings)} columns mapped. Enter a batch tag and click Import.")
    
    def start_mapping(self):
        """Start the step-by-step mapping process"""
        # First check that we have CSV data
        if self.df is None or len(self.df.columns) == 0:
            QMessageBox.warning(self, "No Data", "Please select a CSV file first.")
            return
        
        # Create the step-by-step mapping dialog
        dialog = StepByStepMappingDialog(
            csv_columns=list(self.df.columns),
            db_tables=self.db_tables,
            previous_mappings=self.previous_mappings,
            parent=self
        )
        
        # Show the dialog (non-modal so you can still see the main window)
        dialog.show()
        
        # Connect to dialog closing
        # Use closeEvent instead of finished signal since QMainWindow doesn't have finished
        dialog.closeEvent = lambda event: self.mapping_completed(dialog)
    
    def mapping_completed(self, dialog):
        """Called when the mapping dialog is closed"""
        # Get the mappings from the dialog
        self.mappings = dialog.mappings
        
        # Debug output 
        print(f"Received mappings from dialog: {self.mappings}")
        
        # Show the import button if we have mappings
        if self.mappings:
            # Now show batch tag input after mapping is complete
            self.batch_group.setVisible(True)
            self.batch_tag_input.setFocus()
            
            # Show import button
            self.import_button.setVisible(True)
            
            # Show success message
            self.status_bar.showMessage(f"Mapping completed with {len(self.mappings)} columns mapped. Enter a batch tag and click Import.")
        else:
            # No mappings created - create default mappings from column names
            print("No mappings received. Creating basic default mappings.")
            default_mappings = {}
            
            for col in self.df.columns:
                col_lower = col.lower()
                # Map some common columns by name
                if col_lower in ['name', 'company', 'company_name']:
                    default_mappings[col] = 'companies.name'
                elif col_lower in ['website', 'url', 'web']:
                    default_mappings[col] = 'companies.website'
                elif col_lower in ['email', 'company_email']:
                    default_mappings[col] = 'companies.email'
                elif col_lower in ['phone', 'contact', 'telephone']:
                    default_mappings[col] = 'companies.phone'
                elif col_lower in ['address', 'location', 'hq']:
                    default_mappings[col] = 'companies.address'
                elif col_lower in ['description', 'about', 'summary']:
                    default_mappings[col] = 'companies.description'
                elif col_lower in ['founded', 'founding_date', 'start_date']:
                    default_mappings[col] = 'companies.founded'
                elif col_lower in ['revenue', 'earnings']:
                    default_mappings[col] = 'companies.revenue'
                elif col_lower in ['headcount', 'employees', 'employee_count']:
                    default_mappings[col] = 'companies.headcount'
            
            if default_mappings:
                print(f"Created default mappings: {default_mappings}")
                self.mappings = default_mappings
                self.batch_group.setVisible(True)
                self.batch_tag_input.setFocus()
                self.import_button.setVisible(True)
                self.status_bar.showMessage(f"Created {len(default_mappings)} default mappings. Enter a batch tag and click Import.")
            else:
                # No mappings created and couldn't create defaults
                self.status_bar.showMessage("Mapping cancelled or no columns were mapped.")
                
                # Go back to file selection
                self.browse_button.setFocus()
                
    # Old method - not used anymore with new UI
    def generate_mapping_ui(self):
        pass
    
    def import_data(self):
        """Process the CSV import with the current mappings using the csv_parser approach"""
        # Validate batch tag
        batch_tag = self.batch_tag_input.text().strip()
        if not batch_tag:
            QMessageBox.warning(self, "Missing Batch Tag", "Please enter a batch tag")
            self.batch_tag_input.setFocus()
            return
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Prepare progress dialog
        progress = QProgressDialog("Importing data...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Import Progress")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        try:
            progress.setValue(10)
            progress.setLabelText("Saving mappings...")
            
            # Save mappings for future use with the file path for persistent mapping
            save_mappings(self.mappings, self.csv_file_path)
            
            # COMPLETELY NEW APPROACH: Use csv_parser's approach directly
            progress.setValue(30)
            progress.setLabelText("Preparing data for preprocessing...")
            
            # Get the project root directory (works for both approaches)
            project_root = os.environ.get('PROJECT_ROOT')
            if not project_root:
                # Fallback to calculating the path - ensure we get to the parent of src
                script_dir = os.path.dirname(os.path.abspath(__file__))  # src_companies dir
                src_companies_dir = os.path.dirname(script_dir)          # companies dir
                companies_dir = os.path.dirname(src_companies_dir)       # src dir
                project_root = os.path.dirname(companies_dir)            # project root
            
            os.environ['PROJECT_ROOT'] = project_root
            print(f"Using project root: {project_root}")
            
            # Get all dataframe records as dictionary
            records = self.df.to_dict(orient="records")
            print(f"Prepared {len(records)} records for import")
            
            # Process the data directly using the preprocessor
            progress.setValue(50)
            progress.setLabelText("Processing data through preprocessor...")
            
            # Directly using preprocessor
            from preprocessor import preprocessor
            print(f"Calling preprocessor with {len(records)} records, batch_id: {batch_id}, batch_tag: {batch_tag}")
            
            # Convert mappings to the exact format the csv_parser uses
            # From csv_parser.py - we need table_mappings correctly formatted
            fixed_mappings = {}
            table_mappings = {}
            
            # Process the mappings the same way csv_parser.py does
            for csv_col, mapping in self.mappings.items():
                if not mapping:
                    continue  # Skip empty mappings
                    
                if "." in mapping:
                    # Handle fully qualified mappings (table.column)
                    table, column = mapping.split(".", 1)
                    if table not in table_mappings:
                        table_mappings[table] = []
                    table_mappings[table].append((csv_col, column))
                    fixed_mappings[csv_col] = column
                else:
                    # Handle direct column mappings
                    fixed_mappings[csv_col] = mapping
                    
                    # Try to find which table this column belongs to
                    found_table = None
                    for table_name, columns in self.db_tables.items():
                        if mapping in columns:
                            found_table = table_name
                            break
                            
                    if found_table:
                        if found_table not in table_mappings:
                            table_mappings[found_table] = []
                        table_mappings[found_table].append((csv_col, mapping))
            
            print("DEBUG: Processed table mappings:")
            for table, table_map in table_mappings.items():
                print(f"  {table}: {table_map}")
            
            # Create extra context similar to csv_parser
            extra_context = {
                "original_data": records,
                "header_mapping": fixed_mappings,
                "table_mappings": table_mappings
            }
            
            # Print first few records for debugging
            print("DEBUG: First record data:")
            if len(records) > 0:
                first_record = records[0]
                for key, value in first_record.items():
                    print(f"  {key}: {value}")
                
            # Print mappings for debugging
            print("DEBUG: Mappings after processing:")
            for original, mapped in self.mappings.items():
                print(f"  {original} -> {mapped}")
                
            # Create "fake" records in exactly the format expected by preprocessor
            # We must have lowercase 'name' and 'website' fields as required by the code
            new_records = []
            skipped_count = 0
            
            for record in records:
                new_record = {}
                
                # Extract name - try multiple variations
                name = None
                for key in ['Name', 'name', 'company', 'Company', 'company_name', 'Company Name']:
                    if key in record and pd.notna(record[key]):
                        name = str(record[key]).strip()
                        break
                        
                # Extract website - try multiple variations
                website = None
                for key in ['Website', 'website', 'url', 'URL', 'web']:
                    if key in record and pd.notna(record[key]):
                        website = str(record[key]).strip()
                        break
                
                # Skip if we don't have both name and website
                if not name or not website:
                    skipped_count += 1
                    continue
                
                # Create the new record with lowercase field names
                new_record["name"] = name
                new_record["website"] = website
                
                # Copy additional fields that might be useful - lowercase them all
                for key, value in record.items():
                    if pd.notna(value) and value:
                        lkey = key.lower()
                        if lkey not in ['name', 'website']:  # Skip fields we've already handled
                            new_record[lkey] = value
                
                new_records.append(new_record)
            
            print(f"DEBUG: Created {len(new_records)} valid records, skipped {skipped_count} due to missing name/website")
                    
            # Now call the preprocessor with our properly formatted records
            print("DEBUG: Calling preprocessor with properly formatted records...")
            if new_records:
                # Try with our cleaned records first
                preprocessor(new_records, batch_id, batch_tag, extra_context=extra_context)
            else:
                # Fall back to original records if no valid records could be created
                print("WARNING: No valid records could be created. Trying with original records...")
                preprocessor(records, batch_id, batch_tag, extra_context=extra_context)
            
            # Complete
            progress.setValue(100)
            
            # Show success message
            QMessageBox.information(
                self, "Import Complete", 
                f"CSV data imported successfully!\n\n"
                f"Batch Tag: {batch_tag}\n"
                f"Batch ID: {batch_id}"
            )
            
            # Close the window
            self.close()
            
        except Exception as e:
            progress.cancel()
            QMessageBox.critical(self, "Import Error", f"Failed to import data: {str(e)}")
            print(f"Error details: {str(e)}")

def run_csv_import_gui():
    """Launch the CSV import GUI"""
    # Get the project root path - must be the parent of src directory!
    script_dir = os.path.dirname(os.path.abspath(__file__))  # src_companies dir
    src_companies_dir = os.path.dirname(script_dir)          # companies dir
    companies_dir = os.path.dirname(src_companies_dir)       # src dir
    project_root = os.path.dirname(companies_dir)            # project root
    
    # Log the path for debugging
    print(f"Setting PROJECT_ROOT to: {project_root}")
    os.environ['PROJECT_ROOT'] = project_root
    
    # Initialize Qt application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show window
    window = CSVImportWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_csv_import_gui()