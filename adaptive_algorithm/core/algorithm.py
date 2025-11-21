"""Main adaptive learning algorithm implementation."""  
import numpy as np  
from typing import Dict, List, Tuple, Optional  
import logging
from adaptive_algorithm.models.schemas import  Content, StudentState, Topic, Observation  
from .scoring import ScoringComponents  
from .knowledge_tracing import BayesianKnowledgeTracing  
from adaptive_algorithm.config.settings import ALGORITHM_CONFIG
  
logger = logging.getLogger(__name__)

  
class AdaptiveLearningAlgorithm:  
    """  
    Multi-Objective Adaptive Learning Algorithm.
      
    Implements equation (18) from the paper:  
    C* = argmax[wls·LS + wd·D + wcl·CL + wkg·KG + we·Eng + β·√(ln(N)/Nc)]
      
    Subject to pedagogical constraints.  
    """
      
    def __init__(self, weights: Optional[Dict[str, float]] = None,  
                 zpd_delta: float = None, zpd_sigma: float = None,  
                 cl_optimal: float = None, cl_max: float = None,  
                 beta_0: float = None):  
        """  
        Initialize adaptive learning algorithm.
          
        Args:  
            weights: Component weights (must sum to 1.0)  
            zpd_delta: Zone of Proximal Development offset (δ)  
            zpd_sigma: ZPD width parameter (σ_zpd)  
            cl_optimal: Optimal cognitive load level  
            cl_max: Maximum cognitive load threshold  
            beta_0: Initial exploration parameter  
        """  
        # Load weights from config or use provided  
        self.weights = weights or ALGORITHM_CONFIG['weights']
          
        # Validate weights sum to 1  
        weight_sum = sum(self.weights.values())  
        if abs(weight_sum - 1.0) > 0.01:  
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")
          
        # Algorithm parameters  
        self.zpd_delta = zpd_delta or ALGORITHM_CONFIG['zpd_delta']  
        self.zpd_sigma = zpd_sigma or ALGORITHM_CONFIG['zpd_sigma']  
        self.cl_optimal = cl_optimal or ALGORITHM_CONFIG['cl_optimal']  
        self.cl_max = cl_max or ALGORITHM_CONFIG['cl_max']  
        self.beta_0 = beta_0 or ALGORITHM_CONFIG['beta_0']  
        self.mastery_threshold = ALGORITHM_CONFIG['mastery_threshold']
          
        # Initialize components  
        self.scoring = ScoringComponents()  
        self.bkt = BayesianKnowledgeTracing()
          
        # Tracking  
        self.time_step = 0
          
        logger.info(f"Algorithm initialized with weights: {self.weights}")
      
    def select_optimal_content(  
        self,  
        student: StudentState,  
        available_content: List[Content],  
        topics: Dict[str, Topic]  
    ) -> Tuple[Content, Dict[str, float]]:  
        """  
        Select optimal content for student (Equation 18).
          
        Args:  
            student: Current student state  
            available_content: List of available content  
            topics: Dictionary of topics
          
        Returns:  
            Tuple of (selected_content, component_scores)  
        """  
        # Filter eligible content based on constraints  
        eligible_content = self._filter_eligible_content(  
            available_content, student, topics  
        )
          
        if not eligible_content:  
            logger.warning(f"No eligible content for student {student.student_id}")  
            # Fallback: return easiest available content  
            return min(available_content, key=lambda c: c.difficulty), {}
          
        # Calculate overall knowledge level K(st)  
        topic_weights = {  
            tid: topics[tid].importance_weight  
            for tid in student.knowledge_state.keys()  
            if tid in topics  
        }  
        knowledge_level = self.bkt.estimate_knowledge_level(  
            student.knowledge_state, topic_weights  
        )
          
        # Score all eligible content  
        best_content = None  
        best_score = -np.inf  
        best_components = {}
          
        for content in eligible_content:  
            score, components = self._calculate_score(  
                content, student, knowledge_level  
            )
              
            if score > best_score:  
                best_score = score  
                best_content = content  
                best_components = components
          
        self.time_step += 1
          
        logger.info(  
            f"Selected content '{best_content.id}' with score {best_score:.3f} "  
            f"for student {student.student_id}"  
        )  
        logger.debug(f"Component scores: {best_components}")
          
        return best_content, best_components
      
    def _calculate_score(  
        self,  
        content: Content,  
        student: StudentState,  
        knowledge_level: float  
    ) -> Tuple[float, Dict[str, float]]:  
        """  
        Calculate total score for content (Equation 17).
          
        S(c,st,t) = Σ wi·fi(c,st,t) + E(c,st,t)  
        """  
        # Calculate each component  
        ls_score = self.scoring.learning_style_match(content, student)
          
        d_score = self.scoring.difficulty_appropriateness(  
            content, student, knowledge_level,  
            self.zpd_delta, self.zpd_sigma  
        )
          
        cl_score = self.scoring.cognitive_load_optimization(  
            content, student, self.cl_optimal  
        )
          
        kg_score = self.scoring.knowledge_gap_targeting(content, student)
          
        eng_score = self.scoring.engagement_prediction(content, student)
          
        e_bonus = self.scoring.exploration_bonus(  
            content, student.total_interactions,  
            self.beta_0, self.time_step  
        )
          
        # Weighted sum (Equation 5)  
        total_score = (  
            self.weights['learning_style'] * ls_score +  
            self.weights['difficulty'] * d_score +  
            self.weights['cognitive_load'] * cl_score +  
            self.weights['knowledge_gap'] * kg_score +  
            self.weights['engagement'] * eng_score +  
            e_bonus  
        )
          
        components = {  
            'learning_style': ls_score,  
            'difficulty': d_score,  
            'cognitive_load': cl_score,  
            'knowledge_gap': kg_score,  
            'engagement': eng_score,  
            'exploration': e_bonus,  
            'total': total_score  
        }
          
        return total_score, components
      
    def _filter_eligible_content(  
        self,  
        content_list: List[Content],  
        student: StudentState,  
        topics: Dict[str, Topic]  
    ) -> List[Content]:  
        """  
        Filter content based on pedagogical constraints.
          
        Constraints from equation (18):  
        1. Prerequisites(c) ⊆ Mastered(st)  
        2. D(c) ∈ ZPD(st)  
        3. CL_projected(c,st) < CL_max  
        """  
        eligible = []
          
        for content in content_list:  
            # Constraint 1: Check prerequisites  
            topic = topics.get(content.topic_id)  
            if topic and not self._prerequisites_met(topic, student):  
                continue
              
            # Constraint 2: Check ZPD  
            knowledge_level = student.knowledge_state.get(content.topic_id, 0.0)  
            if not self._in_zpd(content.difficulty, knowledge_level):  
                continue
              
            # Constraint 3: Check cognitive load  
            projected_load = self.scoring._estimate_projected_load(content, student)  
            if projected_load > self.cl_max:  
                continue
              
            eligible.append(content)
          
        return eligible
      
    def _prerequisites_met(self, topic: Topic, student: StudentState) -> bool:  
        """Check if all prerequisites are mastered."""  
        for prereq_id in topic.prerequisites:  
            mastery = student.knowledge_state.get(prereq_id, 0.0)  
            if mastery < self.mastery_threshold:  
                return False  
        return True
      
    def _in_zpd(self, difficulty: float, knowledge_level: float) -> bool:  
        """  
        Check if difficulty is within Zone of Proximal Development.
          
        ZPD range: [K(st) - margin, K(st) + δ + margin]  
        """  
        margin = 0.1  
        lower_bound = knowledge_level - margin  
        upper_bound = knowledge_level + self.zpd_delta + margin  
        return lower_bound <= difficulty <= upper_bound
      
    def update_student_state(  
        self,  
        student: StudentState,  
        observation: Observation,  
        content: Content  
    ) -> StudentState:  
        """  
        Update student state based on observation.
          
        Implements state transition function T(st, ot) -> st+1  
        Updates: Knowledge, Cognitive Load, Performance History  
        """  
        # Update knowledge state using BKT (Equations 9-11)  
        current_mastery = student.knowledge_state.get(observation.topic_id, 0.0)  
        new_mastery = self.bkt.update_mastery(current_mastery, observation.correct)  
        student.knowledge_state[observation.topic_id] = new_mastery
          
        # Update mastered topics  
        if new_mastery >= 0.8 and observation.topic_id not in student.mastered_topics:  
            student.mastered_topics.append(observation.topic_id)  
            logger.info(f"Student {student.student_id} mastered topic {observation.topic_id}")
          
        # Update performance history  
        performance_score = 1.0 if observation.correct else 0.0  
        student.recent_performance.append(performance_score)  
        if len(student.recent_performance) > 20:  
            student.recent_performance = student.recent_performance[-20:]
          
        # Update cognitive load (exponential decay + new load)  
        decay_factor = 0.8  
        student.current_cognitive_load = (  
            student.current_cognitive_load * decay_factor +  
            content.intrinsic_load * 0.2  
        )  
        student.current_cognitive_load = np.clip(  
            student.current_cognitive_load, 0.0, 1.0  
        )
          
        # Update engagement history  
        student.engagement_history.append(observation.engagement_score)  
        if len(student.engagement_history) > 20:  
            student.engagement_history = student.engagement_history[-20:]
          
        # Update interaction counts  
        student.total_interactions += 1
          
        logger.info(  
            f"Updated student {student.student_id}: "  
            f"Topic {observation.topic_id} mastery: {new_mastery:.3f}"  
        )
          
        return student
      
    def set_weights(self, weights: Dict[str, float]) -> None:  
        """Update algorithm weights (for A/B testing)."""  
        weight_sum = sum(weights.values())  
        if abs(weight_sum - 1.0) > 0.01:  
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")  
        self.weights = weights  
        logger.info(f"Updated weights: {weights}")  