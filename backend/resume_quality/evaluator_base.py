from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import re
import time
from functools import wraps

class ResumeEvaluator(ABC):
    """Base class for all resume quality evaluators."""
    
    @abstractmethod
    def evaluate(self, text: str) -> Dict[str, Any]:
        """
        Evaluate a specific quality aspect of the resume.
        
        Args:
            text: The resume text to evaluate
            
        Returns:
            Dict containing at minimum:
                - score: float between 0-100
                - details: Dict of additional information about the evaluation
        """
        pass
    
    def name(self) -> str:
        """Return the name of the evaluator (defaults to class name)."""
        return self.__class__.__name__
    
    def extract_bullet_points(self, text: str) -> List[str]:
        """
        Extract bullet points from resume text using common patterns.
        
        Args:
            text: The text to extract bullet points from
            
        Returns:
            List of bullet point strings
        """
        # Match common bullet point patterns
        bullet_pattern = r'(?:^|\n)[\s]*([•\-*>–])[\s]+(.*?)(?=\n[\s]*[•\-*>–][\s]+|\n\n|$)'
        bullets = [m.group(2).strip() for m in re.finditer(bullet_pattern, text, re.DOTALL)]
        
        # If no bullet points found, try to use sentences as fallback
        if not bullets:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            bullets = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return bullets
    
    def extract_section(self, text: str, 
                        section_headers: List[str], 
                        end_section_headers: Optional[List[str]] = None) -> str:
        """
        Extract a specific section from resume text.
        
        Args:
            text: The text to extract section from
            section_headers: List of possible section header keywords
            end_section_headers: List of headers that might indicate the end of the section
            
        Returns:
            Extracted section text or empty string if not found
        """
        if not end_section_headers:
            end_section_headers = ["education", "skills", "projects", "certifications", 
                                  "interests", "awards", "publications", "references"]
        
        section_start = None
        for header in section_headers:
            pattern = rf"\b{re.escape(header)}\b"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                section_start = match.start()
                break
        
        if section_start is None:
            return ""
        
        section_end = None
        for header in end_section_headers:
            if header in [h for h in section_headers if text[section_start:].lower().startswith(h.lower())]:
                continue
            
            pattern = rf"\b{re.escape(header)}\b"
            match = re.search(pattern, text[section_start:], re.IGNORECASE)
            if match:
                section_end = section_start + match.start()
                break
        
        section = text[section_start:section_end] if section_end else text[section_start:]
        return section.strip()
    
    def timed_evaluation(func):
        """Decorator to time evaluation methods and add timing to result details."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            result = func(self, *args, **kwargs)
            execution_time = time.time() - start_time
            
            if isinstance(result, dict) and 'details' in result:
                if isinstance(result['details'], dict):
                    result['details']['execution_time_ms'] = round(execution_time * 1000, 2)
            
            return result
        return wrapper
