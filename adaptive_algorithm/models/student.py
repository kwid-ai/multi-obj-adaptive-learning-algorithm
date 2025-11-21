"""  
Student model representing learner state.
  
Based on the paper's student model (st) which includes:  
- Knowledge state: P(mastery) for each topic (Equations 8-11)  
- Learning style preferences: Used in LS(c,st) (Equation 6)  
- Cognitive load: Used in CL(c,st) (Equation 12)  
- Performance history: Used for engagement prediction (Equation 14)  
"""
  
from dataclasses import dataclass, field  
from typing import Dict, List, Optional  
from datetime import datetime  
from enum import Enum  
import numpy as np

  
class LearningStyle(Enum):  
    """  
    Learning style preferences based on VARK model.
      
    Used in Learning Style Match calculation (Equation 6):  
    LS(c,st) = Σ M(type(c), style_j) · P(style_j | st)  
    """  
    VISUAL = "visual"  
    AUDITORY = "auditory"  
    KINESTHETIC = "kinesthetic"  
    READING_WRITING = "reading_writing"

  
@dataclass  
class StudentState:  
    """  
    Represents the current state of a student (st in the paper).
      
    This is the core learner model that gets updated after each interaction  
    via the state transition function T(st, ot) -> st+1.
      
    Attributes:  
        student_id: Unique identifier  
        knowledge_state: P(mastery_topic) for each topic (Equation 8)  
        learning_style_preferences: P(style_j | st) for each style (Equation 6)  
        current_cognitive_load: L_current for CL calculation (Equation 12)  
        recent_performance: Recent correctness for engagement (Equation 14)  
        mastered_topics: Topics with P(mastery) >= threshold  
        total_interactions: Nt in exploration bonus (Equation 15)  
        engagement_history: Historical engagement scores  
    """
      
    student_id: str
      
    # Knowledge state: topic_id -> P(mastery)  
    # Updated via BKT (Equations 9-11)  
    knowledge_state: Dict[str, float] = field(default_factory=dict)
      
    # Learning style preferences: style -> probability  
    # Used in LS(c,st) calculation (Equation 6)  
    learning_style_preferences: Dict[LearningStyle, float] = field(default_factory=dict)
      
    # Cognitive load state  
    # Used in CL(c,st) calculation (Equation 12)  
    current_cognitive_load: float = 0.0
      
    # Performance tracking  
    recent_performance: List[float] = field(default_factory=list)  
    mastered_topics: List[str] = field(default_factory=list)
      
    # Interaction tracking  
    total_interactions: int = 0  # Nt in Equation 15
      
    # Engagement tracking  
    engagement_history: List[float] = field(default_factory=list)
      
    # Timestamps  
    created_at: Optional[datetime] = None  
    updated_at: Optional[datetime] = None
      
    # Additional metadata  
    metadata: Dict = field(default_factory=dict)
      
    def __post_init__(self):  
        """Validate student state."""  
        # Validate learning style preferences sum to 1.0  
        if self.learning_style_preferences:  
            total = sum(self.learning_style_preferences.values())  
            if abs(total - 1.0) > 0.01:  
                raise ValueError(  
                    f"Learning style preferences must sum to 1.0, got {total}"  
                )  
        else:  
            # Initialize with uniform distribution  
            self.learning_style_preferences = {  
                LearningStyle.VISUAL: 0.25,  
                LearningStyle.AUDITORY: 0.25,  
                LearningStyle.KINESTHETIC: 0.25,  
                LearningStyle.READING_WRITING: 0.25  
            }
          
        # Validate cognitive load  
        if not 0 <= self.current_cognitive_load <= 1:  
            raise ValueError(  
                f"Cognitive load must be in [0, 1], got {self.current_cognitive_load}"  
            )
          
        # Validate knowledge state probabilities  
        for topic_id, mastery in self.knowledge_state.items():  
            if not 0 <= mastery <= 1:  
                raise ValueError(  
                    f"Mastery probability for {topic_id} must be in [0, 1], got {mastery}"  
                )
      
    def get_overall_knowledge_level(  
        self,  
        topic_weights: Dict[str, float]  
    ) -> float:  
        """  
        Calculate overall knowledge level K(st).
          
        Implements Equation (8):  
        K(st) = Σ wj · P(mastery_j)
          
        Args:  
            topic_weights: Importance weight for each topic
          
        Returns:  
            Overall knowledge level [0, 1]  
        """  
        if not self.knowledge_state:  
            return 0.0
          
        weighted_sum = sum(  
            self.knowledge_state.get(topic, 0.0) * weight  
            for topic, weight in topic_weights.items()  
        )  
        total_weight = sum(topic_weights.values())
          
        return weighted_sum / total_weight if total_weight > 0 else 0.0
      
    def get_topic_mastery(self, topic_id: str) -> float:  
        """Get mastery probability for a specific topic."""  
        return self.knowledge_state.get(topic_id, 0.0)
      
    def is_topic_mastered(self, topic_id: str, threshold: float = 0.7) -> bool:  
        """Check if topic is mastered (for prerequisite checking)."""  
        return self.get_topic_mastery(topic_id) >= threshold
      
    def get_average_performance(self, window: int = 10) -> float:  
        """Get average performance over recent window."""  
        if not self.recent_performance:  
            return 0.5
          
        recent = self.recent_performance[-window:]  
        return np.mean(recent)
      
    def get_average_engagement(self, window: int = 10) -> float:  
        """Get average engagement over recent window."""  
        if not self.engagement_history:  
            return 0.5
          
        recent = self.engagement_history[-window:]  
        return np.mean(recent)
      
    def get_learning_velocity(self) -> float:  
        """  
        Calculate learning velocity (rate of improvement).
          
        Returns:  
            Slope of performance trend (positive = improving)  
        """  
        if len(self.recent_performance) < 2:  
            return 0.0
          
        x = np.arange(len(self.recent_performance))  
        y = np.array(self.recent_performance)
          
        # Linear regression slope  
        slope = np.polyfit(x, y, 1)[0]
          
        return float(slope)
      
    def get_dominant_learning_style(self) -> LearningStyle:  
        """Get the dominant learning style."""  
        if not self.learning_style_preferences:  
            return LearningStyle.VISUAL
          
        return max(  
            self.learning_style_preferences.items(),  
            key=lambda x: x[1]  
        )[0]
      
    def update_cognitive_load(  
        self,  
        new_load: float,  
        decay_factor: float = 0.8  
    ) -> None:  
        """  
        Update cognitive load with exponential decay.
          
        L_current(t+1) = decay_factor · L_current(t) + (1 - decay_factor) · L_new
          
        Args:  
            new_load: New cognitive load from content  
            decay_factor: Decay rate for previous load  
        """  
        self.current_cognitive_load = (  
            decay_factor * self.current_cognitive_load +  
            (1 - decay_factor) * new_load  
        )  
        self.current_cognitive_load = np.clip(self.current_cognitive_load, 0.0, 1.0)
      
    def to_dict(self) -> Dict:  
        """Convert to dictionary representation."""  
        return {  
            'student_id': self.student_id,  
            'knowledge_state': self.knowledge_state,  
            'learning_style_preferences': {  
                k.value: v for k, v in self.learning_style_preferences.items()  
            },  
            'current_cognitive_load': self.current_cognitive_load,  
            'recent_performance': self.recent_performance,  
            'mastered_topics': self.mastered_topics,  
            'total_interactions': self.total_interactions,  
            'engagement_history': self.engagement_history,  
            'created_at': self.created_at.isoformat() if self.created_at else None,  
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,  
            'metadata': self.metadata  
        }
      
    @classmethod  
    def from_dict(cls, data: Dict) -> 'StudentState':  
        """Create StudentState from dictionary."""  
        # Convert learning style strings to enums  
        if 'learning_style_preferences' in data:  
            data['learning_style_preferences'] = {  
                LearningStyle(k): v  
                for k, v in data['learning_style_preferences'].items()  
            }
          
        # Convert datetime strings  
        if 'created_at' in data and isinstance(data['created_at'], str):  
            data['created_at'] = datetime.fromisoformat(data['created_at'])  
        if 'updated_at' in data and isinstance(data['updated_at'], str):  
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
          
        return cls(**data)

  
