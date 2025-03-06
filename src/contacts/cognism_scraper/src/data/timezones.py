# US States and their respective Timezones
STATE_TIMEZONE_MAPPING = {
    "California": "PT", "Oregon": "PT", "Washington": "PT", "Nevada": "PT",
    "Idaho": "MT", "Montana": "MT", "Wyoming": "MT", "Utah": "MT", "Colorado": "MT", "Arizona": "MT", "New Mexico": "MT",
    "North Dakota": "CT", "South Dakota": "CT", "Nebraska": "CT", "Kansas": "CT", "Oklahoma": "CT", "Texas": "CT",
    "Minnesota": "CT", "Iowa": "CT", "Missouri": "CT", "Arkansas": "CT", "Louisiana": "CT", "Wisconsin": "CT", "Illinois": "CT",
    "Mississippi": "CT", "Alabama": "CT", "Tennessee": "CT", "Kentucky": "CT",
    "Indiana": "ET", "Ohio": "ET", "West Virginia": "ET", "Virginia": "ET", "North Carolina": "ET", "South Carolina": "ET",
    "Georgia": "ET", "Florida": "ET", "Michigan": "ET", "Pennsylvania": "ET", "New York": "ET", "New Jersey": "ET",
    "Connecticut": "ET", "Rhode Island": "ET", "Massachusetts": "ET", "Vermont": "ET", "New Hampshire": "ET", "Maine": "ET", "D.C.": "ET", "D.C": "ET", "DC": "ET"
}

# European countries and their respective timezones
EUROPE_TIMEZONE_MAPPING = {
    "United Kingdom": "GMT", "Ireland": "GMT",
    "Portugal": "WET", "Spain": "CET", "France": "CET", "Germany": "CET", "Netherlands": "CET",
    "Belgium": "CET", "Switzerland": "CET", "Italy": "CET", "Austria": "CET", "Sweden": "CET",
    "Norway": "CET", "Denmark": "CET", "Poland": "CET", "Czech Republic": "CET", "Hungary": "CET",
    "Romania": "EET", "Bulgaria": "EET", "Greece": "EET", "Finland": "EET", "Lithuania": "EET", 
    "Latvia": "EET", "Estonia": "EET"
}

# Latin American countries and their respective timezones
LATAM_TIMEZONE_MAPPING = {
    "Mexico": "CT", "Guatemala": "CT", "Honduras": "CT", "El Salvador": "CT", "Nicaragua": "CT",
    "Costa Rica": "CT", "Panama": "ET", "Colombia": "ET", "Ecuador": "ET", "Peru": "ET",
    "Venezuela": "ET", "Bolivia": "BOT", "Chile": "CLT", "Argentina": "ART", "Uruguay": "UYT",
    "Paraguay": "PYT", "Brazil": "BRT"
}

def get_timezone(state, country):
    """Returns the timezone based on state (for US) or country (for Europe/LatAm)."""
    if country == "United States":
        return STATE_TIMEZONE_MAPPING.get(state, "Not found")
    elif country in EUROPE_TIMEZONE_MAPPING:
        return EUROPE_TIMEZONE_MAPPING[country]
    elif country in LATAM_TIMEZONE_MAPPING:
        return LATAM_TIMEZONE_MAPPING[country]
    return "Not applicable"
