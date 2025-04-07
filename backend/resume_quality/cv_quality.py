import time
import logging
from functools import lru_cache
import hashlib
from backend.utils.spacy_model import nlp
from typing import Dict, Any,Optional
from .grammar_spelling import GrammarSpellingEvaluator
from .readability import ReadabilityEvaluator
from .format import FormattingEvaluator
from .tense_timeline import TenseTimelineEvaluator
from .action_verb import ActionVerbEvaluator
from .structure import StructureEvaluator  # Add the new evaluator
from .config import CV_QUALITY_COMPONENT_WEIGHTS

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cv_quality')

class CVQualityEvaluator:
    """Main evaluator that integrates all resume quality components."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the evaluator with component evaluators.
        
        Args:
            weights: Optional dictionary to override default component weights
        """
        self.evaluators = {
            'grammar': GrammarSpellingEvaluator(),
            'readability': ReadabilityEvaluator(),
            'formatting': FormattingEvaluator(),
            'timeline': TenseTimelineEvaluator(),
            'action_verbs': ActionVerbEvaluator(),
            'structure': StructureEvaluator()  # Add the new evaluator
        }
        
        self.weights = weights or CV_QUALITY_COMPONENT_WEIGHTS.copy()
        logger.info(f"Initialized CV quality evaluator with weights: {self.weights}")
        
        # Cache to avoid re-evaluating the same text
        self._evaluation_cache = {}
    
    def _get_cache_key(self, text: str) -> str:
        """Generate a cache key from text content."""
        return hashlib.md5(text.encode()).hexdigest()
    
    @lru_cache(maxsize=100)
    def evaluate(self, text: str) -> Dict[str, Any]:
        """
        Evaluate the overall quality of a CV/resume.
        
        Args:
            text: The full text of the resume
            
        Returns:
            Dict containing overall score and component scores
        """
        # Check cache
        cache_key = self._get_cache_key(text)
        if cache_key in self._evaluation_cache:
            logger.info(f"Using cached evaluation for {cache_key[:8]}...")
            return self._evaluation_cache[cache_key]
        
        logger.info(f"Evaluating resume quality (length: {len(text)} chars)")
        
        results = {}
        component_errors = {}
        
        # Run each evaluator with proper error handling
        for name, evaluator in self.evaluators.items():
            try:
                logger.debug(f"Running {name} evaluator")
                start_time = time.time()
                results[name] = evaluator.evaluate(text)
                elapsed = time.time() - start_time
                logger.debug(f"{name} evaluation completed in {elapsed:.2f}s")
            except Exception as e:
                logger.error(f"Error in {name} evaluation: {str(e)}", exc_info=True)
                component_errors[name] = str(e)
                # Provide default scores if evaluator fails
                results[name] = {"score": 60, "details": {"error": str(e)}}
        
        # Calculate weighted final score with safeguards
        weighted_scores = []
        total_weight = 0
        
        for component, weight in self.weights.items():
            if component in results:
                score = results[component]["score"]
                # Ensure score is within valid range
                score = max(0, min(100, score))
                weighted_scores.append(score * weight)
                total_weight += weight
        
        # Prevent division by zero
        if total_weight == 0:
            logger.warning("No valid components to evaluate, using default score")
            final_score = 60.0
        else:
            final_score = sum(weighted_scores) / total_weight
            
        final_score = round(final_score, 1)
        
        # Create component scores for the return value
        component_scores = {
            name: results[name]["score"] 
            for name in self.evaluators.keys()
            if name in results
        }
        
        result = {
            "final_score": final_score,
            "component_scores": component_scores,
            "details": {
                name: results[name]["details"]
                for name in self.evaluators.keys() 
                if name in results
            },
            "errors": component_errors if component_errors else None
        }
        
        # Store in cache
        self._evaluation_cache[cache_key] = result
        logger.info(f"Evaluation complete. Final score: {final_score}")
        
        return result

# Convenience function
def evaluate_cv_quality(resume_text: str) -> Dict[str, Any]:
    """
    Convenience function to evaluate CV quality.
    
    Args:
        resume_text: The full text of the resume
        
    Returns:
        Dict containing overall score and component scores
    """
    evaluator = CVQualityEvaluator()
    return evaluator.evaluate(resume_text)