import re
from collections import defaultdict
from typing import Dict, Any, Set, List
from .evaluator_base import ResumeEvaluator
from .config import FORMAT_MAX_CATEGORY_PENALTY, FORMAT_WEIGHTS

class FormattingEvaluator(ResumeEvaluator):
    """Evaluates the formatting quality of a resume."""
    
    def evaluate(self, text: str) -> Dict[str, Any]:
        try:
            lines = [line.strip() for line in text.split('\n')]
            penalties = defaultdict(int)
            section_details = self._analyze_sections(lines)
            # Use base class method for bullet point extraction
            bullet_details = self._analyze_bullet_points(text)
            date_details = self._analyze_date_formats(lines)
            spacing_details = self._analyze_spacing(lines)
            
            # Calculate penalties for each category
            penalties['sections'] = min(
                len(section_details['missing']) * 12, 
                FORMAT_MAX_CATEGORY_PENALTY
            )
            
            penalties['bullets'] = min(
                (len(bullet_details['styles'])-1) * 6 if bullet_details['styles'] else 0, 
                FORMAT_MAX_CATEGORY_PENALTY
            )
            
            penalties['dates'] = min(
                (len(date_details['formats'])-1) * 8 if date_details['formats'] else 0,
                FORMAT_MAX_CATEGORY_PENALTY
            )
            
            penalties['spacing'] = min(
                spacing_details['issues'] * 3,
                FORMAT_MAX_CATEGORY_PENALTY
            )
            
            # Calculate heading penalties
            if section_details['headings']['mixed_style']:
                penalties['headings'] += 8
            
            # Weighted penalty calculation
            total_penalty = sum(
                min(penalty * FORMAT_WEIGHTS.get(cat, 1.0), FORMAT_MAX_CATEGORY_PENALTY)
                for cat, penalty in penalties.items()
            )
            
            score = max(0, 100 - int(total_penalty))
            
            return {
                "score": score,
                "details": {
                    "penalties": dict(penalties),
                    "sections": section_details,
                    "bullets": bullet_details,
                    "dates": date_details,
                    "spacing": spacing_details
                }
            }
        except Exception as e:
            print(f"Error in format evaluation: {e}")
            return {"score": 60, "details": {"error": str(e)}}  # Default fallback score
    
    def _analyze_sections(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze headings and sections."""
        heading_patterns = [
            re.compile(r'^[A-Z][a-z]+(?: [A-Z][a-z]+)*:?$'),  # Title Case
            re.compile(r'^[A-Z\s&]+:?$'),                     # All Caps
            re.compile(r'^[A-Z][a-z]+(?:[\-/&][A-Z][a-z]+)*:?$')  # Mixed case
        ]
        
        section_checks = {
            'education': re.compile(r'\b(education|academic)\b', re.I),
            'experience': re.compile(r'\b(experience|employment|work\s*history)\b', re.I),
            'skills': re.compile(r'\b(skills?|competencies|expertise)\b', re.I),
            'projects': re.compile(r'\b(projects|portfolio)\b', re.I)
        }
        
        headings = []
        heading_styles = set()
        with_colon = 0
        without_colon = 0
        present_sections = set()
        
        for line in lines:
            if any(pattern.fullmatch(line) for pattern in heading_patterns):
                headings.append(line)
                
                # Track heading styles
                if line.isupper():
                    heading_styles.add('all_caps')
                elif line.istitle():
                    heading_styles.add('title_case')
                else:
                    heading_styles.add('mixed_case')
                
                # Track colon usage
                if ':' in line:
                    with_colon += 1
                else:
                    without_colon += 1
                
                # Section detection
                for section, pattern in section_checks.items():
                    if pattern.search(line):
                        present_sections.add(section)
                        break
        
        missing = {'education', 'experience', 'skills', 'projects'} - present_sections
        mixed_style = len(heading_styles) > 1
        mixed_colons = with_colon > 0 and without_colon > 0
        
        return {
            'headings': {
                'count': len(headings),
                'styles': list(heading_styles),
                'mixed_style': mixed_style,
                'mixed_colons': mixed_colons
            },
            'present': list(present_sections),
            'missing': list(missing)
        }
    
    def _analyze_bullet_points(self, text: str) -> Dict[str, Any]:
        """Analyze bullet point consistency."""
        bullet_regex = re.compile(r'^(\s*)([•\-*●◦○]|\d+\.)\s+')
        styles = defaultdict(set)
        
        # Use the base class method to get bullets
        bullets = self.extract_bullet_points(text)
        bullet_count = len(bullets)
        
        # Analyze the formatting styles
        for line in text.split('\n'):
            match = bullet_regex.match(line)
            if match:
                indent = len(match.group(1))
                symbol = match.group(2)
                styles[symbol].add(indent)
        
        return {
            'count': bullet_count,
            'styles': dict((k, list(v)) for k, v in styles.items())
        }
    
    def _analyze_date_formats(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze date format consistency."""
        date_patterns = {
            'month_year': r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b',
            'mm/yyyy': r'\b(0[1-9]|1[0-2])/\d{4}\b',
            'yyyy-mm': r'\d{4}-(0[1-9]|1[0-2])\b',
            'full_date': r'\b\d{4}-\d{2}-\d{2}\b',
            'year_range': r'\d{4}[\-–—]\d{4}\b',
            'month_range': r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* [\-–—] '
        }
        
        formats = set()
        format_examples = {}
        
        for line in lines:
            for name, pattern in date_patterns.items():
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    formats.add(name)
                    format_examples[name] = match.group(0)
        
        return {
            'formats': list(formats),
            'examples': format_examples
        }
    
    def _analyze_spacing(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze spacing consistency."""
        multi_space_count = 0
        consecutive_empty = 0
        empty_lines_count = 0
        issues = 0
        
        prev_empty = False
        for line in lines:
            # Multiple spaces between words
            if re.search(r'\s{2,}', line.strip()):
                multi_space_count += 1
                issues += 1
            
            # Consecutive empty lines
            if not line.strip():
                empty_lines_count += 1
                if prev_empty:
                    consecutive_empty += 1
                    issues += 1
                prev_empty = True
            else:
                prev_empty = False
        
        return {
            'multi_space_count': multi_space_count,
            'consecutive_empty': consecutive_empty,
            'empty_lines_count': empty_lines_count,
            'issues': issues
        }
