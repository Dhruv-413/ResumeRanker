import re
import textstat
import language_tool_python
from backend.utils.spacy_model import nlp  # Import shared SpaCy model

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