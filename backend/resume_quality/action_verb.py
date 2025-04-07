import re
import os
import json
from collections import defaultdict
from typing import Dict, Any, List, Set, Optional, Tuple
from .evaluator_base import ResumeEvaluator
from .config import ACTION_VERB_WEIGHTS

# Add SpaCy for NLP-based analysis
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

class ActionVerbEvaluator(ResumeEvaluator):
    """Evaluates the use of strong action verbs in resume bullet points."""
    
    DEFAULT_VERBS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'action_verbs.json')
    
    def __init__(self, custom_verbs_path: Optional[str] = None, nlp_model: str = "en_core_web_sm"):
        # Initialize verb collections
        self.strong_action_verbs = set()
        self.domain_specific_verbs = defaultdict(set)
        
        # Word patterns that often indicate the start of a bullet but aren't action verbs
        self.non_action_starters = {
            "responsible", "duties", "working", "helping", "assisting", 
            "supporting", "participating", "attending"
        }
        
        # Initialize NLP for contextual analysis
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(nlp_model)
                print(f"SpaCy NLP model '{nlp_model}' loaded successfully.")
            except Exception as e:
                print(f"Warning: Could not load SpaCy model '{nlp_model}': {e}")
                print("Falling back to basic text analysis.")
        else:
            print("SpaCy not available. Install with 'pip install spacy' and download models.")
            print("Falling back to basic text analysis.")
        
        # Load default verbs
        self._load_default_verbs()
        
        # Load custom verbs if path provided
        if custom_verbs_path:
            self.load_verbs_from_file(custom_verbs_path)
    
    def _load_default_verbs(self):
        """Load the default set of action verbs."""
        # First try to load from the external file
        try:
            if os.path.exists(self.DEFAULT_VERBS_PATH):
                self.load_verbs_from_file(self.DEFAULT_VERBS_PATH)
                return
        except Exception as e:
            print(f"Error loading default verbs from file: {e}")
        
        # Fallback to hardcoded list if file loading fails
    
    def load_verbs_from_file(self, file_path: str) -> bool:
        """
        Load action verbs from a JSON file.
        
        Expected format:
        {
            "general": ["achieved", "built", ...],
            "domains": {
                "technology": ["coded", "debugged", ...],
                "marketing": ["campaigned", "branded", ...]
            }
        }
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load general verbs
            if "general" in data and isinstance(data["general"], list):
                self.strong_action_verbs.update(set(verb.lower() for verb in data["general"]))
            
            # Load domain-specific verbs
            if "domains" in data and isinstance(data["domains"], dict):
                for domain, verbs in data["domains"].items():
                    if isinstance(verbs, list):
                        self.domain_specific_verbs[domain.lower()].update(
                            set(verb.lower() for verb in verbs)
                        )
                        # Also add domain verbs to general set for normal evaluation
                        self.strong_action_verbs.update(
                            set(verb.lower() for verb in verbs)
                        )
            return True
        except Exception as e:
            print(f"Error loading verbs from {file_path}: {e}")
            return False
    
    def add_custom_verbs(self, verbs: List[str], domain: Optional[str] = None) -> None:
        """
        Add custom action verbs to the evaluator.
        
        Args:
            verbs: List of verbs to add
            domain: Optional domain to categorize these verbs
        """
        lower_verbs = set(verb.lower() for verb in verbs)
        self.strong_action_verbs.update(lower_verbs)
        
        if domain:
            self.domain_specific_verbs[domain.lower()].update(lower_verbs)
    
    def get_domain_strength(self, text: str, domain: str) -> Dict[str, Any]:
        """
        Evaluate the use of domain-specific action verbs.
        
        Args:
            text: The resume text
            domain: The domain to evaluate against
            
        Returns:
            Dict with domain-specific evaluation
        """
        domain = domain.lower()
        if domain not in self.domain_specific_verbs:
            return {"domain_match": 0, "verbs_used": []}
        
        bullets = self.extract_bullet_points(text)
        domain_verbs_used = []
        
        for bullet in bullets:
            cleaned_bullet = re.sub(r'^\s*[•\-*>]?\s*', '', bullet).strip()
            words = re.findall(r'\b[a-zA-Z]+\b', cleaned_bullet)
            
            if words and words[0].lower() in self.domain_specific_verbs[domain]:
                domain_verbs_used.append(words[0].lower())
        
        return {
            "domain_match": len(domain_verbs_used) / max(1, len(bullets)) * 100,
            "verbs_used": domain_verbs_used
        }
    
    def extract_verb_context(self, text: str) -> Dict[str, Any]:
        """
        Extract the main verb and its context using NLP.
        
        Args:
            text: A sentence or bullet point text
            
        Returns:
            Dict with verb information and context
        """
        # Clean the bullet text
        cleaned_text = re.sub(r'^\s*[•\-*>]?\s*', '', text).strip()
        
        if not self.nlp:
            # Fallback to simple extraction if SpaCy is not available
            words = re.findall(r'\b[a-zA-Z]+\b', cleaned_text)
            if not words:
                return {"has_verb": False}
                
            first_word = words[0].lower()
            return {
                "has_verb": True,
                "verb": first_word,
                "is_strong": first_word in self.strong_action_verbs,
                "is_weak_starter": first_word in self.non_action_starters,
                "is_first_word": True,
                "context_score": 0.5  # Neutral context score without NLP
            }
        
        # Use SpaCy for advanced analysis
        doc = self.nlp(cleaned_text)
        
        # Find all verbs in the sentence
        verbs = []
        for token in doc:
            if token.pos_ == "VERB":
                is_main = token.dep_ == "ROOT"
                verb_obj = {
                    "text": token.lemma_.lower(),
                    "original": token.text.lower(),
                    "is_first_word": token.i == 0,
                    "is_main": is_main,
                    "position": token.i,
                    "has_object": any(child.dep_ in ("dobj", "pobj") for child in token.children),
                    "has_quantifier": any(child.dep_ in ("nummod", "quantmod") for child in token.children),
                    "token": token
                }
                verbs.append(verb_obj)
        
        if not verbs:
            return {"has_verb": False}
        
        # Prioritize main verb, then first verb
        main_verbs = [v for v in verbs if v["is_main"]]
        target_verb = main_verbs[0] if main_verbs else verbs[0]
        
        # Calculate contextual score based on verb usage
        context_score = 0.5  # Start with neutral score
        
        # Increase score for verbs with direct objects (more concrete actions)
        if target_verb["has_object"]:
            context_score += 0.25
            
        # Increase score for quantified achievements
        if target_verb["has_quantifier"]:
            context_score += 0.25
            
        # Check if the verb is in our strong verb list
        is_strong = target_verb["text"] in self.strong_action_verbs or target_verb["original"] in self.strong_action_verbs
            
        return {
            "has_verb": True,
            "verb": target_verb["text"],
            "original_verb": target_verb["original"],
            "is_strong": is_strong,
            "is_weak_starter": target_verb["text"] in self.non_action_starters,
            "is_first_word": target_verb["is_first_word"],
            "is_main_verb": target_verb["is_main"],
            "has_object": target_verb["has_object"],
            "context_score": context_score
        }
    
    @ResumeEvaluator.timed_evaluation
    def evaluate(self, text: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate the use of action verbs in resume bullet points.
        
        Args:
            text: The resume text to evaluate
            domain: Optional domain to evaluate against
            
        Returns:
            Dict with evaluation score and details
        """
        try:
            # Extract bullets from the text using the base class method
            bullets = self.extract_bullet_points(text)
            
            # Also try to extract specifically from experience section for better results
            experience_section = self.extract_section(
                text, 
                ["experience", "employment", "work history", "professional background"]
            )
            
            if experience_section:
                experience_bullets = self.extract_bullet_points(experience_section)
                # If we found bullets in the experience section, prioritize those
                if experience_bullets:
                    bullets = experience_bullets
            
            action_verbs_used = []
            action_context_scores = []
            non_action_count = 0
            weak_verbs = []
            non_first_word_verbs = 0
            
            for bullet in bullets:
                if not bullet.strip():
                    non_action_count += 1
                    continue
                
                # Get verb context using NLP
                context = self.extract_verb_context(bullet)
                
                if not context["has_verb"]:
                    non_action_count += 1
                    continue
                
                if context["is_strong"]:
                    action_verbs_used.append(context["verb"])
                    action_context_scores.append(context["context_score"])
                    
                    # Track verbs that aren't the first word
                    if not context["is_first_word"]:
                        non_first_word_verbs += 1
                elif context["is_weak_starter"]:
                    non_action_count += 1
                    weak_verbs.append(context["verb"])
                else:
                    non_action_count += 1
                    # Only add to weak verbs list if it's a verb that could be improved
                    if context["verb"].endswith('ed') or context["verb"].endswith('ing'):
                        weak_verbs.append(context["verb"])
            
            # Calculate duplicate penalties
            verb_counts = defaultdict(int)
            for verb in action_verbs_used:
                verb_counts[verb] += 1
            duplicates = sum(count - 1 for count in verb_counts.values())
            
            # Calculate context quality (average of all context scores)
            avg_context_score = sum(action_context_scores) / max(1, len(action_context_scores))
            
            # Calculate score components
            action_reward = len(action_verbs_used) * ACTION_VERB_WEIGHTS['action_reward']
            non_action_penalty = non_action_count * ACTION_VERB_WEIGHTS['non_action_penalty']
            duplicate_penalty = duplicates * ACTION_VERB_WEIGHTS['duplicate_penalty']
            
            # Add context bonus (scale from -10 to +10 points)
            context_bonus = (avg_context_score - 0.5) * 20
            
            raw_score = action_reward - non_action_penalty - duplicate_penalty + context_bonus
            
            # Normalize score to 0-100 range
            bullet_count = len(bullets) or 1  # Avoid division by zero
            normalized_score = min(100, max(0, 50 + (raw_score * 100 / (bullet_count * 2))))
            
            result = {
                "score": round(normalized_score, 1),
                "details": {
                    "bullets_count": len(bullets),
                    "action_verbs_count": len(action_verbs_used),
                    "non_action_count": non_action_count,
                    "duplicate_count": duplicates,
                    "non_first_word_verbs": non_first_word_verbs,
                    "context_quality": round(avg_context_score, 2),
                    "action_verbs_used": dict(verb_counts),
                    "weak_verbs": list(set(weak_verbs))[:10],  # Show only top weak verbs
                    "components": {
                        "action_reward": action_reward,
                        "non_action_penalty": non_action_penalty,
                        "duplicate_penalty": duplicate_penalty,
                        "context_bonus": round(context_bonus, 1)
                    }
                }
            }
            
            # Add domain-specific evaluation if a domain was specified
            if domain and domain in self.domain_specific_verbs:
                domain_results = self.get_domain_strength(text, domain)
                result["details"]["domain_specific"] = domain_results
            
            return result
        except Exception as e:
            print(f"Error in action verb evaluation: {e}")
            return {"score": 60, "details": {"error": str(e)}}