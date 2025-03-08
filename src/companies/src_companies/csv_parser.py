import os
import pandas as pd
import uuid
import json
import sqlite3
import platform
from sqlite3 import Error
from db_initializer import check_for_database
from preprocessor import preprocessor, clean_url

# Initialize console encoding for Windows
if platform.system() == 'Windows':
    try:
        import colorama
        colorama.init()
    except ImportError:
        pass  # colorama not installed, colors won't work

# ANSI color codes for styled output
class Colors:
    HEADER = '\033[95m' if platform.system() != 'Windows' else ''
    BLUE = '\033[94m' if platform.system() != 'Windows' else ''
    CYAN = '\033[96m' if platform.system() != 'Windows' else ''
    GREEN = '\033[92m' if platform.system() != 'Windows' else ''
    YELLOW = '\033[93m' if platform.system() != 'Windows' else ''
    RED = '\033[91m' if platform.system() != 'Windows' else ''
    BOLD = '\033[1m' if platform.system() != 'Windows' else ''
    UNDERLINE = '\033[4m' if platform.system() != 'Windows' else ''
    END = '\033[0m' if platform.system() != 'Windows' else ''

def get_db_columns():
    """
    Obtiene las columnas de las tablas relevantes de la base de datos.
    
    Returns:
        dict: Un diccionario donde las llaves son los nombres de las tablas y los valores son listas de columnas.
    """
    # Get project root from environment variable if set, otherwise calculate
    project_root = os.environ.get('PROJECT_ROOT')
    
    if not project_root:
        # Fallback to calculating the path - ensure we get to the parent of src
        script_dir = os.path.dirname(os.path.abspath(__file__))  # src_companies dir
        src_companies_dir = os.path.dirname(script_dir)          # companies dir
        companies_dir = os.path.dirname(src_companies_dir)       # src dir
        project_root = os.path.dirname(companies_dir)            # project root
    
    db_path = os.path.join(project_root, 'databases', 'database.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    tables = [
        "companies", "company_locations", "company_phones", "company_technologies",
        "company_industries", "company_identifiers", "company_reviews", "company_projects",
        "company_focus_areas", "company_social_links", "company_verifications", "company_events",
        "company_ratings"
    ]
    db_columns = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        db_columns[table] = [column[1] for column in cursor.fetchall()]
    conn.close()
    return db_columns

def load_previous_mappings(file_path=None):
    """
    Carga los mapeos previos de headers desde el archivo JSON, si existe.
    
    Args:
        file_path (str, optional): Path to the CSV file being imported.
            This is used to look up file-specific mappings in the GUI version.
    
    Returns:
        dict: Un diccionario con los mapeos anteriores o vacío si el archivo no existe.
    """
    # Get project root from environment variable if set, otherwise calculate
    project_root = os.environ.get('PROJECT_ROOT')
    
    if not project_root:
        # Fallback to calculating the path - ensure we get to the parent of src
        script_dir = os.path.dirname(os.path.abspath(__file__))  # src_companies dir
        src_companies_dir = os.path.dirname(script_dir)          # companies dir
        companies_dir = os.path.dirname(src_companies_dir)       # src dir
        project_root = os.path.dirname(companies_dir)            # project root
    
    mappings_path = os.path.join(project_root, 'databases', 'header_mappings.json')
    
    if os.path.exists(mappings_path):
        try:
            with open(mappings_path, 'r') as f:
                mappings = json.load(f)
                
                # If a specific file path is provided, look for file-specific mappings
                if file_path:
                    # Use the basename as a key for the mappings
                    file_name = os.path.basename(file_path)
                    if file_name in mappings:
                        return mappings[file_name]
                
                # Otherwise, return the whole mappings dictionary
                return mappings
        except Exception as e:
            print(f"Error loading mappings: {e}")
            return {}
    else:
        return {}

