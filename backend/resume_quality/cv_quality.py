import re
import textstat
import language_tool_python
from backend.utils.spacy_model import nlp
from .resume_parser import parse_resume
from .job_analyzer import parse_job_description
from .scoring import calculate_scores, WEIGHTS
from .similarity import semantic_similarity
from .bias import detect_bias
from .certification import validate_certifications

def evaluate_cv_quality(resume_text, jd_text):
    # Bias detection and anonymization
    bias_report, anonymized_text = detect_bias(resume_text)
    
    # Parse resume and job description
    resume_data = parse_resume(anonymized_text)
    job_data = parse_job_description(jd_text)
    
    # Certification validation
    cert_report = validate_certifications(
        resume_data["raw_text"],  # Fixed key name
        job_data.get("certifications", [])
    )
    
    # Calculate component scores
    component_scores = calculate_scores(resume_data, job_data)
    semantic_score = semantic_similarity(anonymized_text, jd_text)
    
    # Calculate weighted score
    weighted_score = sum(
        component_scores[category] * weight 
        for category, weight in WEIGHTS.items()
    )
    
    # Combine scores
    final_score = (weighted_score * 0.7) + (semantic_score * 0.3)
    
    return {
        "final_score": round(final_score, 1),
        "bias_report": bias_report,
        "certification_report": cert_report,
        "component_scores": {
            "weighted_components": {
                k: round(v, 1) 
                for k, v in component_scores.items()
            },
            "semantic_similarity": round(semantic_score, 1)
        }
    }