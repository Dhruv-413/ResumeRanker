from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .config import WEIGHTS
from .certification import validate_certifications 

def calculate_scores(resume, job):
    cert_report = validate_certifications(
        resume["raw_text"],
        job.get("certifications", [])
    )
    
    return {
        "required_skills": _skill_score(resume["skills"], job["required_skills"]),
        "preferred_skills": _skill_score(resume["skills"], job["preferred_skills"]),
        "experience": _experience_score(resume["experience"]["years"], job["experience"]),
        "education": _education_score(resume["education"]["degrees"], job["education"]),
        "keywords": _keyword_score(resume["raw_text"], job["raw_text"]),
        "structure": resume["structure"],
        "projects": _project_score(resume["projects"], job["raw_text"]),
        "certifications": cert_report["score"]
    }

def _skill_score(candidate, required):
    if not required: return 100
    return min(len(set(candidate) & set(required)) / len(required) * 100, 100)

def _experience_score(candidate_years, required_years):
    if not required_years: return 100
    return min(candidate_years / required_years * 100, 100)

def _education_score(candidate_degrees, required_degrees):
    if not required_degrees: return 100
    return 100 if any(deg in required_degrees for deg in candidate_degrees) else 0

def _keyword_score(cv_text, jd_text):
    tfidf = TfidfVectorizer(stop_words='english').fit_transform([cv_text, jd_text])
    similarity = cosine_similarity(tfidf[0], tfidf[1])[0][0] * 100
    return similarity * 0.8 if (tfidf[0].sum()/len(cv_text.split())) > 0.15 else similarity

def _project_score(projects, jd_text):
    if not projects: return 0
    tfidf = TfidfVectorizer().fit_transform([' '.join(projects), jd_text])
    return cosine_similarity(tfidf[0], tfidf[1])[0][0] * 100