def save_mappings(mappings, file_path=None):
    """
    Guarda los mapeos actualizados en un archivo JSON para futuras importaciones.
    
    Args:
        mappings (dict): El diccionario de mapeos a guardar.
        file_path (str, optional): Path to the CSV file being imported.
            This is used to store file-specific mappings in the GUI version.
    """
    # Get project root from environment variable if set, otherwise calculate
    project_root = os.environ.get('PROJECT_ROOT')
    
    if not project_root:
        # Fallback to calculating the path - ensure we get to the parent of src
        script_dir = os.path.dirname(os.path.abspath(__file__))  # src_companies dir
        src_companies_dir = os.path.dirname(script_dir)          # companies dir
        companies_dir = os.path.dirname(src_companies_dir)       # src dir
        project_root = os.path.dirname(companies_dir)            # project root
    
    mappings_path = os.path.join(project_root, 'databases', 'header_mappings.json')
    
    # If a file path is provided, store mappings under the file name
    if file_path:
        # Load existing mappings
        existing_mappings = {}
        if os.path.exists(mappings_path):
            try:
                with open(mappings_path, 'r') as f:
                    existing_mappings = json.load(f)
            except:
                existing_mappings = {}
        
        # Update with new mappings
        file_name = os.path.basename(file_path)
        existing_mappings[file_name] = mappings
        
        # Save updated mappings
        with open(mappings_path, 'w') as f:
            json.dump(existing_mappings, f, indent=4)
    else:
        # Traditional mode - just save the mappings as is
        with open(mappings_path, 'w') as f:
            json.dump(mappings, f, indent=4)

