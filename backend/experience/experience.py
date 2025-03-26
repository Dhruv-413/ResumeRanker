import re
from datetime import datetime
import dateparser
from backend.utils.spacy_model import nlp 

def extract_experience_details(text):
    doc = nlp(text)
    skills = list(set(token.text.lower() for token in doc if token.pos_ == "NOUN" and len(token.text) > 2))

    experience_section = extract_experience_section(text)
    if not experience_section:
        print("No experience section found.")
        return {
            "years_experience": 0,
            "skills": skills
        }

    date_patterns = [
        r"(\b[A-Za-z]{3,9}\s\d{4})\s*[-–]\s*(\b[A-Za-z]{3,9}\s\d{4}|\b[Pp]resent\b)",
    ]

    total_months_experience = 0
    for pattern in date_patterns:
        matches = re.finditer(pattern, experience_section)
        for match in matches:
            start_date_str, end_date_str = match.groups()
            start_date = dateparser.parse(start_date_str)
            end_date = datetime.now() if "present" in end_date_str.lower() else dateparser.parse(end_date_str)

            if start_date and end_date:
                months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                total_months_experience += max(0, months_diff)
                
                print(f"Start Date: {start_date}, End Date: {end_date}, Months Diff: {months_diff}")
                print(total_months_experience)

    years_experience = total_months_experience / 12
    print(f"Experience Details: {{'years_experience': {round(years_experience, 1)}, 'skills': {list(skills)}}}")
    print(f"Experience Section: {experience_section}")
    return {
        "years_experience": round(years_experience, 1),
        "skills": skills
    }

def extract_experience_section(text):
    experience_keywords = ["experience", "work history", "employment", "jobs", "professional experience"]
    section_end_keywords = [
        "leadership", "leadership and activities", 
        "education", "degree", "university", "college", "school", 
        "projects", "certifications", "skills", "languages"
    ]

    experience_start = None
    for keyword in experience_keywords:
        match = re.search(rf"\b{keyword}\b", text, re.IGNORECASE)
        if match:
            experience_start = match.start()
            break

    if experience_start is None:
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
