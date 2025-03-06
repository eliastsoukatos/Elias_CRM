# clutch_mapper.py

import re
import uuid
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

def clean_url(url):
    if not url:
        return ""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if "u" in query and query["u"]:
        final_url = unquote(query["u"][0])
    elif "provider_website" in query and query["provider_website"]:
        final_url = query["provider_website"][0]
        if not final_url.startswith("http"):
            final_url = "https://" + final_url
    else:
        final_url = url

    parsed_final = urlparse(final_url)
    scheme = parsed_final.scheme if parsed_final.scheme else "https"
    netloc = parsed_final.netloc
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return f"{scheme}://{netloc}"

def standardize_string(s):
    if isinstance(s, str):
        return ' '.join(s.lower().strip().split())
    return s

def standardize_date(date_str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue
    return None

def standardize_founded(founded_str):
    if not founded_str:
        return None
    founded_str = founded_str.lower().replace("founded", "").strip()
    if re.match(r'^\d{4}$', founded_str):
        return f"{founded_str}-01-01"
    return standardize_date(founded_str)

def extract_social_links(social_links):
    result = {
        "linkedin": None,
        "facebook": None,
        "twitter": None,
        "instagram": None
    }
    
    links_list = []
    if isinstance(social_links, list):
        links_list = social_links
    elif isinstance(social_links, str):
        links_list = [link.strip() for link in social_links.split(',') if link.strip()]
    
    for link in links_list:
        # Preserve the full social media URLs including company handles
        if "linkedin.com" in link:
            result["linkedin"] = link
        elif "facebook.com" in link:
            result["facebook"] = link
        elif "twitter.com" in link or "x.com" in link:
            result["twitter"] = link
        elif "instagram.com" in link:
            result["instagram"] = link
            
    return result

def map_companies(record, batch_id, batch_tag):
    summary = record.get("summary", {})
    website_url = record.get("websiteUrl", "")
    website = clean_url(website_url) if website_url else ""
    domain = urlparse(website).netloc
    if domain.startswith("www."):
        domain = domain[4:]
    employees = summary.get("employees", "")
    if "-" in employees:
        headcount_range = employees.strip()
        headcount = None
    else:
        headcount_range = None
        headcount = employees.strip() if employees else ""
    company = {
        "company_id": str(uuid.uuid4()),
        "name": summary.get("name", "").strip(),  # conserva mayúsculas
        "website": website,
        "domain": domain,
        "headcount": headcount,
        "headcount_range": headcount_range,
        "description": summary.get("description", ""),
        "revenue": None,
        "company_type": None,
        "founded": standardize_founded(summary.get("founded", "")),
        "verification_status": summary.get("verificationStatus", ""),
        "min_project_size": summary.get("minProjectSize", ""),
        "avg_hourly_rate": summary.get("averageHourlyRate", "")
    }
    return company

def map_company_locations(record):
    locations = []
    addresses = record.get("summary", {}).get("addresses", [])
    for addr in addresses:
        location = {
            "street": addr.get("street", ""),
            "city": standardize_string(addr.get("city", "")),
            "state": standardize_string(addr.get("state", "")),
            "country": standardize_string(addr.get("country", "")),
            "postal_code": addr.get("postalCode", "")
        }
        locations.append(location)
    return locations

def map_company_phones(record):
    phones = []
    addresses = record.get("summary", {}).get("addresses", [])
    for addr in addresses:
        phone = addr.get("phone", "")
        if phone:
            phones.append({"phone_number": phone})
    return phones

def map_company_focus_areas(record):
    focus_areas = []
    for focus in record.get("focus", []):
        title = focus.get("title", "")
        for item in focus.get("values", []):
            focus_areas.append({
                "focus_title": title,
                "focus_name": item.get("name", ""),
                "percentage": item.get("percentage", None)
            })
    return focus_areas

def map_company_social_links(record):
    social_links = record.get("summary", {}).get("socialLinks", [])
    links = extract_social_links(social_links)
    
    # Only return a record if at least one social media link exists
    if any(links.values()):
        return [links]
    return []

def map_company_verifications(record):
    verification = record.get("verification", {})
    business_entity = verification.get("businessEntity", {})
    
    # Create the verification object
    verification_data = {
        "verification_status": verification.get("verificationStatus", ""),
        "source": business_entity.get("source", ""),
        "last_updated": standardize_date(business_entity.get("lastUpdated", ""))
    }
    
    # Only return a verification record if it has meaningful data
    if verification_data["verification_status"] or verification_data["source"]:
        return verification_data
    return None

def map_company_reviews(record):
    reviews = []
    for rev in record.get("reviews", []):
        review = {
            "review_id": str(uuid.uuid4()),
            "reviewer_name": rev.get("reviewer", {}).get("name", ""),
            "review_title": rev.get("name", ""),
            "review_content": rev.get("review", {}).get("comments", ""),
            "review_rating": rev.get("review", {}).get("rating", None),
            "review_date": standardize_date(rev.get("datePublished", ""))
        }
        reviews.append(review)
    return reviews

def map_company_portfolio(record):
    portfolio_items = []
    for item in record.get("portfolio", []):
        portfolio_items.append({
            "portfolio_id": item.get("id") or str(uuid.uuid4()),
            "portfolio_name": item.get("title", ""),
            "portfolio_category": ", ".join(item.get("services", [])) if isinstance(item.get("services"), list) else item.get("services", ""),
            "portfolio_size": item.get("projectSize", ""),
            "portfolio_description": item.get("description", "")
        })
    return portfolio_items

def map_company_ratings(record):
    summary = record.get("summary", {})
    rating_data = {
        "overall_rating": summary.get("rating", None),
        "review_count": summary.get("noOfReviews", None)
    }
    
    # Only return a rating record if it has meaningful data
    if rating_data["overall_rating"] is not None or rating_data["review_count"] is not None:
        return rating_data
    return None

def map_all(record, batch_id, batch_tag):
    result = {
        "companies": map_companies(record, batch_id, batch_tag),
        "company_locations": map_company_locations(record),
        "company_phones": map_company_phones(record),
        "company_technologies": [],      
        "company_industries": [],        
        "company_identifiers": [],       
        "company_reviews": map_company_reviews(record),
        "company_portfolio": map_company_portfolio(record),
        "company_focus_areas": map_company_focus_areas(record),
        "company_social_links": map_company_social_links(record),
        "company_verifications": [],
        "company_events": [],
        "company_ratings": []
    }
    
    # Add verification data if it exists
    verification = map_company_verifications(record)
    if verification:
        result["company_verifications"] = [verification]
        
    # Add rating data if it exists
    rating = map_company_ratings(record)
    if rating:
        result["company_ratings"] = [rating]
    
    return result
