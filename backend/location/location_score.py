import pycountry
import re
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import math
from backend.utils.spacy_model import nlp  

geolocator = Nominatim(user_agent="cv_analyzer")

def is_valid_location(location):
    parts = [p.strip() for p in location.split(',')]

    if len(parts) == 2:
        city, country = parts[0], parts[1]
    elif len(parts) == 1:
        city, country = parts[0], None
    else:
        return False

    if country:
        try:
            pycountry.countries.search_fuzzy(country)[0]
        except LookupError:
            return False

    try:
        city_location = geolocator.geocode(city, timeout=5)
        if city_location:
            return True
    except Exception:
        return False

    return False

def extract_location(text):
    doc = nlp(text)

    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    location_patterns = [
        r"^[A-Za-z\s]+,\s*[A-Za-z\s]+$",
    ]

    for pattern in location_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            try:
                location = match.group(0).strip()
                if location:
                    locations.insert(0, location)
            except (IndexError, AttributeError):
                continue

    for loc in locations:
        if is_valid_location(loc):
            return loc

    return ""

def compute_location_score(cv_location, job_location):
    if not cv_location or not job_location:
        return 0

    try:
        cv_loc = geolocator.geocode(cv_location, timeout=10)
        job_loc = geolocator.geocode(job_location, timeout=10)

        if cv_loc and job_loc:
            distance = geodesic((cv_loc.latitude, cv_loc.longitude), (job_loc.latitude, job_loc.longitude)).km

            return round(100 * math.exp(-0.0006 * (distance - 100)) if distance > 100 else 100,2)
    except Exception:
        cv_parts = cv_location.lower().split(',')
        job_parts = job_location.lower().split(',')

        if cv_parts[-1].strip() == job_parts[-1].strip():
            return 70
        return 30

    return 0