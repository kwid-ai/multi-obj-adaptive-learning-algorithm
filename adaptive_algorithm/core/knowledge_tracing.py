"""Bayesian Knowledge Tracing implementation."""  
import numpy as np  
from typing import Dict

  
class BayesianKnowledgeTracing:  
    """  
    Implements Bayesian Knowledge Tracing for mastery estimation.
      
    Based on the paper's equations (9), (10), (11).  
    """
      
    def __init__(self, p_init: float = 0.0, p_learn: float = 0.3,  
                 p_slip: float = 0.1, p_guess: float = 0.2):  
        """  
        Initialize BKT parameters.
          
        Args:  
            p_init: Initial mastery probability  
            p_learn: Learning rate  
            p_slip: Slip probability (knows but gets wrong)  
            p_guess: Guess probability (doesn't know but gets right)  
        """  
        self.p_init = p_init  
        self.p_learn = p_learn  
        self.p_slip = p_slip  
        self.p_guess = p_guess
      
    def update_mastery(self, current_mastery: float, correct: bool) -> float:  
        """  
        Update mastery probability based on observation.
          
        Implements equations (9) and (10) from the paper.
          
        Args:  
            current_mastery: Current mastery probability P(M_t-1)  
            correct: Whether the answer was correct
          
        Returns:  
            Updated mastery probability P(M_t)  
        """  
        if correct:  
            # P(M_t | correct) - Equation (9)  
            numerator = (1 - self.p_slip) * current_mastery  
            denominator = numerator + self.p_guess * (1 - current_mastery)  
            p_mastery_given_obs = numerator / denominator if denominator > 0 else current_mastery  
        else:  
            # P(M_t | incorrect) - Equation (10)  
            numerator = self.p_slip * current_mastery  
            denominator = numerator + (1 - self.p_guess) * (1 - current_mastery)  
            p_mastery_given_obs = numerator / denominator if denominator > 0 else current_mastery
          
        # Update with learning - Equation (11)  
        updated_mastery = p_mastery_given_obs + (1 - p_mastery_given_obs) * self.p_learn
          
        return np.clip(updated_mastery, 0.0, 1.0)
      
    def estimate_knowledge_level(self, topic_masteries: Dict[str, float],  
                                 topic_weights: Dict[str, float]) -> float:  
        """  
        Estimate overall knowledge level across topics.
          
        Implements K(st) from equation (8).
          
        Args:  
            topic_masteries: Dict mapping topic_id to mastery probability  
            topic_weights: Dict mapping topic_id to importance weight
          
        Returns:  
            Overall knowledge level K(st)  
        """  
        if not topic_masteries:  
            return 0.0
          
        weighted_sum = sum(  
            topic_masteries.get(topic, 0.0) * weight  
            for topic, weight in topic_weights.items()  
        )  
        total_weight = sum(topic_weights.values())
          
        return weighted_sum / total_weight if total_weight > 0 else 0.0  