def create_new_column(table, column):
    """
    Crea una nueva columna en la tabla especificada.
    Se asume tipo TEXT para la nueva columna.
    
    Args:
        table (str): Nombre de la tabla.
        column (str): Nombre de la nueva columna.
    """
    try:
        # Get project root from environment variable if set, otherwise calculate
        project_root = os.environ.get('PROJECT_ROOT')
        
        if not project_root:
            # Fallback to calculating the path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
        
        db_path = os.path.join(project_root, 'databases', 'database.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        alter_query = f"ALTER TABLE {table} ADD COLUMN {column} TEXT;"
        cursor.execute(alter_query)
        conn.commit()
        conn.close()
        print(f"✅ Se ha creado la nueva columna '{column}' en la tabla '{table}'.")
    except Error as e:
        print(f"🚨 Error al crear la columna nueva: {e}")
        
def create_new_table(table_name):
    """
    Creates a new table with a company_id foreign key.
    
    Args:
        table_name (str): Name of the new table to create.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Get project root from environment variable if set, otherwise calculate
        project_root = os.environ.get('PROJECT_ROOT')
        
        if not project_root:
            # Fallback to calculating the path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
        
        db_path = os.path.join(project_root, 'databases', 'database.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if cursor.fetchone():
            print(f"⚠️ Table '{table_name}' already exists.")
            conn.close()
            return True
            
        # Create new table with company_id as foreign key
        create_query = f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );
        """
        cursor.execute(create_query)
        conn.commit()
        conn.close()
        print(f"✅ Successfully created new table '{table_name}' with company_id foreign key.")
        return True
    except Error as e:
        print(f"🚨 Error creating new table: {e}")
        return False

def import_csv():
    """
    import_csv()

    - Solicita la ruta o nombre del archivo CSV a importar.
    - Verifica y crea la estructura necesaria de la base de datos usando check_for_database() de db_initializer.py.
    - Muestra todas las tablas disponibles para el mapeo de headers.
    - Mapea los headers del CSV a las columnas de la base de datos:
      * Presenta mapeos anteriores (si existen) y ofrece la opción de aplicarlos automáticamente.
      * Permite ajustes manuales para cada columna, ofreciendo las opciones de:
            - Conservar el mapeo anterior.
            - Omitir la columna (escribir 'skip').
            - Crear una nueva columna (escribir 'new') y seleccionar en qué tabla.
      * Guarda los mapeos actualizados para futuras importaciones.
    - Solicita un batch_tag único y genera un batch_id.
    - Convierte los datos del CSV en formato JSON.
    - Llama a preprocessor() de preprocessor.py para procesar los datos.
    
    Asegura la consistencia de los datos, la reutilización de mapeos de headers y un manejo robusto de errores.
    """
    try:
        # 1. Solicitar el archivo CSV
        file_path = input("Please enter the path or name of the CSV file you want to import: ").strip()
        
        # Get the absolute path to the CRM root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get project root from environment variable if set, otherwise calculate
        crm_root = os.environ.get('PROJECT_ROOT')
        if not crm_root:
            # Navigate up to the CRM root (src_companies -> companies -> src -> CRM)
            crm_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        
        # Try with different path combinations
        possible_paths = [
            file_path,                        # As provided
            os.path.join(os.getcwd(), file_path),  # From current working directory
            os.path.join(crm_root, file_path),     # From CRM root
            os.path.abspath(file_path)        # As absolute path
        ]
        
        # Find the first path that exists
        for path in possible_paths:
            if os.path.exists(path) and path.lower().endswith('.csv'):
                file_path = path
                print(f"{Colors.GREEN}✅ Found CSV file at:{Colors.END} {file_path}")
                break
        else:
            # This executes if the for loop completes without a break
            print(f"{Colors.RED}❌ Invalid file. Please ensure the CSV file exists and has a '.csv' extension.{Colors.END}")
            print(f"{Colors.YELLOW}Searched in the following locations:{Colors.END}")
            for path in possible_paths:
                print(f"  - {path}")
            return

        # 2. Leer el archivo CSV con pandas
        dataframe = pd.read_csv(file_path)
        print(f"{Colors.GREEN}✅ CSV file loaded successfully. Proceeding to database verification...{Colors.END}")

        # 3. Verificar la base de datos
        if not check_for_database():
            print(f"{Colors.RED}❌ Database verification failed.{Colors.END}")
            return
        print(f"{Colors.GREEN}✅ Database verified successfully. Proceeding to header mapping...{Colors.END}")

        # 4. Mostrar tablas disponibles para el mapeo
        db_columns = get_db_columns()
        print(f"\n{Colors.BOLD}{Colors.BLUE}DATABASE TABLES AND COLUMNS{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
        for table, columns in db_columns.items():
            print(f"{Colors.YELLOW}➤ {table}:{Colors.END} {columns}")

        # 5. Imprimir las instrucciones de mapeo (solo una vez)
        print(f"\n{Colors.BOLD}{Colors.BLUE}MAPPING INSTRUCTIONS{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
        print(f"  {Colors.GREEN}➤ Type a {Colors.BOLD}column name{Colors.END}{Colors.GREEN} from the database to map to it{Colors.END}")
        print(f"  {Colors.YELLOW}➤ Type {Colors.BOLD}'skip'{Colors.END}{Colors.YELLOW} to ignore this column{Colors.END}")
        print(f"  {Colors.BLUE}➤ Type {Colors.BOLD}'new'{Colors.END}{Colors.BLUE} to create a new column in a table{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}\n")

        # 6. Cargar mapeos anteriores
        previous_mappings = load_previous_mappings()

        # 7. Mapeo de headers del CSV a columnas de la base de datos
        csv_headers = list(dataframe.columns)
        header_mapping = {}

        # Si hay mapeos previos y el CSV coincide completamente con ellos, ofrecer aplicar todos automáticamente.
        if previous_mappings and set(previous_mappings.keys()) == set(csv_headers):
            print(f"\n{Colors.BOLD}{Colors.YELLOW}⚡ Previous header mapping found for this CSV.{Colors.END}")
            use_prev = input(f"Do you want to apply the previous mapping to all columns? ({Colors.GREEN}yes{Colors.END}/{Colors.RED}no{Colors.END}): ").strip().lower()
            if use_prev == "yes":
                header_mapping = previous_mappings
                print(f"{Colors.GREEN}✅ Applied previous mappings to all columns.{Colors.END}")
            else:
                # Proceder a mapeo manual por cada columna
                for header in csv_headers:
                    if header in previous_mappings:
                        print(f"\n{Colors.CYAN}Column:{Colors.END} {Colors.BOLD}{header}{Colors.END}")
                        print(f"{Colors.YELLOW}Previous mapping:{Colors.END} '{Colors.BOLD}{previous_mappings[header]}{Colors.END}'")
                        use_mapping = input(f"Keep this mapping? ({Colors.GREEN}yes{Colors.END}/{Colors.RED}no{Colors.END}): ").strip().lower()
                        if use_mapping == "yes":
                            header_mapping[header] = previous_mappings[header]
                            print(f"{Colors.GREEN}✓ Kept previous mapping{Colors.END}")
                            continue
                    valid_mapping = False
                    while not valid_mapping:
                        print(f"\n{Colors.CYAN}Column:{Colors.END} {Colors.BOLD}{header}{Colors.END}")
                        user_mapping = input(f"Enter your choice: ").strip()
                        if user_mapping.lower() == "skip":
                            header_mapping[header] = None
                            print(f"{Colors.YELLOW}⏩ Column '{header}' will be skipped{Colors.END}")
                            valid_mapping = True
                        elif user_mapping.lower() == "new":
                            print(f"\n{Colors.BOLD}{Colors.CYAN}CREATE NEW FIELD{Colors.END}")
                            create_option = input(f"Do you want to create:\n{Colors.GREEN}(1) A new column in existing table{Colors.END}, or\n{Colors.BLUE}(2) A new table and column{Colors.END}\nEnter 1 or 2: ").strip()
                            
                            if create_option == "1":
                                # Create new column in existing table
                                print(f"\n{Colors.BOLD}{Colors.YELLOW}Available tables:{Colors.END}")
                                for i, table in enumerate(sorted(db_columns.keys()), 1):
                                    print(f"  {Colors.CYAN}{i}.{Colors.END} {table}")
                                    
                                chosen_table = input(f"\n{Colors.BOLD}Enter the table name:{Colors.END} ").strip()
                                if chosen_table in db_columns:
                                    new_col = input(f"Enter the new column name for CSV header '{Colors.BOLD}{header}{Colors.END}' (default: use CSV header name): ").strip()
                                    if not new_col:
                                        new_col = header
                                    create_new_column(chosen_table, new_col)
                                    db_columns[chosen_table].append(new_col)
                                    header_mapping[header] = new_col
                                    print(f"{Colors.GREEN}✅ Created new column '{new_col}' in table '{chosen_table}'{Colors.END}")
                                    valid_mapping = True
                                else:
                                    print(f"{Colors.RED}❌ Invalid table name. Please choose one of the listed tables.{Colors.END}")
                            elif create_option == "2":
                                # Create new table and column
                                new_table = input(f"{Colors.BOLD}Enter the name for the new table (use snake_case, e.g. company_certifications):{Colors.END} ").strip()
                                if not new_table:
                                    print(f"{Colors.RED}❌ Table name cannot be empty.{Colors.END}")
                                    continue
                                    
                                # Validate table name format
                                if not all(c.islower() or c.isdigit() or c == '_' for c in new_table):
                                    print(f"{Colors.YELLOW}⚠️ Table name should be in snake_case. Converting to lowercase with underscores.{Colors.END}")
                                    new_table = new_table.lower().replace(' ', '_')
                                    
                                # Create the new table
                                if create_new_table(new_table):
                                    # Add the new table to db_columns
                                    db_columns[new_table] = ["id", "company_id"]
                                    
                                    # Now create a column in the new table
                                    new_col = input(f"Enter the new column name for CSV header '{Colors.BOLD}{header}{Colors.END}' (default: use CSV header name): ").strip()
                                    if not new_col:
                                        new_col = header
                                        
                                    # Validate column name format
                                    if not all(c.islower() or c.isdigit() or c == '_' for c in new_col):
                                        print(f"{Colors.YELLOW}⚠️ Column name should be in snake_case. Converting to lowercase with underscores.{Colors.END}")
                                        new_col = new_col.lower().replace(' ', '_')
                                        
                                    create_new_column(new_table, new_col)
                                    db_columns[new_table].append(new_col)
                                    
                                    # Map the CSV header to this new column
                                    header_mapping[header] = new_col
                                    
                                    # Create a special marker to indicate this is for a new table
                                    header_mapping[f"__table__{header}"] = new_table
                                    
                                    print(f"{Colors.GREEN}✅ Created new table '{new_table}' with column '{new_col}'{Colors.END}")
                                    valid_mapping = True
                                else:
                                    print(f"{Colors.RED}❌ Failed to create new table. Please try again.{Colors.END}")
                            else:
                                print(f"{Colors.RED}❌ Invalid option. Please enter 1 or 2.{Colors.END}")                                
                            
                        else:
                            if any(user_mapping in cols for cols in db_columns.values()):
                                header_mapping[header] = user_mapping
                                # Find which table this column belongs to
                                for table, columns in db_columns.items():
                                    if user_mapping in columns:
                                        table_name = table
                                        break
                                print(f"{Colors.GREEN}✅ Mapped to '{table_name}.{user_mapping}'{Colors.END}")
                                valid_mapping = True
                            else:
                                print(f"{Colors.RED}❌ Invalid mapping. Please enter a valid database column, or choose 'skip' or 'new'.{Colors.END}")
        else:
            # No hay mapeos previos completos o no coinciden, proceder mapeo manual para cada header
            for header in csv_headers:
                if header in previous_mappings:
                    use_mapping = input(f"Previous mapping for '{header}' is '{previous_mappings[header]}'. Do you want to keep it? (yes/no): ").strip().lower()
                    if use_mapping == "yes":
                        header_mapping[header] = previous_mappings[header]
                        continue
                valid_mapping = False
                while not valid_mapping:
                    user_mapping = input(f"Enter your choice for '{header}': ").strip()
                    if user_mapping.lower() == "skip":
                        header_mapping[header] = None
                        valid_mapping = True
                    elif user_mapping.lower() == "new":
                        create_option = input("Do you want to create: (1) A new column in existing table, or (2) A new table and column? Enter 1 or 2: ").strip()
                        
                        if create_option == "1":
                            # Create new column in existing table
                            chosen_table = input("Enter the table name where you want to create the new column: ").strip()
                            if chosen_table in db_columns:
                                new_col = input(f"Enter the new column name for CSV header '{header}' (default: use CSV header name): ").strip()
                                if not new_col:
                                    new_col = header
                                create_new_column(chosen_table, new_col)
                                db_columns[chosen_table].append(new_col)
                                header_mapping[header] = new_col
                                valid_mapping = True
                            else:
                                print("❌ Invalid table name. Please choose one of the listed tables.")
                        elif create_option == "2":
                            # Create new table and column
                            new_table = input("Enter the name for the new table (use snake_case, e.g. company_certifications): ").strip()
                            if not new_table:
                                print("❌ Table name cannot be empty.")
                                continue
                                
                            # Validate table name format (lowercase, underscore separated)
                            if not all(c.islower() or c.isdigit() or c == '_' for c in new_table):
                                print("❌ Table name should be in snake_case (lowercase with underscores).")
                                continue
                                
                            # Create the new table
                            if create_new_table(new_table):
                                # Add the new table to db_columns
                                db_columns[new_table] = ["id", "company_id"]
                                
                                # Now create a column in the new table
                                new_col = input(f"Enter the new column name for CSV header '{header}' (default: use CSV header name): ").strip()
                                if not new_col:
                                    new_col = header
                                    
                                # Validate column name format
                                if not all(c.islower() or c.isdigit() or c == '_' for c in new_col):
                                    print("⚠️ Column name should be in snake_case. Converting to lowercase with underscores.")
                                    new_col = new_col.lower().replace(' ', '_')
                                    
                                create_new_column(new_table, new_col)
                                db_columns[new_table].append(new_col)
                                
                                # Map the CSV header to this new column
                                header_mapping[header] = new_col
                                
                                # Create a special marker to indicate this is for a new table
                                header_mapping[f"__table__{header}"] = new_table
                                
                                valid_mapping = True
                            else:
                                print("❌ Failed to create new table. Please try again.")
                        else:
                            print("❌ Invalid option. Please enter 1 or 2.")
                    else:
                        if any(user_mapping in cols for cols in db_columns.values()):
                            header_mapping[header] = user_mapping
                            valid_mapping = True
                        else:
                            print("❌ Invalid mapping. Please enter a valid database column, or choose 'skip' or 'new'.")

        # Guardar los mapeos actualizados para futuras importaciones
        save_mappings(header_mapping)
        print(f"{Colors.GREEN}✅ Header mappings have been saved for future imports.{Colors.END}")

        # 8. Solicitar ingreso del batch_tag
        print(f"\n{Colors.BOLD}{Colors.BLUE}BATCH INFORMATION{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
        valid_tag = False
        while not valid_tag:
            batch_tag = input(f"{Colors.BOLD}Please enter a unique batch tag for this data load:{Colors.END} ").strip()
            # Validar que el batch_tag no contenga caracteres especiales (solo letras, números, espacios, guiones y guiones bajos)
            if batch_tag and all(c.isalnum() or c in " -_" for c in batch_tag):
                valid_tag = True
            else:
                print(f"{Colors.RED}❌ Invalid batch tag. Please avoid special characters.{Colors.END}")
        
        # 9. Generar automáticamente un batch_id único
        batch_id = str(uuid.uuid4())
        print(f"{Colors.GREEN}🆔 Generated batch ID:{Colors.END} {Colors.BOLD}{batch_id}{Colors.END}")

        # 10. Transformar los datos a JSON usando los mapeos para renombrar las columnas
        # Eliminar columnas que se han decidido omitir
        columns_to_drop = [header for header, mapping in header_mapping.items() if mapping is None]
        if columns_to_drop:
            dataframe.drop(columns=columns_to_drop, inplace=True)
            print(f"ℹ️ The following columns were skipped: {columns_to_drop}")
            
        # Track which columns get mapped to which table
        table_mappings = {}
        for table in db_columns.keys():
            table_mappings[table] = []
            
        # Process new table markers first
        new_tables = {}
        for header, mapped_name in list(header_mapping.items()):
            if header.startswith("__table__"):
                original_header = header.replace("__table__", "")
                new_tables[original_header] = mapped_name
                # Remove the marker from the header_mapping
                del header_mapping[header]
                
        # Find out which table each mapped column belongs to
        for header, mapped_name in header_mapping.items():
            if mapped_name is None:
                continue
                
            # Check if this header is for a new table
            if header in new_tables:
                table_name = new_tables[header]
                # Create entry for new table if it doesn't exist
                if table_name not in table_mappings:
                    table_mappings[table_name] = []
                table_mappings[table_name].append((header, mapped_name))
                continue
                
            # Otherwise look in existing tables
            for table, columns in db_columns.items():
                if mapped_name in columns:
                    table_mappings[table].append((header, mapped_name))
                    
        # Print a summary of the mappings
        print(f"\n{Colors.BOLD}{Colors.BLUE}MAPPING SUMMARY{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
        for table, mappings in table_mappings.items():
            if mappings:
                print(f"{Colors.YELLOW}➤ {table}:{Colors.END}")
                for header, column in mappings:
                    print(f"  {Colors.GREEN}• {header} → {column}{Colors.END}")
        
        # Standardize website URLs in the dataframe
        print(f"\n{Colors.BOLD}{Colors.BLUE}URL STANDARDIZATION{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
        
        # Check for both original 'website' column and mapped 'website' columns
        website_columns = []
        
        # Check for direct 'website' column
        if 'website' in dataframe.columns:
            website_columns.append('website')
            
        # Check if any column is mapped to 'website'
        for csv_header, db_column in header_mapping.items():
            if db_column == 'website' and csv_header in dataframe.columns:
                website_columns.append(csv_header)
                
        # Process all website columns - keep track of which columns were processed
        processed_columns = set()
        if website_columns:
            print(f"{Colors.CYAN}🌐 Standardizing website URLs to format: https://domain.com{Colors.END}")
            for col in website_columns:
                # Skip if already processed (avoid processing the same column twice)
                if col in processed_columns:
                    continue
                    
                print(f"  {Colors.GREEN}➤ Processing '{col}' column{Colors.END}")
                dataframe[col] = dataframe[col].apply(lambda url: clean_url(url) if pd.notna(url) and url else "")
                processed_columns.add(col)
        
        # Prepare the dataframe first, before renaming columns
        # This preserves the data before we rename columns
        data_dict = dataframe.to_dict(orient="records")
                    
        # Rename columns, checking for duplicates
        valid_mapping = {header: mapping for header, mapping in header_mapping.items() if mapping is not None}
        
        # Check for duplicate target column names
        target_columns = list(valid_mapping.values())
        duplicate_targets = [col for col in set(target_columns) if target_columns.count(col) > 1]
        
        if duplicate_targets:
            print("⚠️ Warning: Found duplicate target column names after mapping:")
            for dup in duplicate_targets:
                headers = [h for h, m in valid_mapping.items() if m == dup]
                print(f"  - '{dup}' used for CSV headers: {headers}")
                
            # Fix duplicates by adding a suffix
            for i, header in enumerate([h for h, m in valid_mapping.items() if m in duplicate_targets]):
                source_headers = [h for h, m in valid_mapping.items() if m == valid_mapping[header]]
                idx = source_headers.index(header)
                if idx > 0:  # Skip the first occurrence
                    valid_mapping[header] = f"{valid_mapping[header]}_{idx + 1}"
                    print(f"  - Renamed mapping for '{header}' to '{valid_mapping[header]}'")
                    
        # Rename columns with the corrected mapping
        dataframe.rename(columns=valid_mapping, inplace=True)
        
        # Double-check for duplicate columns
        if len(dataframe.columns) != len(set(dataframe.columns)):
            # Get list of column names
            cols = list(dataframe.columns)
            
            # Find all duplicate column names
            seen = {}
            for i, col in enumerate(cols):
                if col in seen:
                    seen[col].append(i)
                else:
                    seen[col] = [i]
            
            # Get only the duplicates
            duplicates = {col: indices for col, indices in seen.items() if len(indices) > 1}
            
            if duplicates:
                print("⚠️ Found duplicate columns after renaming. Fixing by adding suffixes:")
                renamed_columns = cols.copy()
                
                # Rename duplicates
                for col, indices in duplicates.items():
                    # Skip the first occurrence
                    for i, idx in enumerate(indices[1:], 1):
                        new_name = f"{col}_{i+1}"
                        print(f"  - Renaming duplicate column at position {idx} from '{col}' to '{new_name}'")
                        renamed_columns[idx] = new_name
                
                # Create new dataframe with renamed columns
                dataframe.columns = renamed_columns
        
        # Convert to JSON
        data_json = dataframe.to_json(orient="records")
        print(f"{Colors.GREEN}✅ Data successfully mapped and converted to JSON format.{Colors.END}")

        # 11. Llamar al preprocesador con los datos transformados
        print(f"\n{Colors.BOLD}{Colors.BLUE}PROCESSING DATA{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
        
        # Include both the renamed data and the original data with mapping information
        # This ensures newly created columns receive their data
        extra_context = {
            "table_mappings": table_mappings,
            "original_data": data_dict,
            "header_mapping": header_mapping
        }
        
        print(f"{Colors.YELLOW}Starting data processing...{Colors.END}")
        preprocessor(data_json, batch_id, batch_tag, extra_context=extra_context)
        print(f"{Colors.GREEN}🚀 Data preprocessing completed with batch ID: {batch_id}{Colors.END}")

    except Exception as e:
        print(f"🚨 An error occurred during the CSV import process: {e}")

if __name__ == "__main__":
    import_csv()