import re
import spacy

nlp = spacy.load("en_core_web_lg")

def parse_job_description(text):
    doc = nlp(text)
    return {
        "required_skills": _extract_requirements(doc, "required"),
        "preferred_skills": _extract_requirements(doc, "preferred"),
        "experience": _extract_experience(text),
        "education": _extract_education(text),
        "certifications": _extract_certifications(text), 
        "raw_text": text
    }
def _extract_certifications(text):
    cert_pattern = r"\b([A-Za-z]+ (?:Certification|Certified|Certificate)\b|AWS|PMP|CCNA)\b"
    matches = re.findall(cert_pattern, text, flags=re.IGNORECASE)
    return list(set([m.upper() for m in matches if len(m) > 3]))

def _extract_requirements(doc, req_type):
    return list(set(
        chunk.text.lower() 
        for sent in doc.sents 
        if req_type in sent.text.lower() 
        for chunk in sent.noun_chunks
    ))

def _extract_experience(text):
    matches = re.findall(r'(\d+)\+? years?', text)
    return max(map(int, matches)) if matches else 0

def _extract_education(text):
    return list(set(re.findall(r'\b(B\.?S\.?|B\.?A\.?|M\.?S\.?|Ph\.?D\.?)\b', text)))
