"""Data models and schemas."""  
from dataclasses import dataclass, field  
from typing import List, Dict, Optional  
from enum import Enum  
from datetime import datetime

  
class LearningStyle(Enum):  
    """Learning style preferences."""  
    VISUAL = "visual"  
    AUDITORY = "auditory"  
    KINESTHETIC = "kinesthetic"  
    READING_WRITING = "reading_writing"

  
class ContentType(Enum):  
    """Types of learning content."""  
    VIDEO = "video"  
    TEXT = "text"  
    INTERACTIVE = "interactive"  
    QUIZ = "quiz"  
    CASE_STUDY = "case_study"

  
@dataclass  
class Topic:  
    """Represents a learning topic."""  
    id: str  
    name: str  
    prerequisites: List[str] = field(default_factory=list)  
    importance_weight: float = 1.0  
    difficulty: float = 0.5  
    created_at: Optional[datetime] = None

  
@dataclass  
class Content:  
    """Represents learning content."""  
    id: str  
    topic_id: str  
    content_type: ContentType  
    difficulty: float  
    title: str  
    description: str  
    estimated_duration: int  # minutes  
    intrinsic_load: float = 0.5  
    content_data: Dict = field(default_factory=dict)  
    interaction_count: int = 0  
    created_at: Optional[datetime] = None

  
@dataclass  
class StudentState:  
    """Represents student state."""  
    student_id: str  
    knowledge_state: Dict[str, float] = field(default_factory=dict)  
    learning_style_preferences: Dict[LearningStyle, float] = field(default_factory=dict)  
    current_cognitive_load: float = 0.0  
    recent_performance: List[float] = field(default_factory=list)  
    mastered_topics: List[str] = field(default_factory=list)  
    total_interactions: int = 0  
    engagement_history: List[float] = field(default_factory=list)  
    created_at: Optional[datetime] = None  
    updated_at: Optional[datetime] = None

  
@dataclass  
class Observation:  
    """Represents a learning interaction observation."""  
    content_id: str  
    topic_id: str  
    correct: bool  
    time_spent: int  # seconds  
    engagement_score: float  
    timestamp: datetime = field(default_factory=datetime.now)  
    metadata: Dict = field(default_factory=dict)

  
@dataclass  
class Recommendation:  
    """Represents a content recommendation."""  
    student_id: str  
    content_id: str  
    score: float  
    component_scores: Dict[str, float]  
    timestamp: datetime = field(default_factory=datetime.now)  
    was_selected: bool = False  
    ab_variant: Optional[str] = None  