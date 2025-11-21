"""Scoring components for the adaptive algorithm."""  
import numpy as np  
from typing import Dict, Optional  
from adaptive_algorithm.models.schemas import Content, StudentState, ContentType, LearningStyle  
from .knowledge_tracing import BayesianKnowledgeTracing

  
class ScoringComponents:  
    """  
    Implements all scoring components from the paper.
      
    Corresponds to equations (6), (7), (12), (13), (14), (15).  
    """
      
    def __init__(self):  
        self.bkt = BayesianKnowledgeTracing()
          
        # Style-content affinity matrix M(type, style)  
        self.style_affinity = {  
            ContentType.VIDEO: {  
                LearningStyle.VISUAL: 1.0,  
                LearningStyle.AUDITORY: 0.8,  
                LearningStyle.KINESTHETIC: 0.3,  
                LearningStyle.READING_WRITING: 0.4  
            },  
            ContentType.TEXT: {  
                LearningStyle.VISUAL: 0.5,  
                LearningStyle.AUDITORY: 0.3,  
                LearningStyle.KINESTHETIC: 0.2,  
                LearningStyle.READING_WRITING: 1.0  
            },  
            ContentType.INTERACTIVE: {  
                LearningStyle.VISUAL: 0.7,  
                LearningStyle.AUDITORY: 0.5,  
                LearningStyle.KINESTHETIC: 1.0,  
                LearningStyle.READING_WRITING: 0.6  
            },  
            ContentType.QUIZ: {  
                LearningStyle.VISUAL: 0.6,  
                LearningStyle.AUDITORY: 0.4,  
                LearningStyle.KINESTHETIC: 0.7,  
                LearningStyle.READING_WRITING: 0.9  
            },  
            ContentType.CASE_STUDY: {  
                LearningStyle.VISUAL: 0.8,  
                LearningStyle.AUDITORY: 0.6,  
                LearningStyle.KINESTHETIC: 0.9,  
                LearningStyle.READING_WRITING: 0.8  
            }  
        }
      
    def learning_style_match(self, content: Content, student: StudentState) -> float:  
        """  
        Calculate learning style match score (LS).
          
        Implements equation (6) from the paper.
          
        Args:  
            content: Content item  
            student: Student state
          
        Returns:  
            Learning style match score [0, 1]  
        """  
        if not student.learning_style_preferences:  
            return 0.5
          
        affinity = self.style_affinity.get(content.content_type, {})
          
        score = sum(  
            affinity.get(style, 0.5) * prob  
            for style, prob in student.learning_style_preferences.items()  
        )
          
        total_prob = sum(student.learning_style_preferences.values())  
        return score / total_prob if total_prob > 0 else 0.5
      
    def difficulty_appropriateness(self, content: Content, student: StudentState,  
                                   knowledge_level: float, delta: float = 0.2,  
                                   sigma_zpd: float = 0.15) -> float:  
        """  
        Calculate difficulty appropriateness score (D).
          
        Implements equation (7) and (16) from the paper.  
        Uses Gaussian function centered at ZPD.
          
        Args:  
            content: Content item  
            student: Student state  
            knowledge_level: Current knowledge level K(st)  
            delta: Optimal challenge offset (ZPD parameter)  
            sigma_zpd: ZPD width parameter
          
        Returns:  
            Difficulty appropriateness score [0, 1]  
        """  
        # Center of ZPD: μ_zpd = K(st) + δ  
        mu_zpd = knowledge_level + delta
          
        # Gaussian function  
        exponent = -((content.difficulty - mu_zpd) ** 2) / (2 * sigma_zpd ** 2)  
        score = np.exp(exponent)
          
        return score
      
    def cognitive_load_optimization(self, content: Content, student: StudentState,  
                                   l_optimal: float = 0.7) -> float:  
        """  
        Calculate cognitive load optimization score (CL).
          
        Implements equation (12) from the paper.
          
        Args:  
            content: Content item  
            student: Student state  
            l_optimal: Optimal cognitive load level
          
        Returns:  
            Cognitive load optimization score [0, 1]  
        """  
        # Project cognitive load  
        l_projected = self._estimate_projected_load(content, student)
          
        # Score based on distance from optimal  
        score = 1 - abs(l_projected - l_optimal) / l_optimal
          
        return np.clip(score, 0.0, 1.0)
      
    def _estimate_projected_load(self, content: Content, student: StudentState) -> float:  
        """Estimate projected cognitive load."""  
        # Combine current load, content difficulty, and intrinsic load  
        base_load = content.intrinsic_load * content.difficulty
          
        # Adjust based on current state  
        fatigue_factor = min(student.current_cognitive_load * 0.3, 0.3)
          
        projected = base_load + fatigue_factor
          
        return np.clip(projected, 0.0, 1.0)
      
    def knowledge_gap_targeting(self, content: Content, student: StudentState,  
                               is_new_topic: bool = False) -> float:  
        """  
        Calculate knowledge gap targeting score (KG).
          
        Implements equation (13) from the paper.
          
        Args:  
            content: Content item  
            student: Student state  
            is_new_topic: Whether this is a new topic for the student
          
        Returns:  
            Knowledge gap targeting score [0, 1]  
        """  
        if is_new_topic:  
            return 0.5
          
        # Get mastery probability for this topic  
        mastery = student.knowledge_state.get(content.topic_id, 0.0)
          
        # Score is inverse of mastery (target weak areas)  
        score = 1 - mastery
          
        return score
      
    def engagement_prediction(self, content: Content, student: StudentState,  
                            features: Optional[Dict] = None) -> float:  
        """  
        Predict engagement score (Eng).
          
        Implements equation (14) from the paper.  
        In production, this would use a trained ML model.
          
        Args:  
            content: Content item  
            student: Student state  
            features: Optional pre-computed features
          
        Returns:  
            Predicted engagement score [0, 1]  
        """  
        if features is None:  
            features = self._extract_engagement_features(content, student)
          
        # Simple weighted model (replace with trained model in production)  
        weights = {  
            'style_match': 0.3,  
            'difficulty_match': 0.25,  
            'recent_performance': 0.2,  
            'content_variety': 0.15,  
            'time_of_day': 0.1  
        }
          
        score = sum(features.get(key, 0.5) * weight   
                   for key, weight in weights.items())
          
        # Apply sigmoid for 0-1 range  
        return self._sigmoid(score)
      
    def _extract_engagement_features(self, content: Content,  
                                    student: StudentState) -> Dict[str, float]:  
        """Extract features for engagement prediction."""  
        recent_perf = np.mean(student.recent_performance[-5:]) if student.recent_performance else 0.5
          
        return {  
            'style_match': self.learning_style_match(content, student),  
            'difficulty_match': 1 - abs(content.difficulty - 0.5),  
            'recent_performance': recent_perf,  
            'content_variety': 0.5,  
            'time_of_day': 0.7  
        }
      
    def exploration_bonus(self, content: Content, total_interactions: int,  
                         beta_0: float = 1.0, time_step: int = 1) -> float:  
        """  
        Calculate exploration bonus (E).
          
        Implements equation (15) from the paper.  
        Uses Upper Confidence Bound (UCB) approach.
          
        Args:  
            content: Content item  
            total_interactions: Total number of interactions N_t  
            beta_0: Initial exploration parameter  
            time_step: Current time step
          
        Returns:  
            Exploration bonus value  
        """  
        # Decay beta over time  
        beta_t = beta_0 / (1 + np.log(time_step + 1))
          
        # UCB formula  
        if content.interaction_count == 0:  
            return beta_t * np.sqrt(np.log(total_interactions + 1))
          
        bonus = beta_t * np.sqrt(  
            np.log(total_interactions + 1) / (content.interaction_count + 1)  
        )
          
        return bonus
      
    @staticmethod  
    def _sigmoid(x: float) -> float:  
        """Sigmoid activation function."""  
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))  