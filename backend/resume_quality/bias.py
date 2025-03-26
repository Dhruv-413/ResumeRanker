from detoxify import Detoxify
import re

BIAS_PATTERNS = {
    "gender": r'\b(he|she|him|her|his|hers)\b',
    "age": r'\b(\d+ years old|born in \d{4})\b',
    "ethnicity": r'\b(asian|african|caucasian|hispanic)\b'
}

def detect_bias(text):
    results = {
        "bias_score": 0,
        "issues": []
    }
    
    # Toxic content detection
    toxicity = Detoxify('unbiased').predict(text)
    results["bias_score"] = toxicity['toxicity'] * 100
    
    # Pattern-based detection
    for category, pattern in BIAS_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            results["issues"].append(category)
    
    # Anonymization
    anonymized = re.sub(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', '[NAME]', text)
    return results, anonymized