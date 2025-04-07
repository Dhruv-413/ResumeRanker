import language_tool_python
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Any
from functools import lru_cache
import threading
from .evaluator_base import ResumeEvaluator
from .config import (
    GRAMMAR_BASE_SCORE, GRAMMAR_MIN_SCORE, GRAMMAR_MAX_SCORE, GRAMMAR_LENGTH_NORMALIZATION,
    GRAMMAR_ERROR_WEIGHTS, GRAMMAR_DENSITY_THRESHOLDS, GRAMMAR_PROXIMITY_PENALTY, GRAMMAR_CATEGORY_RULES
)

# Thread-local storage for LanguageTool instances
_thread_local = threading.local()

class GrammarSpellingEvaluator(ResumeEvaluator):
    """Evaluates grammar and spelling quality of a resume."""
    
    def __init__(self):
        """Initialize the evaluator with necessary tools."""
        # LanguageTool will be initialized per thread when needed
        self.tool_lock = threading.Lock()
    
    def _get_language_tool(self):
        """Get or create a thread-local LanguageTool instance."""
        if not hasattr(_thread_local, 'language_tool'):
            with self.tool_lock:  # Lock during initialization only
                if not hasattr(_thread_local, 'language_tool'):
                    _thread_local.language_tool = language_tool_python.LanguageTool('en-US')
        return _thread_local.language_tool
    
    @lru_cache(maxsize=50)  # Cache results for performance
    def _check_text(self, text: str) -> List[Any]:
        """Check text for grammar issues with caching."""
        return self._get_language_tool().check(text)
    
    @ResumeEvaluator.timed_evaluation
    def evaluate(self, text: str) -> Dict[str, Any]:
        """
        Evaluate grammar and spelling quality of the resume text.
        
        Args:
            text: The resume text to evaluate
            
        Returns:
            Dict containing score and detailed analysis
        """
        try:
            # Chunk the text for better performance with long resumes
            chunks = self._chunk_text(text, max_length=5000)
            all_matches = []
            
            for chunk in chunks:
                matches = self._check_text(chunk)
                
                # Adjust offsets for chunks after the first
                if chunk != chunks[0]:
                    start_pos = text.find(chunk)
                    for match in matches:
                        match.offset += start_pos
                        match.errorLength = min(match.errorLength, len(chunk) - match.offset + start_pos)
                
                all_matches.extend(matches)
            
            # Basic text analysis
            sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
            word_count = len(re.findall(r'\w+', text))
            sentence_count = max(len(sentences), 1)
            
            # Error analysis
            error_counts, error_positions, detailed_errors = self._categorize_errors(all_matches)
            
            # Calculate penalties
            weighted_penalty = self._calculate_weighted_penalty(error_counts)
            density_penalty = self._calculate_density_penalty(error_counts, sentence_count)
            proximity_penalty = self._calculate_proximity_penalty(error_positions)
            
            # Final score calculation - Modified to be more sensitive to errors
            length_factor = min(1.0, max(0.5, word_count / GRAMMAR_LENGTH_NORMALIZATION))
            total_errors = sum(error_counts.values())
            
            # Apply additional penalty for spelling errors specifically
            spelling_penalty = error_counts.get('spelling', 0) * 1.5
            
            # Modified score calculation to be more sensitive to errors
            raw_score = GRAMMAR_BASE_SCORE - ((weighted_penalty * 2.0) + density_penalty + proximity_penalty + spelling_penalty) * length_factor
            
            # Apply minimum penalty based on errors detected
            if total_errors > 0:
                min_error_penalty = min(15, total_errors * 2)
                raw_score = min(raw_score, GRAMMAR_BASE_SCORE - min_error_penalty)
                
            score = self._clamp_score(raw_score)
            
            return {
                "score": score,
                "details": {
                    "error_counts": dict(error_counts),
                    "total_errors": total_errors,
                    "word_count": word_count,
                    "sentence_count": sentence_count,
                    "error_ratio": round(sum(error_counts.values()) / max(1, word_count/100), 2),  # Errors per 100 words
                    "penalties": {
                        "weighted": weighted_penalty,
                        "density": density_penalty,
                        "proximity": proximity_penalty,
                        "spelling": spelling_penalty
                    },
                    "error_examples": self._get_error_examples(detailed_errors)
                }
            }
        except Exception as e:
            print(f"Error in grammar evaluation: {e}")
            return {"score": 50, "details": {"error": str(e)}}  # Lower default fallback score
    
    def _chunk_text(self, text: str, max_length: int = 5000) -> List[str]:
        """Split text into manageable chunks for processing."""
        if len(text) <= max_length:
            return [text]
        
        # Try to split at paragraph boundaries
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                if len(para) > max_length:
                    # If paragraph is too long, split it at sentence boundaries
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_chunk = ""
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 <= max_length:
                            current_chunk += sentence + ' '
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + ' '
                else:
                    current_chunk = para + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _categorize_errors(self, matches) -> Tuple[Dict[str, int], List[int], List[Dict]]:
        """
        Categorize grammar and spelling errors.
        
        Returns:
            Tuple containing: 
            - Error counts by category
            - List of error positions
            - Detailed error information
        """
        error_counts = defaultdict(int)
        error_positions = []
        detailed_errors = []
        
        for match in matches:
            category = 'other'
            msg = match.message.lower()
            rule = match.ruleId.lower()
            
            # Explicitly check for spelling errors first
            if 'spell' in rule or 'typo' in rule or 'misspell' in msg or 'unknown word' in msg:
                category = 'spelling'
            else:
                # Find matching category
                for cat, keywords in GRAMMAR_CATEGORY_RULES.items():
                    if any(kw in msg or kw in rule for kw in keywords):
                        category = cat
                        break
                    
            error_counts[category] += 1
            error_positions.append(match.offset)
            
            # Store detailed error info for examples
            detailed_errors.append({
                'category': category,
                'message': match.message,
                'rule': match.ruleId,  # Added rule ID for better diagnostics
                'context': match.context,
                'suggestions': match.replacements[:3] if match.replacements else [],
                'offset': match.offset
            })
        
        return error_counts, error_positions, detailed_errors
    
    def _calculate_weighted_penalty(self, error_counts: Dict[str, int]) -> float:
        """Calculate weighted penalty based on error types."""
        # Ensure spelling errors get appropriate weight if not defined in config
        weights = dict(GRAMMAR_ERROR_WEIGHTS)
        if 'spelling' not in weights:
            weights['spelling'] = 2.0  # Higher weight for spelling errors
            
        return sum(
            count * weights.get(cat, 1.5)  # Default weight increased from 1.0 to 1.5
            for cat, count in error_counts.items()
        )
    
    def _calculate_density_penalty(self, error_counts: Dict[str, int], sentence_count: int) -> float:
        """Calculate penalty based on error density per sentence."""
        total_errors = sum(error_counts.values())
        error_density = total_errors / max(sentence_count, 1)
        excess_density = max(0, error_density - GRAMMAR_DENSITY_THRESHOLDS['max_errors_per_sentence'])
        
        return min(
            GRAMMAR_DENSITY_THRESHOLDS['max_density_penalty'],
            excess_density * GRAMMAR_DENSITY_THRESHOLDS['penalty_per_excess']
        )
    
    def _calculate_proximity_penalty(self, error_positions: List[int]) -> float:
        """Calculate penalty based on proximity of errors (clustered errors)."""
        if len(error_positions) < 2:
            return 0
        
        error_positions.sort()
        total_distance = 0
        for i in range(1, len(error_positions)):
            total_distance += max(1, abs(error_positions[i] - error_positions[i-1]))
        
        avg_distance = total_distance / (len(error_positions) - 1)
        
        if avg_distance < GRAMMAR_PROXIMITY_PENALTY['critical_distance']:
            penalty = (GRAMMAR_PROXIMITY_PENALTY['critical_distance'] - avg_distance) \
                    * GRAMMAR_PROXIMITY_PENALTY['penalty_factor']
            return min(penalty, GRAMMAR_PROXIMITY_PENALTY['max_penalty'])
        return 0
    
    def _get_error_examples(self, detailed_errors: List[Dict]) -> Dict[str, List[Dict]]:
        """Get representative examples of each error category."""
        examples = defaultdict(list)
        for error in detailed_errors:
            category = error['category']
            if len(examples[category]) < 3:  # Limit to 3 examples per category
                examples[category].append({
                    'message': error['message'],
                    'suggestions': error['suggestions']
                })
        return dict(examples)
    
    def _clamp_score(self, score: float) -> float:
        """Ensure score stays within valid range."""
        return max(GRAMMAR_MIN_SCORE, min(GRAMMAR_MAX_SCORE, round(score, 1)))
