import re
import uuid
import sqlite3
import json
import os
import platform
from datetime import datetime
from urllib.parse import urlparse
from db_writer import db_writer

def clean_url(url):
    """
    Standardizes URL format to https://domain.com (no www prefix)
    
    Args:
        url: The URL to clean/standardize
        
    Returns:
        Standardized URL in the format https://domain.com
    """
    if not url:
        return ""
    
    # Handle URLs without scheme (http/https)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed = urlparse(url)
    
    # Extract domain from query parameters if applicable
    if 'provider_website=' in url:
        match = re.search(r'provider_website=([\w\.-]+)', url)
        if match:
            domain = match.group(1)
            return f"https://{domain}"
    
    # Get domain and path
    domain = parsed.netloc
    path = parsed.path
    
    # If netloc is empty, the domain might be in the path
    if not domain and path:
        # Try to extract from path
        parts = path.strip('/').split('/', 1)
        domain = parts[0]
        path = '/' + parts[1] if len(parts) > 1 else ''
    
    # Remove www prefix
    if domain.startswith('www.'):
        domain = domain[4:]
        
    # Handle empty domain
    if not domain:
        return ""
    
    # Include querystring and fragments if present
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    
    # If it's just a domain without a path, return just the domain
    if not path and not query and not fragment:
        return f"https://{domain}"
    
    # Otherwise return the full URL (minus www)
    return f"https://{domain}{path}{query}{fragment}"

def extract_domain(url):
    """
    Extracts the domain from a URL, removing www. prefix.
    
    Args:
        url: The URL to extract the domain from
        
    Returns:
        The domain without www. prefix
    """
    if not url:
        return ""
        
    # Handle URLs without scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    
    # If netloc is empty but path isn't, domain might be in path
    if not domain and parsed.path:
        parts = parsed.path.strip('/').split('/', 1)
        domain = parts[0]
    
    # Remove www. prefix if present
    if domain.startswith("www."):
        domain = domain[4:]
        
    return domain

def company_exists(domain):
    try:
        # Connect to the database at project root
        import os
        project_root = os.environ.get('PROJECT_ROOT')
        if not project_root:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
        db_path = os.path.join(project_root, 'databases', 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT company_id FROM companies WHERE domain = ?", (domain,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error checking company existence: {e}")
        return None

def standardize_string(s):
    if isinstance(s, str):
        return ' '.join(s.lower().strip().split())
    return s

def standardize_date(date_str):
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None

def standardize_number(num):
    try:
        clean_num = re.sub(r'[^\d\.-]', '', str(num))
        if '.' in clean_num:
            return float(clean_num)
        else:
            return int(clean_num)
    except Exception:
        return None

def parse_list_field(field):
    if isinstance(field, list):
        return field
    if isinstance(field, str):
        return [x.strip() for x in field.split(',') if x.strip()]
    return []

def extract_social_media_links(record):
    social_links = {}
    
    # Check for various social media fields that might be in the CSV
    linkedin_url = record.get("linkedin_url", "")
    facebook_url = record.get("facebook_url", "")
    twitter_url = record.get("twitter_url", "")
    instagram_url = record.get("instagram_url", "")
    
    # Only include fields that have values
    if linkedin_url or facebook_url or twitter_url or instagram_url:
        social_links = {
            "linkedin": linkedin_url if linkedin_url else None,
            "facebook": facebook_url if facebook_url else None,
            "twitter": twitter_url if twitter_url else None,
            "instagram": instagram_url if instagram_url else None
        }
        
        # Only return a record if at least one social media link exists
        if any(social_links.values()):
            return [social_links]
    
    return []

