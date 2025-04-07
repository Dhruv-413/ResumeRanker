import textstat
from typing import Dict, Any
from .evaluator_base import ResumeEvaluator
from .config import READABILITY_WEIGHTS, READABILITY_THRESHOLDS, READABILITY_PENALTIES

class ReadabilityEvaluator(ResumeEvaluator):
    """Evaluates the readability of resume text."""
    
    def evaluate(self, text: str) -> Dict[str, Any]:
        try:
            # Calculate all readability scores
            scores = {
                'flesch_ease': textstat.flesch_reading_ease(text),
                'gunning_fog': textstat.gunning_fog(text),
                'smog': textstat.smog_index(text),
                'coleman_liau': textstat.coleman_liau_index(text),
                'dale_chall': textstat.dale_chall_readability_score(text)
            }

            # Normalize scores to 0-100 scale where 100 is best
            normalized = {
                'flesch_ease': max(0, min(scores['flesch_ease'], 100)),
                'gunning_fog': (20 - min(scores['gunning_fog'], 20)) * 5,
                'smog': (20 - min(scores['smog'], 20)) * 5,
                'coleman_liau': (20 - min(scores['coleman_liau'], 20)) * 5,
                'dale_chall': (10 - max(min(scores['dale_chall'], 10), 4)) * (100/6)
            }

            # Calculate composite score
            composite = sum(normalized[metric] * weight 
                        for metric, weight in READABILITY_WEIGHTS.items())
            composite = max(0, min(composite, 100))

            # Determine penalty category and points
            category = next(
                (cat for cat, (low, high) in READABILITY_THRESHOLDS.items() 
                if low <= composite <= high),
                'acceptable'
            )
            penalty = READABILITY_PENALTIES[category]
            final_score = max(0, min(100, 100 - penalty))

            return {
                "score": final_score,
                "details": {
                    "raw_scores": scores,
                    "normalized_scores": normalized,
                    "composite_score": composite,
                    "category": category,
                    "penalty": penalty
                }
            }
        except Exception as e:
            print(f"Error in readability evaluation: {e}")
            return {"score": 70, "details": {"error": str(e)}}  # Default fallback score
