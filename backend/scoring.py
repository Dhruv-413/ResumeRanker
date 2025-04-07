import re
import math
import spacy
import torch
import pycountry
import textstat
import language_tool_python
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime
import dateparser

nlp = spacy.load("en_core_web_lg")
geolocator = Nominatim(user_agent="cv_analyzer")

# def evaluate_cv_quality(text):
#     ats_data = ResumeParser(text, custom_nlp=nlp).get_extracted_data()  # Pass the loaded SpaCy model

#     fk_grade = textstat.flesch_kincaid_grade(text)
#     readability_score = max(100 - (fk_grade * 3), 0)

#     extracted_skills = ats_data.get("skills", []) if ats_data else []
#     num_skills = len(extracted_skills)
#     keyword_score = min(num_skills * 5, 100)

#     num_bullet_points = text.count("•") + text.count("- ")
#     structure_score = min(num_bullet_points * 3, 20)

#     ats_score = (readability_score * 0.3) + (keyword_score * 0.5) + (structure_score * 0.2)

#     return round(ats_score, 2)

def evaluate_cv_quality(text):
    tool = language_tool_python.LanguageTool('en-US')

    sentences = re.split(r'(?<=[.!?]) +', text)
    errors = sum(len(tool.check(sent)) for sent in sentences)

    grammar_penalty = min(errors * 1.5, 40)
    grammar_score = max(100 - grammar_penalty, 0)

    fk_grade = textstat.flesch_kincaid_grade(text)
    dale_chall = textstat.dale_chall_readability_score(text)
    smog = textstat.smog_index(text)

    fk_score = max(100 - (fk_grade * 3), 0)
    dale_chall_score = max(100 - (dale_chall * 3), 0)
    smog_score = max(100 - (smog * 3), 0)

    readability_score = (fk_score * 0.4) + (dale_chall_score * 0.3) + (smog_score * 0.3)

    num_bullet_points = text.count("•") + text.count("- ")
    num_short_sentences = sum(1 for sent in sentences if len(sent.split()) < 6)
    structure_boost = min((num_bullet_points + num_short_sentences) * 2, 10)

    doc = nlp(text)
    num_entities = sum(1 for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "TECHNOLOGY"])
    jargon_penalty = max(min(num_entities * 0.3, 8), 0)

    quality_score = max((readability_score * 0.5) + (grammar_score * 0.4) + structure_boost - jargon_penalty, 0)

    return round(quality_score, 2)

def extract_experience_details(text):
    doc = nlp(text)
    
    skills = list(set(token.text.lower() for token in doc if token.pos_ == "NOUN" and len(token.text) > 2))

    experience_section = extract_experience_section(text)
    
    date_patterns = [
        r"(\b[A-Za-z]{3,9}\s\d{4})\s*[-–]\s*(\b[A-Za-z]{3,9}\s\d{4}|\b[Pp]resent\b)",  # "Aug 2024 - Present"
    ]

    total_months_experience = 0
    extracted_dates = []

    for pattern in date_patterns:
        matches = re.finditer(pattern, experience_section) # Only search inside experience or it will search in education
        for match in matches:
            start_date_str, end_date_str = match.groups()
            start_date = dateparser.parse(start_date_str)
            end_date = datetime.now() if "present" in end_date_str.lower() else dateparser.parse(end_date_str)

            if start_date and end_date:
                extracted_dates.append((start_date_str, start_date, end_date_str, end_date))
                months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                total_months_experience += max(0, months_diff)

    years_experience = total_months_experience / 12

    # print("\n--- Extracted Experience Dates (From Experience Section Only) ---")
    # for entry in extracted_dates:
    #     print(f"Start: {entry[0]} → {entry[1]}, End: {entry[2]} → {entry[3]}")

    return {
        "years_experience": round(years_experience, 1),
        "skills": skills
    }

def extract_experience_section(text):
    experience_keywords = ["experience", "work history", "employment", "jobs", "professional experience"]
    section_end_keywords = ["education", "degree", "university", "college", "school", "projects", "certifications", "skills", "languages"]

    experience_start = None
    for keyword in experience_keywords:
        match = re.search(rf"\b{keyword}\b", text, re.IGNORECASE)
        if match:
            experience_start = match.start()
            break

    if experience_start is None:
        print("No experience section found!")
        return ""

    section_end = None
    for keyword in section_end_keywords:
        match = re.search(rf"\b{keyword}\b", text[experience_start:], re.IGNORECASE)
        if match:
            section_end = experience_start + match.start()
            break

    experience_section = text[experience_start:section_end] if section_end else text[experience_start:]
    experience_section = re.sub(r"[^a-zA-Z0-9\s.,\-–]", "", experience_section)
    return experience_section.strip()

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

def compute_similarity_bert(cv_text, job_description):
    def get_embedding(text):
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()
    
    cv_embedding = get_embedding(cv_text)
    job_embedding = get_embedding(job_description)
    similarity = cosine_similarity(cv_embedding, job_embedding)[0][0] * 100
    return round(similarity, 2)

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
            print(f"Extracted Location: {loc}")
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

            if distance < 30:
                return 100
            elif distance < 100:
                return 90
            elif distance < 300:
                return 75
            elif distance < 1000:
                return 50
            else:
                return max(10, int(100 - (10 * math.log10(distance))))
    except Exception as e:
        print(f"Geocoding error: {e}")

        cv_parts = cv_location.lower().split(',')
        job_parts = job_location.lower().split(',')

        if cv_parts[-1].strip() == job_parts[-1].strip():
            return 70
        return 30

    return 0