def parse_addresses(address_str, hq_location):
    addresses = []
    if not address_str:
        return addresses
    # Si se detecta el uso de corchetes, se asume que hay múltiples direcciones
    if '[' in address_str:
        cleaned = address_str.strip()
        if cleaned.startswith('[') and cleaned.endswith(']'):
            cleaned = cleaned[1:-1]
        addr_list = cleaned.split("], [")
        for addr in addr_list:
            parts = [p.strip() for p in addr.split(",")]
            country = state = city = street = zip_code = ""
            if len(parts) >= 3:
                country = parts[0]
                state = parts[1]
                city = parts[2]
                if len(parts) >= 4:
                    street = parts[3]
                if len(parts) >= 5:
                    zip_code = parts[4]
            office_type = "headquarters" if hq_location and hq_location.strip() and hq_location.strip() in addr else "sucursal"
            # Si todos los campos clave están vacíos, se omite el registro
            if not any([street, city, state, country, zip_code]):
                continue
            addresses.append({
                "street": street,
                "city": city,
                "state": state,
                "country": country,
                "postal_code": zip_code,
                "office_type": office_type
            })
    else:
        # Caso de una única dirección
        parts = [p.strip() for p in address_str.split(",")]
        country = state = city = street = zip_code = ""
        if len(parts) >= 3:
            country = parts[0]
            state = parts[1]
            city = parts[2]
            if len(parts) >= 4:
                street = parts[3]
            if len(parts) >= 5:
                zip_code = parts[4]
        office_type = "headquarters" if hq_location and hq_location.strip() and hq_location.strip() in address_str else "sucursal"
        # Si todos los campos clave están vacíos, se omite el registro
        if any([street, city, state, country, zip_code]):
            addresses.append({
                "street": street,
                "city": city,
                "state": state,
                "country": country,
                "postal_code": zip_code,
                "office_type": office_type
            })
    return addresses

try:
    from clutch_mapper import map_all as clutch_map_all
except ImportError:
    clutch_map_all = None

