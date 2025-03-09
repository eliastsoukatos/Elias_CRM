
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_companies_dir = os.path.join(current_dir, 'src_companies')
if src_companies_dir not in sys.path:
    sys.path.insert(0, src_companies_dir)

os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.dirname(current_dir))
os.environ['DB_PATH'] = r"C:\Users\EliasTsoukatos\Documents\software_code\Elias_CRM\databases\database.db"

from src_companies.csv_import_gui import run_csv_import_gui
run_csv_import_gui()
                    