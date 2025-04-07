import re
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
from .evaluator_base import ResumeEvaluator
from .config import STRUCTURE_ESSENTIALS, STRUCTURE_PENALTIES, STRUCTURE_IDEAL_ORDER

class StructureEvaluator(ResumeEvaluator):
    """Evaluates the structural organization of a resume."""
    
    def __init__(self):
        """Initialize the structure evaluator."""
        # Define common section patterns
        self.section_patterns = {
            'contact': r'\b(?:contact|contact info|personal info|address|phone|email)\b',
            'summary': r'\b(?:summary|profile|objective|about me|professional summary)\b',
            'experience': r'\b(?:experience|employment|work history|professional experience|career)\b',
            'education': r'\b(?:education|academic|degree|university|school|college)\b',
            'skills': r'\b(?:skills|technical skills|core competencies|expertise|qualifications)\b',
            'projects': r'\b(?:projects|portfolio|works|case studies)\b',
            'certifications': r'\b(?:certifications|certificates|licenses|credentials)\b',
            'awards': r'\b(?:awards|honors|achievements|recognitions)\b',
            'publications': r'\b(?:publications|papers|articles|research|presentations)\b',
            'languages': r'\b(?:languages|language skills)\b',
            'volunteer': r'\b(?:volunteer|community service|activities)\b',
            'interests': r'\b(?:interests|hobbies|activities|personal)\b',
            'references': r'\b(?:references|referees)\b'
        }
        
        # Define ideal section order
        self.ideal_order = STRUCTURE_IDEAL_ORDER
        
        # Define essential sections
        self.essential_sections = [k for k, v in STRUCTURE_ESSENTIALS.items() if v > 0]
    
    @ResumeEvaluator.timed_evaluation
    def evaluate(self, text: str) -> Dict[str, Any]:
        """
        Evaluate the structure of a resume.
        
        Args:
            text: The resume text to evaluate
            
        Returns:
            Dict containing score and detailed analysis
        """
        try:
            # Extract sections from the resume
            sections = self._extract_sections(text)
            
            # Analyze sections
            missing_sections = self._check_missing_sections(sections)
            section_order_penalty = self._check_section_order(sections)
            section_completeness = self._check_section_completeness(text, sections)
            formatting_consistency = self._check_formatting_consistency(text, sections)
            
            # Calculate penalties
            penalties = {
                'missing': sum(STRUCTURE_ESSENTIALS.get(section, 0) for section in missing_sections),
                'order': section_order_penalty,
                'completeness': STRUCTURE_PENALTIES['max_completeness_penalty'] - section_completeness,
                'formatting': STRUCTURE_PENALTIES['max_consistency_penalty'] - formatting_consistency
            }
            
            # Calculate final score
            max_penalty = sum([
                STRUCTURE_PENALTIES['max_missing_penalty'],
                STRUCTURE_PENALTIES['max_order_penalty'],
                STRUCTURE_PENALTIES['max_completeness_penalty'],
                STRUCTURE_PENALTIES['max_consistency_penalty']
            ])
            total_penalty = sum(penalties.values())
            # Cap the total penalty at the maximum
            total_penalty = min(total_penalty, max_penalty)
            score = max(0, min(100, 100 - (total_penalty * 100 / max_penalty)))
            
            return {
                "score": round(score, 1),
                "details": {
                    "sections_found": list(sections.keys()),
                    "missing_sections": missing_sections,
                    "section_order": self._get_order_details(sections),
                    "completeness_score": section_completeness,
                    "formatting_consistency_score": formatting_consistency,
                    "penalties": penalties
                }
            }
        except Exception as e:
            print(f"Error in structure evaluation: {e}")
            return {"score": 65, "details": {"error": str(e)}}
            
    def _extract_sections(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract sections from the resume text.
        
        Returns:
            Dict mapping section types to their details
        """
        lines = text.split('\n')
        sections = {}
        current_section = None
        section_headings = []
        
        # First pass: identify potential section headings
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if this line looks like a section heading
            if self._is_likely_heading(line):
                section_headings.append((i, line))
        
        # Second pass: determine section types and content
        for i, (line_index, heading) in enumerate(section_headings):
            section_type = self._identify_section_type(heading)
            if not section_type:
                continue
                
            # Determine section content (text between this heading and the next, or end)
            start_idx = line_index + 1
            end_idx = section_headings[i+1][0] if i+1 < len(section_headings) else len(lines)
            content = '\n'.join(lines[start_idx:end_idx]).strip()
            
            # Store section details
            sections[section_type] = {
                'heading': heading,
                'content': content,
                'line_index': line_index,
                'format': self._analyze_heading_format(heading)
            }
        
        return sections
    
    def _is_likely_heading(self, line: str) -> bool:
        """
        Determine if a line is likely to be a section heading.
        
        Checks for characteristics like:
        - All caps or title case
        - Short length
        - Ends with colon
        - Not indented (typically)
        """
        line = line.strip()
        if not line:
            return False
            
        # Check for common heading patterns
        if len(line) < 40 and (line.isupper() or line.istitle() or line.endswith(':')):
            return True
            
        # Check if line matches any section pattern
        for pattern in self.section_patterns.values():
            if re.search(pattern, line, re.IGNORECASE):
                return True
                
        return False
    
    def _identify_section_type(self, heading: str) -> str:
        """Identify section type from heading text."""
        heading_lower = heading.lower()
        
        for section_type, pattern in self.section_patterns.items():
            if re.search(pattern, heading_lower, re.IGNORECASE):
                return section_type
                
        return 'unknown'
    
    def _analyze_heading_format(self, heading: str) -> Dict[str, Any]:
        """Analyze the formatting of a section heading."""
        return {
            'case': 'upper' if heading.isupper() else 'title' if heading.istitle() else 'mixed',
            'ends_with_colon': heading.endswith(':'),
            'length': len(heading),
            'has_bullet': any(bullet in heading for bullet in ['•', '-', '*'])
        }
    
    def _check_missing_sections(self, sections: Dict[str, Dict[str, Any]]) -> List[str]:
        """Check for missing essential sections."""
        return [section for section in self.essential_sections if section not in sections]
    
    def _check_section_order(self, sections: Dict[str, Dict[str, Any]]) -> int:
        """
        Check if sections appear in a logical order.
        Returns a penalty score (0-15).
        """
        if not sections:
            return STRUCTURE_PENALTIES['max_order_penalty']
            
        # Create a map of actual section positions
        actual_order = {}
        for section_type, details in sections.items():
            actual_order[section_type] = details['line_index']
        
        # Sort sections by their line index
        sorted_sections = sorted(actual_order.items(), key=lambda x: x[1])
        actual_section_types = [s[0] for s in sorted_sections]
        
        # Calculate order violations
        violations = 0
        for i, section_type in enumerate(actual_section_types):
            ideal_idx = self._get_ideal_index(section_type)
            for j, other_type in enumerate(actual_section_types[i+1:], i+1):
                other_ideal_idx = self._get_ideal_index(other_type)
                if ideal_idx > other_ideal_idx:
                    violations += 1
        
        # Calculate penalty based on violations
        return min(STRUCTURE_PENALTIES['max_order_penalty'], violations * 5)
    
    def _get_ideal_index(self, section_type: str) -> int:
        """Get the ideal index for a section type."""
        try:
            return self.ideal_order.index(section_type)
        except ValueError:
            # For unknown section types, place them at the end
            return len(self.ideal_order)
    
    def _get_order_details(self, sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Get detailed information about section ordering."""
        if not sections:
            return {'status': 'no_sections'}
            
        # Create a map of actual section positions
        actual_order = {}
        for section_type, details in sections.items():
            actual_order[section_type] = details['line_index']
        
        # Sort sections by their line index
        sorted_sections = sorted(actual_order.items(), key=lambda x: x[1])
        actual_section_types = [s[0] for s in sorted_sections]
        
        # Find section order issues
        issues = []
        for i, section_type in enumerate(actual_section_types):
            ideal_idx = self._get_ideal_index(section_type)
            for j, other_type in enumerate(actual_section_types[i+1:], i+1):
                other_ideal_idx = self._get_ideal_index(other_type)
                if ideal_idx > other_ideal_idx:
                    issues.append({
                        'swap': f"{section_type} should come after {other_type}"
                    })
        
        return {
            'actual_order': actual_section_types,
            'ideal_order': [s for s in self.ideal_order if s in sections],
            'issues': issues
        }
    
    def _check_section_completeness(self, text: str, sections: Dict[str, Dict[str, Any]]) -> int:
        """
        Check if sections contain expected content.
        Returns a completeness score (0-30).
        """
        completeness_score = 0
        
        # Contact section checks
        if 'contact' in sections:
            contact_text = sections['contact']['content']
            has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', contact_text))
            has_phone = bool(re.search(r'[\d\-\+\(\)\s]{10,}', contact_text))
            
            completeness_score += 5 if has_email else 0
            completeness_score += 5 if has_phone else 0
        
        # Education section checks
        if 'education' in sections:
            education_text = sections['education']['content']
            has_degree = bool(re.search(r'\b(?:degree|bachelor|master|phd|diploma|certificate)\b', education_text, re.IGNORECASE))
            has_dates = bool(re.search(r'\b(?:19|20)\d{2}\b', education_text))
            
            completeness_score += 5 if has_degree else 0
            completeness_score += 2 if has_dates else 0
        
        # Experience section checks
        if 'experience' in sections:
            experience_text = sections['experience']['content']
            has_company = bool(re.search(r'[A-Z][a-z]+ (?:Inc|LLC|Ltd|Co|Corporation|Company)', experience_text))
            has_dates = bool(re.search(r'\b(?:19|20)\d{2}\b', experience_text))
            has_bullets = experience_text.count('\n') > 3 and any(line.strip().startswith(('•', '-', '*')) for line in experience_text.split('\n'))
            
            completeness_score += 3 if has_company else 0
            completeness_score += 2 if has_dates else 0
            completeness_score += 5 if has_bullets else 0
        
        # Skills section checks
        if 'skills' in sections:
            skills_text = sections['skills']['content']
            skills_count = len(re.findall(r'\b[A-Za-z][A-Za-z+#.]{2,}\b', skills_text))
            
            completeness_score += min(3, skills_count // 5)  # Up to 3 points based on skills count
        
        return completeness_score
    
    def _check_formatting_consistency(self, text: str, sections: Dict[str, Dict[str, Any]]) -> int:
        """
        Check for consistency in formatting across sections.
        Returns a consistency score (0-20).
        """
        if len(sections) < 2:
            return 0
            
        # Check heading format consistency
        heading_formats = [details['format'] for details in sections.values()]
        
        # Count distinct formats for various aspects
        case_formats = {fmt['case'] for fmt in heading_formats}
        colon_formats = {fmt['ends_with_colon'] for fmt in heading_formats}
        bullet_formats = {fmt['has_bullet'] for fmt in heading_formats}
        
        # Calculate consistency score
        consistency_score = 0
        consistency_score += 8 if len(case_formats) == 1 else 4 if len(case_formats) == 2 else 0
        consistency_score += 6 if len(colon_formats) == 1 else 3
        consistency_score += 6 if len(bullet_formats) == 1 else 3
        
        return consistency_score