def preprocessor(data, batch_id, batch_tag, extra_context=None):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        elif isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            print("🚨 Unsupported data format.")
            return
            
        # Process original data with mapping information if provided
        has_new_columns = False
        if extra_context and 'original_data' in extra_context and 'header_mapping' in extra_context:
            has_new_columns = True

        for record in data:
            # Si el registro proviene de Clutch se ignora la sección de dirección
            if isinstance(record, dict) and "summary" in record and clutch_map_all:
                mapped = clutch_map_all(record, batch_id, batch_tag)
                mapped["company_locations"] = []  # Ignoramos direcciones de Clutch
                company_name = mapped.get("companies", {}).get("name", "").strip()  # conserva mayúsculas
                website = mapped.get("companies", {}).get("website", "")
            else:
                company_name = record.get("name", "").strip()  # conserva mayúsculas
                website = record.get("website", "")
                website = clean_url(website) if website else ""
                domain = extract_domain(website) if website else ""
                mapped = {
                    "companies": {
                        "company_id": str(uuid.uuid4()),
                        "name": company_name,
                        "website": website,
                        "domain": domain,
                        "headcount": standardize_number(record.get("headcount", None)),
                        "headcount_range": None,
                        "revenue": standardize_number(record.get("revenue", None)),
                        "founded": standardize_date(record.get("founding_date", None)),
                        "company_type": record.get("company_type", ""),
                        "description": record.get("company description", "")
                    },
                    "company_locations": [],  
                    "company_phones": [],
                    "company_technologies": [{"technology_name": tech} for tech in parse_list_field(record.get("technology_name", []))],
                    "company_industries": [{"industry_name": ind} for ind in parse_list_field(record.get("industry_name", []))],
                    "company_identifiers": [],
                    "company_reviews": [],
                    "company_portfolio": [],
                    "company_focus_areas": [],
                    "company_social_links": extract_social_media_links(record),
                    "company_verifications": [],
                    "company_ratings": []
                }
                
                identifiers = {}
                if record.get("sic_code"):
                    identifiers["sic_code"] = record.get("sic_code")
                if record.get("isic_code"):
                    identifiers["isic_code"] = record.get("isic_code")
                if record.get("naics_code"):
                    identifiers["naics_code"] = record.get("naics_code")
                if identifiers:
                    mapped["company_identifiers"] = [identifiers]
                
                if record.get("portfolio"):
                    portfolio_items = []
                    for item in record["portfolio"]:
                        portfolio_items.append({
                            "portfolio_id": item.get("id") or str(uuid.uuid4()),
                            "portfolio_name": item.get("title", ""),
                            "portfolio_category": ", ".join(item.get("services", [])),
                            "portfolio_size": item.get("projectSize", ""),
                            "portfolio_description": item.get("description", "")
                        })
                    mapped["company_portfolio"] = portfolio_items

                # Process phone numbers - split multiple phone numbers
                if record.get("phone_number"):
                    phone_number = record.get("phone_number")
                    # Check if the phone number contains multiple numbers
                    if ',' in phone_number:
                        # Split by comma and strip whitespace
                        phone_numbers = [p.strip() for p in phone_number.split(',') if p.strip()]
                        for phone in phone_numbers:
                            mapped["company_phones"].append({"phone_number": phone})
                    else:
                        mapped["company_phones"].append({"phone_number": phone_number.strip()})
                
                # Process verifications - only add if there's actual data
                if record.get("verification_status") or record.get("verification_source"):
                    verification = {
                        "verification_id": str(uuid.uuid4()),
                        "verification_status": record.get("verification_status", ""),
                        "source": record.get("verification_source", ""),
                        "last_updated": standardize_date(record.get("verification_date", None))
                    }
                    mapped["company_verifications"] = [verification]
                
                # Process ratings - only add if there's actual data
                overall_rating = standardize_number(record.get("overall_rating", None))
                review_count = standardize_number(record.get("review_count", None))
                if overall_rating is not None or review_count is not None:
                    rating = {
                        "rating_id": str(uuid.uuid4()),
                        "overall_rating": overall_rating,
                        "review_count": review_count
                    }
                    mapped["company_ratings"] = [rating]
                
                # Procesar la dirección usando la función parse_addresses:
                mapped["company_locations"] = parse_addresses(record.get("locations", ""), record.get("hq_location", ""))
                
                # Procesar eventos a partir de columnas con nombres que empiecen con "company_events_raw_"
                company_events = []
                for key, value in record.items():
                    if key.startswith("company_events_raw_") and value:
                        company_events.append({
                            "event_id": str(uuid.uuid4()),
                            "event_data": value
                        })
                mapped["company_events"] = company_events

            if not company_name or not website:
                print(f"⚠️ Skipped company due to missing mandatory fields: {company_name}")
                continue

            domain = extract_domain(website)
            existing_company_id = company_exists(domain)
            if existing_company_id:
                mapped["companies"]["company_id"] = existing_company_id
                print(f"🔄 Existing company found. Updating fields for: {company_name}")
            else:
                print(f"✨ New company detected. Preparing data for insertion: {company_name}")

            # Process new columns from the CSV if they exist
            if has_new_columns and not (isinstance(record, dict) and "summary" in record):
                original_idx = data.index(record)
                original_data = extra_context["original_data"][original_idx]
                table_mappings = extra_context["table_mappings"]
                header_mapping = extra_context["header_mapping"]
                
                print(f"📊 Processing new columns for {company_name}...")
                
                # Process custom columns for each table
                for table, mappings in table_mappings.items():
                    if not mappings:
                        continue  # Skip tables with no mappings
                        
                    # Check if this table is one of the default ones
                    if table not in mapped and table != "companies":
                        mapped[table] = []
                    
                    # For standard tables that expect a list of dictionaries
                    if table not in ["companies", "batch_tag", "batch_id", "source"]:
                        # Initialize if needed
                        if not mapped[table]:
                            mapped[table] = []
                            
                        # Determine if this is a dynamically created table
                        is_new_table = table not in ["companies", "company_locations", "company_phones", 
                                                   "company_technologies", "company_industries", 
                                                   "company_identifiers", "company_reviews", 
                                                   "company_portfolio", "company_focus_areas", 
                                                   "company_social_links", "company_verifications", 
                                                   "company_events", "company_ratings"]
                        
                        # Special handling for dynamically created tables - create a new row for each field
                        if is_new_table:
                            company_id = mapped["companies"]["company_id"]
                            print(f"  ➕ Processing custom table {table} with {len(mappings)} fields")
                            
                            # Get column names for this table (excluding id and company_id)
                            # Get project root from environment variable if set, otherwise calculate
                            import os
                            project_root = os.environ.get('PROJECT_ROOT')
                            if not project_root:
                                # Fallback to calculating the path - ensure we get to the parent of src
                                script_dir = os.path.dirname(os.path.abspath(__file__))  # src_companies dir
                                src_companies_dir = os.path.dirname(script_dir)          # companies dir
                                companies_dir = os.path.dirname(src_companies_dir)       # src dir
                                project_root = os.path.dirname(companies_dir)            # project root
                            
                            db_path = os.path.join(project_root, 'databases', 'database.db')
                            cursor = sqlite3.connect(db_path).cursor()
                            cursor.execute(f"PRAGMA table_info({table});")
                            table_columns = [column[1] for column in cursor.fetchall()]
                            cursor.close()
                            
                            # Find out how many fields this table has (excluding id and company_id)
                            data_fields = [col for col in table_columns if col not in ["id", "company_id"]]
                            
                            # If there's only one data field, put all values in separate rows
                            if len(data_fields) == 1:
                                field_name = data_fields[0]
                                # Create a new row for each CSV column mapped to this table
                                for csv_header, db_column in mappings:
                                    if csv_header in original_data and original_data[csv_header]:
                                        value = original_data[csv_header]
                                        # Create a new row for this value
                                        new_row = {
                                            "company_id": company_id,
                                            field_name: value
                                        }
                                        mapped[table].append(new_row)
                                        print(f"  ➕ Added new row in {table} with {field_name}='{value}' from CSV column '{csv_header}'")
                            else:
                                # If table has multiple fields, use first record approach
                                if not mapped[table]:
                                    mapped[table].append({"company_id": company_id})
                                
                                # Populate the fields in the first record
                                for csv_header, db_column in mappings:
                                    if csv_header in original_data:
                                        value = original_data[csv_header]
                                        mapped[table][0][db_column] = value
                                        print(f"  ➕ Added value '{value}' to {table}.{db_column} from CSV column '{csv_header}'")
                        else:
                            # Standard tables (not custom) - use original behavior
                            if not mapped[table]:
                                mapped[table] = [{}]
                                
                            # For standard tables, ensure we add any required fields
                            if "company_id" not in mapped[table][0]:
                                mapped[table][0]["company_id"] = mapped["companies"]["company_id"]
                                
                            # Populate the new columns with their values
                            for csv_header, db_column in mappings:
                                if csv_header in original_data:
                                    value = original_data[csv_header]
                                    mapped[table][0][db_column] = value
                                    print(f"  ➕ Added value '{value}' to {table}.{db_column} from CSV column '{csv_header}'.")
                    
                    # For the companies table (which is a dict, not a list)
                    elif table == "companies" and mappings:
                        for csv_header, db_column in mappings:
                            if csv_header in original_data:
                                value = original_data[csv_header]
                                mapped["companies"][db_column] = value
                                print(f"  ➕ Added value '{value}' to {table}.{db_column} from CSV column '{csv_header}'.")

            # Agregar la información del batch a nivel superior (no en companies)
            mapped["batch_tag"] = batch_tag
            mapped["batch_id"] = batch_id

            # Asignar el source según el origen de los datos
            if isinstance(record, dict) and "summary" in record and clutch_map_all:
                mapped["source"] = "clutch"
            else:
                mapped["source"] = "csv import"

            db_writer(mapped)
            print(f"🚀 Data written to the database for company: {company_name}")

    except Exception as e:
        print(f"🚨 An error occurred during preprocessing: {e}")

