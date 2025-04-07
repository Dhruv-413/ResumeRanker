"""
Configuration settings for resume quality evaluation components.

This module contains constants and parameters that control the behavior
of the resume quality evaluators. Modifying these values will affect
how strictly each aspect of resume quality is judged.
"""

# Grammar & Spelling Configuration
GRAMMAR_BASE_SCORE = 100.0  # Starting score before penalties
GRAMMAR_MIN_SCORE = 0       # Minimum possible grammar score
GRAMMAR_MAX_SCORE = 100     # Maximum possible grammar score
GRAMMAR_LENGTH_NORMALIZATION = 250  # Word count used to normalize penalties

# Error weights - higher values penalize certain error types more heavily
GRAMMAR_ERROR_WEIGHTS = {
    'spelling': 3.0,    # Critical for professional docs - misspellings seriously impact perception
    'grammar': 2.0,     # Grammatical errors affect readability and comprehension
    'punctuation': 1.5, # Punctuation affects clarity and flow
    'repetition': 1.5,  # Redundant content affects conciseness
    'casing': 1.0,      # Proper capitalization reflects attention to detail
    'style': 0.5,       # Stylistic issues are less critical but still important
    'other': 0.5        # Minor or less common issues
}

# Controls how error clustering/density affects the score
GRAMMAR_DENSITY_THRESHOLDS = {
    'max_errors_per_sentence': 0.25,  # 1 error per 4 sentences is acceptable
    'penalty_per_excess': 15,         # Points deducted per error above threshold
    'max_density_penalty': 25         # Maximum penalty for high error density
}

# Penalties for errors that are close to each other
GRAMMAR_PROXIMITY_PENALTY = {
    'critical_distance': 60,     # Character distance below which errors are considered clustered
    'penalty_factor': 0.35,      # Multiplier for distance-based penalty
    'max_penalty': 15            # Maximum proximity penalty
}

# Keywords used to categorize grammar errors based on error messages
GRAMMAR_CATEGORY_RULES = {
    'spelling': ['spell', 'typo', 'misspelled', 'unknown word'],
    'grammar': ['grammar', 'verb', 'noun', 'agreement', 'determiner', 'tense'],
    'punctuation': ['punctuation', 'comma', 'period', 'semicolon', 'apostrophe'],
    'repetition': ['repeat', 'repetition', 'duplicate', 'redundant'],
    'casing': ['case', 'capitalization', 'uppercase', 'lowercase'],
    'style': ['style', 'wordy', 'simplify', 'passive voice', 'consider']
}

# Readability Configuration
READABILITY_WEIGHTS = {
    'flesch_ease': 0.30,    # General readability for wide audience
    'gunning_fog': 0.20,    # Sentence complexity measure
    'smog': 0.15,           # Polysyllabic words measure
    'coleman_liau': 0.25,   # Character-based analysis
    'dale_chall': 0.10      # Word familiarity measure
}

# Score ranges for readability categories
READABILITY_THRESHOLDS = {
    'unacceptable': (0, 49),      # Very difficult to read
    'poor': (50, 59),             # Needs improvement
    'acceptable': (60, 79),       # Good readability level for business documents
    'oversimplified': (80, 100)   # Too simple for professional context
}

# Penalty points applied to each readability category
READABILITY_PENALTIES = {
    'unacceptable': 30,     # Significant penalty for very difficult text
    'poor': 15,             # Moderate penalty for suboptimal readability
    'acceptable': 0,        # No penalty for appropriate readability
    'oversimplified': 10    # Small penalty for overly simple language
}

# Formatting Configuration
FORMAT_MAX_CATEGORY_PENALTY = 30  # Maximum penalty points per formatting category
FORMAT_WEIGHTS = {
    'sections': 1.5,  # Standard resume sections - critical
    'dates': 1.3,     # Date format consistency
    'headings': 1.2,  # Heading style consistency
    'bullets': 1.0,   # Bullet point consistency
    'spacing': 0.8    # Spacing and alignment
}

# Timeline & Tense Configuration
TIMELINE_MAX_GAP_DAYS = 180  # Maximum acceptable gap between positions (in days)
TIMELINE_PENALTY_WEIGHTS = {
    'tense_errors': 3,  # Wrong verb tense (present for past jobs, etc.)
    'gaps': 2,          # Unexplained gaps in employment
    'date_errors': 5    # Invalid or inconsistent dates
}

# Action Verb Configuration
ACTION_VERB_WEIGHTS = {
    'action_reward': 2.0,        # Points awarded for each strong action verb
    'non_action_penalty': 1.0,   # Points deducted for weak or missing verbs
    'duplicate_penalty': 0.5     # Points deducted for repeated verbs
}

# Structure Configuration
STRUCTURE_ESSENTIALS = {
    'contact': 15,      # Critical
    'experience': 15,   # Critical
    'education': 10,    # Important
    'skills': 10        # Important
}

STRUCTURE_PENALTIES = {
    'max_missing_penalty': 40,       # Maximum penalty for missing sections
    'max_order_penalty': 15,         # Maximum penalty for bad section order
    'max_completeness_penalty': 30,  # Maximum penalty for incomplete sections
    'max_consistency_penalty': 20    # Maximum penalty for inconsistent formatting
}

# Ideal section order
STRUCTURE_IDEAL_ORDER = [
    'contact', 'summary', 'experience', 'education', 
    'skills', 'projects', 'certifications', 'awards',
    'publications', 'languages', 'volunteer', 'interests', 'references'
]

# Overall CV Quality Component Weights
CV_QUALITY_COMPONENT_WEIGHTS = {
    'grammar': 0.25,      # Grammar and spelling correctness
    'readability': 0.20,  # Text readability and clarity
    'formatting': 0.20,   # Layout consistency and professional structure
    'timeline': 0.10,     # Chronological consistency and tense usage
    'action_verbs': 0.05, # Use of strong action verbs in achievements
    'structure': 0.20     # Overall document structure and organization
}
