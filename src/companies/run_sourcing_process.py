import sys
import os

# Set up path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_companies_dir = os.path.join(current_dir, 'src_companies')
if src_companies_dir not in sys.path:
    sys.path.insert(0, src_companies_dir)

# Set up project root path for database access - ensure we use the correct path
project_root = os.path.dirname(os.path.dirname(current_dir))
os.environ['PROJECT_ROOT'] = project_root

# Print the project root in debug mode
if os.environ.get('CRM_DEBUG', '0') == '1':
    print(f"Project root set to: {project_root}")

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

def run_company_process():
    """
    Run the sourcing process for companies, offering options to:
    1. Scrape data from web sources
    2. Import data from CSV files
    3. Query existing data in the database
    """
    while True:
        print("\n" + "=" * 50)
        print(f"{Colors.BOLD}{Colors.BLUE}🔍 COMPANY SOURCING{Colors.END}")
        print("=" * 50)
        print("Please select an option:")
        print(f"{Colors.GREEN}1. Run Scraper{Colors.END}")
        print(f"{Colors.GREEN}2. Import CSV File{Colors.END}")
        print(f"{Colors.GREEN}3. Execute Data Query{Colors.END}")
        print(f"{Colors.RED}0. Back to Companies Menu{Colors.END}")
        option = input(f"{Colors.BOLD}> {Colors.END}").strip()

        if option == '1':
            try:
                from select_scraper import select_scraper
                select_scraper()
            except Exception as e:
                print(f"{Colors.RED}🚨 Error while executing the scraper: {e}{Colors.END}")
        elif option == '2':
            try:
                # Use the new GUI CSV importer
                try:
                    from src_companies.csv_import_gui import run_csv_import_gui
                    run_csv_import_gui()
                except ImportError:
                    # Fall back to command-line version if GUI import fails
                    print(f"{Colors.YELLOW}GUI import failed. Falling back to command-line version.{Colors.END}")
                    from csv_parser import import_csv
                    import_csv()
            except Exception as e:
                print(f"{Colors.RED}🚨 Error while importing CSV: {e}{Colors.END}")
        elif option == '3':
            try:
                from data_query import data_query
                data_query()
            except Exception as e:
                print(f"{Colors.RED}🚨 Error while executing the query: {e}{Colors.END}")
        elif option == '0':
            return
        else:
            print(f"{Colors.RED}❌ Invalid option. Please select a valid option.{Colors.END}")
        
        # Ask if the user wants to perform another operation
        if option in ['1', '2', '3']:
            print(f"\n{Colors.GREEN}Operation completed.{Colors.END}")
            continue_choice = input(f"{Colors.YELLOW}Would you like to perform another operation? (y/n): {Colors.END}").strip().lower()
            if continue_choice != 'y':
                return

if __name__ == '__main__':
    run_company_process()