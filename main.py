import os
import sys
import warnings
from src.initializer import initialize_app, start_app_menu

# Set the PROJECT_ROOT environment variable and hardcode the database path
# This is crucial for all database operations
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["PROJECT_ROOT"] = current_dir

# Add hardcoded database path for Windows
# All database code will first try this path
os.environ["DB_PATH"] = "C:\\Users\\EliasTsoukatos\\Documents\\software_code\\Elias_CRM\\databases\\database.db"

# Suppress PyQt warnings
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false;qt.network.*=false"

# Suppress unwanted output by redirecting stdout/stderr when not in debug mode
debug_mode = os.environ.get("CRM_DEBUG", "0") == "1"
if not debug_mode:
    # Filter out warnings in non-debug mode
    warnings.filterwarnings("ignore")
    
    # Save original stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # Redirect stdout/stderr to null device (suppress output)
    # Use platform-independent method with os.devnull
    null_device = open(os.devnull, 'w')
    sys.stdout = null_device
    sys.stderr = null_device

def main():
    try:
        # First initialize the app (database, migrations, etc.)
        initialize_app()
        
        # Restore stdout/stderr for the menu interaction
        if not debug_mode:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        # Then launch the main menu
        start_app_menu()
    except Exception as e:
        # Ensure stdout/stderr are restored even if there's an exception
        if not debug_mode:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        print(f"Error: {e}")
        if debug_mode:
            raise  # Re-raise the exception in debug mode

if __name__ == "__main__":
    main()
