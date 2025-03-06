import os
import sys
import warnings
from src.initializer import initialize_app, start_app_menu

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
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

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
