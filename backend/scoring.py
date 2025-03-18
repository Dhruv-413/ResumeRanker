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
    jargon_penalty = max(min(num_entities * 0.3, 8), 0)  # Reduced penalty impact

    quality_score = max((readability_score * 0.5) + (grammar_score * 0.4) + structure_boost - jargon_penalty, 0)

    return round(quality_score, 2)

def extract_experience_details(text):
    doc = nlp(text)
    
    job_titles = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "WORK_OF_ART"]]
    skills = [token.text.lower() for token in doc if token.pos_ == "NOUN" and len(token.text) > 2]
    
    date_patterns = [
        r"(\b[A-Za-z]{3,9}\s\d{4})\s[–-]\s(\b[A-Za-z]{3,9}\s\d{4}|\b[Pp]resent\b)",
        r"(\d{4})\s[–-]\s(\d{4}|\b[Pp]resent\b)"
    ]
    total_months_experience = 0

    for pattern in date_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            start_date_str, end_date_str = match.groups()
            start_date = dateparser.parse(start_date_str)
            end_date = dateparser.parse(end_date_str) if "present" not in end_date_str.lower() else datetime.now()
            
            if start_date and end_date:
                total_months_experience += (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    years_experience = total_months_experience // 12
    return {
        "job_titles": list(set(job_titles)),
        "years_experience": years_experience,
        "skills": list(set(skills))
    }

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
    parts = location.split(',')
    if len(parts) > 1:
        city, country = parts[0].strip(), parts[-1].strip()
        try:
            country_obj = pycountry.countries.search_fuzzy(country)[0]
            return True
        except LookupError:
            return False
    return False

def extract_location(text):
    doc = nlp(text)
    
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    
    location_patterns = [
        r"(?:based in|located in|living in|residing in|from)\s+([A-Za-z,\s]+)",
        r"(?:address|location)(?:\s*:\s*)([A-Za-z,\s]+)",
        r"([A-Za-z]+(?:,\s*[A-Za-z]+){1,2})\s*(?:\d{5})?$"
    ]
    
    for pattern in location_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            locations.append(match.group(1).strip())
    
    valid_locations = [loc for loc in locations if is_valid_location(loc)]
    
    return valid_locations[0] if valid_locations else None

def compute_location_score(cv_location, job_location):
    if not cv_location or not job_location:
        return 0
    
    geolocator = Nominatim(user_agent="cv_analyzer")
    
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

def recommend_candidates(candidates, job_description, job_location, weights):
    results = []
    for candidate in candidates:
        quality_score = evaluate_cv_quality(candidate)

        experience_details = extract_experience_details(candidate)
        years_experience = experience_details["years_experience"]

        relevance_score = compute_similarity_bert(candidate, job_description)

        candidate_location = extract_location(candidate)
        location_score = compute_location_score(candidate_location, job_location)

        total_score = (
            (quality_score * weights.get("quality", 0)) +
            (relevance_score * weights.get("experience", 0)) +
            (years_experience * weights.get("years", 0)) +
            (location_score * weights.get("location", 0))
        ) / sum(weights.values())

        results.append({
            "candidate": candidate,
            "quality_score": quality_score,
            "relevance_score": relevance_score,
            "years_experience": years_experience,
            "location_score": location_score,
            "total_score": round(total_score, 2)
        })

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results

if __name__ == "__main__":
    sample_candidates = [
        """Experienced software engineer with 5 years in AI development. Proficient in Python, NLP, and cloud technologies. Based in New York, USA.""",
        """Sales manager with 10 years of experience in retail and e-commerce. Skilled in team management and customer relations. Based in Los Angeles, USA.""",
        """Security guard with 3 years of experience in corporate security. Certified in first aid and emergency response. Based in Chicago, USA.""",
        """Data scientist with 7 years of experience in machine learning, data analysis, and visualization. Skilled in Python, R, and SQL. Based in Boston, USA.""",
        """Marketing specialist with 4 years of experience in digital marketing, SEO, and content creation. Based in Austin, USA.""",
        """Project manager with 8 years of experience in IT project delivery, Agile methodologies, and stakeholder management. Based in Seattle, USA.""",
        """Graphic designer with 6 years of experience in branding, UI/UX design, and Adobe Creative Suite. Based in Denver, USA.""",
        """AI researcher with 3 years of experience in deep learning, computer vision, and reinforcement learning. Based in San Francisco, USA."""
    ]
    job_description = """We need an AI developer proficient in Python, NLP, and cloud platforms. The job is located in San Francisco, USA."""
    job_location = "San Francisco, USA"

    weights = {"quality": 5, "experience": 50, "years": 10, "location": 10}

    recommendations = recommend_candidates(sample_candidates, job_description, job_location, weights)
    print("Candidate Recommendations (Sorted by Total Score):\n")
    for idx, recommendation in enumerate(recommendations, start=1):
        print(f"Candidate {idx}:")
        print(f"  Total Score: {recommendation['total_score']}%")
        print(f"  Quality Score: {recommendation['quality_score']}%")
        print(f"  Relevance Score: {recommendation['relevance_score']}%")
        print(f"  Years of Experience: {recommendation['years_experience']}")
        print(f"  Location Score: {recommendation['location_score']}%")
        print()
