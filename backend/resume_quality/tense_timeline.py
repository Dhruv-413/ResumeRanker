import spacy
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from dateutil.parser import parse, ParserError
from collections import defaultdict
from .evaluator_base import ResumeEvaluator
from .config import TIMELINE_MAX_GAP_DAYS, TIMELINE_PENALTY_WEIGHTS

class TenseTimelineEvaluator(ResumeEvaluator):
    """Evaluates tense consistency and timeline coherence in resumes."""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        # Common irregular past tense verbs
        self.irregular_past_tense = {
            'ran', 'spoke', 'wrote', 'ate', 'drank', 'drove', 'broke',
            'began', 'flew', 'knew', 'took', 'saw', 'came', 'went'
        }
    
    def evaluate(self, text: str) -> Dict[str, Any]:
        try:
            # Extract work experience sections using base class method
            experience_section = self.extract_section(text, ["experience", "work history", "employment", "jobs", "professional experience"])
            if not experience_section:
                return {"score": 70, "details": {"error": "No work experience sections found"}}
            
            work_exp = self._extract_work_experience(experience_section)
            if not work_exp:
                return {"score": 70, "details": {"error": "No work experience entries found"}}
            
            issues = defaultdict(list)
            parsed_roles = []
            date_parse_errors = []

            # Parse dates for each work experience entry
            for idx, exp in enumerate(work_exp):
                start, end, error = self._parse_date_range(exp.get('dates', ''))
                if error or not start:
                    date_parse_errors.append({
                        "entry": idx,
                        "dates": exp.get('dates', ''),
                        "error": error or "Invalid start date"
                    })
                    continue
                
                parsed_roles.append({
                    'start': start,
                    'end': end,  # None indicates a current role
                    'bullets': exp.get('bullets', []),
                    'raw_dates': exp.get('dates', '')
                })

            # Timeline analysis
            if len(parsed_roles) > 1:
                # Sort by start date
                parsed_roles.sort(key=lambda x: x['start'])
                
                # Check for gaps and overlaps
                for i in range(1, len(parsed_roles)):
                    previous = parsed_roles[i-1]
                    current = parsed_roles[i]
                    
                    # Gap detection
                    if previous['end'] is not None:
                        gap_days = (current['start'] - previous['end']).days
                        if gap_days > TIMELINE_MAX_GAP_DAYS:
                            issues['gaps'].append({
                                "days": gap_days,
                                "from": previous['raw_dates'],
                                "to": current['raw_dates']
                            })
                    
                    # Overlap detection
                    previous_end = previous['end'] if previous['end'] is not None else datetime.max.date()
                    if current['start'] < previous_end:
                        issues['overlaps'].append({
                            "from": previous['raw_dates'],
                            "to": current['raw_dates']
                        })

            # Tense consistency check
            for role in parsed_roles:
                expected_tense = 'present' if role['end'] is None else 'past'
                for bullet in role['bullets']:
                    tense_errors = self._check_tense_consistency(bullet, expected_tense)
                    if tense_errors:
                        issues['tense_errors'].extend([{
                            "text": bullet,
                            "role": role['raw_dates'],
                            "token": e['token'],
                            "expected": expected_tense,
                            "detected": e['detected']
                        } for e in tense_errors])
            
            # Calculate penalties
            penalties = {
                'tense_errors': len(issues['tense_errors']) * TIMELINE_PENALTY_WEIGHTS['tense_errors'],
                'gaps': len(issues['gaps']) * TIMELINE_PENALTY_WEIGHTS['gaps'],
                'date_errors': len(date_parse_errors) * TIMELINE_PENALTY_WEIGHTS['date_errors'],
                'overlaps': len(issues['overlaps']) * 2  # Additional penalty for overlaps
            }
            
            total_penalty = sum(penalties.values())
            score = max(0, 100 - total_penalty)
            
            return {
                "score": score,
                "details": {
                    "penalties": penalties,
                    "issues": {k: v for k, v in issues.items() if v},
                    "parse_errors": date_parse_errors,
                    "roles_count": len(parsed_roles)
                }
            }
        except Exception as e:
            print(f"Error in tense timeline evaluation: {e}")
            return {"score": 65, "details": {"error": str(e)}}  # Default fallback score
    
    def _extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience sections and their bullet points."""
        # Simple extraction based on common patterns
        # Could be improved with more sophisticated section parsing
        experience_sections = []
        
        # Find potential date ranges
        date_pattern = r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[\s\.]+ \d{4})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|December|January|February|March|April|May|June|July|August|September|October|November|December)[\s\.]+ \d{4}|[Pp]resent|[Cc]urrent)\b'
        
        date_matches = list(re.finditer(date_pattern, text))
        
        for i, match in enumerate(date_matches):
            date_range = match.group(0)
            
            # Determine end of section (next date or end of text)
            start_pos = match.end()
            end_pos = date_matches[i+1].start() if i+1 < len(date_matches) else len(text)
            
            section_text = text[start_pos:end_pos].strip()
            
            # Use base class method to extract bullet points
            bullets = self.extract_bullet_points(section_text)
            
            experience_sections.append({
                'dates': date_range,
                'text': section_text,
                'bullets': bullets or [section_text]  # If no bullets, use whole section
            })
        
        return experience_sections
    
    def _parse_date_range(self, date_range: str) -> Tuple[Optional[datetime.date], Optional[datetime.date], Optional[str]]:
        """Parse a date range string and return (start_date, end_date, error_message)."""
        if not date_range:
            return None, None, "Empty date range"
        
        try:
            # Clean up and normalize
            cleaned = re.sub(r'[^\w\s–—/-]', '', date_range.strip())
            parts = re.split(r'\s*(?:–|—|-|to|through|until)\s*', cleaned, maxsplit=1)
            
            start = self._parse_single_date(parts[0].strip()) if parts[0] else None
            end = None if len(parts) < 2 else (
                None if re.search(r'\b(?:present|current)\b', parts[1], re.IGNORECASE) 
                else self._parse_single_date(parts[1].strip())
            )
            
            return start, end, None
        except Exception as e:
            return None, None, str(e)
    
    def _parse_single_date(self, date_str: str) -> datetime.date:
        """Parse an individual date string to a date object."""
        try:
            if re.search(r'\b(?:present|current)\b', date_str, re.IGNORECASE):
                return None
            return parse(date_str, fuzzy=True).date()
        except (ParserError, ValueError) as e:
            raise ValueError(f"Failed to parse date: {date_str}")
    
    def _check_tense_consistency(self, bullet: str, expected_tense: str) -> List[Dict[str, Any]]:
        """Check if verbs in a bullet point are in the expected tense."""
        errors = []
        doc = self.nlp(bullet)
        
        for token in doc:
            if token.pos_ == 'VERB':
                detected_tense = self._detect_verb_tense(token)
                if detected_tense != 'unknown' and detected_tense != expected_tense:
                    errors.append({
                        'token': token.text,
                        'detected': detected_tense,
                    })
        
        return errors
    
    def _detect_verb_tense(self, token) -> str:
        """Determine the tense of a token."""
        # Check explicit morphological features first
        if 'Tense=Past' in token.morph:
            return 'past'
        if 'Tense=Pres' in token.morph:
            return 'present'
        
        # Fallback based on POS tags
        if token.tag_ == 'VBD':  # Past tense
            return 'past'
        if token.tag_ in ['VBZ', 'VBP']:  # Present tense forms
            return 'present'
        if token.tag_ == 'VBG':  # Gerund/present participle (often ongoing)
            return 'present'
        
        # Check for irregular past tense forms
        if token.text.lower() in self.irregular_past_tense:
            return 'past'
        
        # Check for words ending in -ed
        if token.text.lower().endswith('ed'):
            return 'past'
        
        return 'unknown'
