import re
import spacy
import dateparser
from datetime import datetime
from .config import SKILL_SYNONYMS

nlp = spacy.load("en_core_web_lg")

def parse_resume(text):
    return {
        "experience": extract_experience(text),
        "education": extract_education(text),
        "skills": extract_skills(text),
        "projects": extract_projects(text),
        "structure": calculate_structure_score(text),
        "raw_text": text
    }

def extract_experience(text):
    section = _find_section(text, ["experience", "work history"])
    dates = _extract_dates(section)
    total_months = sum((end.year - start.year) * 12 + (end.month - start.month) 
                     for start, end in dates)
    return {
        "years": round(total_months / 12, 1),
        "positions": [ent.text for ent in nlp(section).ents if ent.label_ == "TITLE"]
    }

def _find_section(text, keywords):
    for keyword in keywords:
        match = re.search(rf'\b{keyword}\b', text, re.IGNORECASE)
        if match:
            start = match.start()
            next_section = re.search(r'\n\s*[A-Z]+\s*\n', text[start:])
            end = start + (next_section.start() if next_section else len(text))
            return text[start:end]
    return ""

def _extract_dates(text):
    date_pattern = r"(\b[A-Za-z]{3,9}\s\d{4})\s*[-–]\s*(\b[A-Za-z]{3,9}\s\d{4}|\bPresent\b)"
    dates = []
    for match in re.finditer(date_pattern, text, re.IGNORECASE):
        start_str, end_str = match.groups()
        start = dateparser.parse(start_str)
        end = dateparser.parse(end_str) if "present" not in end_str.lower() else datetime.now()
        if start and end: dates.append((start, end))
    return dates

def extract_education(text):
    section = _find_section(text, ["education", "academic background"])
    return {
        "degrees": re.findall(r'\b(B\.?S\.?|B\.?A\.?|M\.?S\.?|Ph\.?D\.?)\b', section),
        "institutions": [ent.text for ent in nlp(section).ents if ent.label_ == "ORG"]
    }

def extract_skills(text):
    doc = nlp(text)
    skills = set()
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 3:
            lemma = SKILL_SYNONYMS.get(token.lemma_.lower(), token.lemma_.lower())
            skills.add(lemma)
    return list(skills)

def extract_projects(text):
    section = _find_section(text, ["projects", "key achievements"])
    return [p.strip() for p in re.split(r'\n\s*\d+\.|\n\s*•', section) if len(p.strip()) > 50]

def calculate_structure_score(text):
    score = 0
    score += len(re.findall(r'\n\s*(EXPERIENCE|EDUCATION|PROJECTS|SKILLS)\s*\n', text)) * 10
    score += min((text.count('•') + text.count('- ')) * 2, 20)
    dates = re.findall(r'\b(?:Jan|Feb|Mar|April|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b', text)
    score += 50 - (len(set(dates)) * 5) if dates else 50
    return min(score, 100)