@dataclass  
class Observation:  
    """  
    Represents an observation from student interaction (ot in the paper).
      
    Used to update student state via BKT (Equations 9-11) and  
    other state transition functions.  
    """
      
    content_id: str  
    topic_id: str  
    correct: bool  # Used in BKT update (Equations 9-10)  
    time_spent: int  # Time in seconds  
    engagement_score: float  # [0, 1]  
    timestamp: datetime = field(default_factory=datetime.now)
      
    # Additional metadata  
    metadata: Dict = field(default_factory=dict)
      
    def __post_init__(self):  
        """Validate observation."""  
        if not 0 <= self.engagement_score <= 1:  
            raise ValueError(  
                f"Engagement score must be in [0, 1], got {self.engagement_score}"  
            )
          
        if self.time_spent < 0:  
            raise ValueError(  
                f"Time spent must be non-negative, got {self.time_spent}"  
            )
      
    def to_dict(self) -> Dict:  
        """Convert to dictionary representation."""  
        return {  
            'content_id': self.content_id,  
            'topic_id': self.topic_id,  
            'correct': self.correct,  
            'time_spent': self.time_spent,  
            'engagement_score': self.engagement_score,  
            'timestamp': self.timestamp.isoformat(),  
            'metadata': self.metadata  
        }  