if __name__ == "__main__":
    sample_csv_data = [
        {
            "name": "Example Company",
            "website": "https://www.example.com",
            "headcount": "100",
            "revenue": "$1,000,000",
            "founding_date": "2020-01-15",
            "technology_name": "Python, Django",
            "industry_name": "Technology, Finance",
            "sic_code": "1234",
            "isic_code": "5678",
            "naics_code": "91011",
            "company_type": "startup",
            "company description": "An example company description.",
            "locations": "[United States, Texas, Austin, 5910 Courtyard Dr, 78731]",
            "hq_location": "5910 Courtyard Dr",
            "portfolio": [
                {
                    "id": "111",
                    "title": "Project Alpha",
                    "services": ["Web Development"],
                    "projectSize": "Large",
                    "description": "A flagship project."
                }
            ],
            "linkedin_url": "https://www.linkedin.com/company/example",
            "facebook_url": "https://www.facebook.com/example",
            "twitter_url": "https://twitter.com/example",
            "instagram_url": "https://www.instagram.com/example",
            "phone_number": "123-456-7890",
            "Company Event 1": "Event description one",
            "Company Event 2": "Event description two",
            "Company Event 3": "",
            "Company Event 4": "",
            "Company Event 5": "",
            "Company Event 6": "",
            "Company Event 7": "",
            "Company Event 8": "",
            "Company Event 9": "",
            "Company Event 10": ""
        }
    ]
    preprocessor(sample_csv_data, "test-batch-id", "test-batch-tag")
