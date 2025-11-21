"""  
Content model representing learning materials.
  
Based on the paper's content representation with:  
- Difficulty levels  
- Content types (video, text, interactive, quiz, case_study)  
- Intrinsic cognitive load  
- Topic associations  
"""
  
from dataclasses import dataclass, field  
from typing import Dict, List, Optional, Any  
from datetime import datetime  
from enum import Enum

  
class ContentType(Enum):  
    """  
    Types of learning content.
      
    Based on the paper's multi-modal content approach.  
    Each type has different affinity with learning styles (Equation 6).  
    """  
    VIDEO = "video"  
    TEXT = "text"  
    INTERACTIVE = "interactive"  
    QUIZ = "quiz"  
    CASE_STUDY = "case_study"

  
@dataclass  
class Content:  
    """  
    Represents a piece of learning content.
      
    Attributes correspond to features used in scoring function (Equation 5):  
    - difficulty: Used in D(c,st) - Difficulty Appropriateness (Equation 7)  
    - intrinsic_load: Used in CL(c,st) - Cognitive Load (Equation 12)  
    - content_type: Used in LS(c,st) - Learning Style Match (Equation 6)  
    - interaction_count: Used in E(c,st,t) - Exploration Bonus (Equation 15)  
    """
      
    id: str  
    topic_id: str  
    content_type: ContentType  
    difficulty: float  # [0, 1] - dc in Equation 7  
    title: str  
    description: str  
    estimated_duration: int  # Duration in minutes  
    intrinsic_load: float = 0.5  # [0, 1] - Used in Equation 12  
    content_data: Dict[str, Any] = field(default_factory=dict)  
    interaction_count: int = 0  # Nc in Equation 15  
    created_at: Optional[datetime] = None  
    updated_at: Optional[datetime] = None
      
    # Additional metadata  
    prerequisites: List[str] = field(default_factory=list)  
    learning_objectives: List[str] = field(default_factory=list)  
    tags: List[str] = field(default_factory=list)
      
    def __post_init__(self):  
        """Validate content attributes."""  
        if not 0 <= self.difficulty <= 1:  
            raise ValueError(f"Difficulty must be in [0, 1], got {self.difficulty}")
          
        if not 0 <= self.intrinsic_load <= 1:  
            raise ValueError(f"Intrinsic load must be in [0, 1], got {self.intrinsic_load}")
          
        if self.estimated_duration <= 0:  
            raise ValueError(f"Duration must be positive, got {self.estimated_duration}")
          
        if isinstance(self.content_type, str):  
            self.content_type = ContentType(self.content_type)
      
    def get_difficulty_label(self) -> str:  
        """Get human-readable difficulty label."""  
        if self.difficulty < 0.3:  
            return "Easy"  
        elif self.difficulty < 0.6:  
            return "Moderate"  
        elif self.difficulty < 0.8:  
            return "Challenging"  
        else:  
            return "Advanced"
      
    def get_cognitive_load_label(self) -> str:  
        """Get cognitive load label."""  
        if self.intrinsic_load < 0.3:  
            return "Low"  
        elif self.intrinsic_load < 0.7:  
            return "Moderate"  
        else:  
            return "High"
      
    def to_dict(self) -> Dict[str, Any]:  
        """Convert to dictionary representation."""  
        return {  
            'id': self.id,  
            'topic_id': self.topic_id,  
            'content_type': self.content_type.value,  
            'difficulty': self.difficulty,  
            'title': self.title,  
            'description': self.description,  
            'estimated_duration': self.estimated_duration,  
            'intrinsic_load': self.intrinsic_load,  
            'content_data': self.content_data,  
            'interaction_count': self.interaction_count,  
            'prerequisites': self.prerequisites,  
            'learning_objectives': self.learning_objectives,  
            'tags': self.tags,  
            'created_at': self.created_at.isoformat() if self.created_at else None,  
            'updated_at': self.updated_at.isoformat() if self.updated_at else None  
        }
      
    @classmethod  
    def from_dict(cls, data: Dict[str, Any]) -> 'Content':  
        """Create Content from dictionary."""  
        # Convert datetime strings  
        if 'created_at' in data and isinstance(data['created_at'], str):  
            data['created_at'] = datetime.fromisoformat(data['created_at'])  
        if 'updated_at' in data and isinstance(data['updated_at'], str):  
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
          
        # Convert content_type string to enum  
        if isinstance(data.get('content_type'), str):  
            data['content_type'] = ContentType(data['content_type'])
          
        return cls(**data)

  
@dataclass  
class Topic:  
    """  
    Represents a learning topic in the curriculum.
      
    Topics form a prerequisite graph used in constraint checking  
    (Equation 18: Prerequisites(c) ⊆ Mastered(st)).  
    """
      
    id: str  
    name: str  
    prerequisites: List[str] = field(default_factory=list)  
    importance_weight: float = 1.0  # wj in K(st) calculation  
    difficulty: float = 0.5  # Average difficulty of topic content  
    created_at: Optional[datetime] = None
      
    # Additional metadata  
    description: str = ""  
    learning_outcomes: List[str] = field(default_factory=list)  
    estimated_hours: float = 0.0
      
    def __post_init__(self):  
        """Validate topic attributes."""  
        if self.importance_weight <= 0:  
            raise ValueError(f"Importance weight must be positive, got {self.importance_weight}")
          
        if not 0 <= self.difficulty <= 1:  
            raise ValueError(f"Difficulty must be in [0, 1], got {self.difficulty}")
      
    def has_prerequisites(self) -> bool:  
        """Check if topic has prerequisites."""  
        return len(self.prerequisites) > 0
      
    def to_dict(self) -> Dict[str, Any]:  
        """Convert to dictionary representation."""  
        return {  
            'id': self.id,  
            'name': self.name,  
            'prerequisites': self.prerequisites,  
            'importance_weight': self.importance_weight,  
            'difficulty': self.difficulty,  
            'description': self.description,  
            'learning_outcomes': self.learning_outcomes,  
            'estimated_hours': self.estimated_hours,  
            'created_at': self.created_at.isoformat() if self.created_at else None  
        }
      
    @classmethod  
    def from_dict(cls, data: Dict[str, Any]) -> 'Topic':  
        """Create Topic from dictionary."""  
        if 'created_at' in data and isinstance(data['created_at'], str):  
            data['created_at'] = datetime.fromisoformat(data['created_at'])
          
        return cls(**data)

  
@dataclass  
class CaseStudy(Content):  
    """  
    Specialized content type for case-based learning.
      
    Extends Content with case-specific attributes for health professions education.  
    """
      
    patient_presentation: str = ""  
    clinical_questions: List[str] = field(default_factory=list)  
    assessment_criteria: Dict[str, Any] = field(default_factory=dict)  
    learning_points: List[str] = field(default_factory=list)  
    complexity_level: str = "moderate"  # simple, moderate, complex
      
    def __post_init__(self):  
        """Initialize case study with CASE_STUDY type."""  
        super().__post_init__()  
        self.content_type = ContentType.CASE_STUDY
      
    def to_dict(self) -> Dict[str, Any]:  
        """Convert to dictionary with case-specific fields."""  
        base_dict = super().to_dict()  
        base_dict.update({  
            'patient_presentation': self.patient_presentation,  
            'clinical_questions': self.clinical_questions,  
            'assessment_criteria': self.assessment_criteria,  
            'learning_points': self.learning_points,  
            'complexity_level': self.complexity_level  
        })  
        return base_dict

  
@dataclass  
class Quiz(Content):  
    """  
    Specialized content type for assessments.
      
    Used for knowledge evaluation and BKT updates (Equations 9-11).  
    """
      
    questions: List[Dict[str, Any]] = field(default_factory=list)  
    passing_score: float = 0.7  
    time_limit: Optional[int] = None  # Time limit in minutes  
    randomize_questions: bool = False  
    show_feedback: bool = True
      
    def __post_init__(self):  
        """Initialize quiz with QUIZ type."""  
        super().__post_init__()  
        self.content_type = ContentType.QUIZ
      
    def get_question_count(self) -> int:  
        """Get number of questions in quiz."""  
        return len(self.questions)
      
    def to_dict(self) -> Dict[str, Any]:  
        """Convert to dictionary with quiz-specific fields."""  
        base_dict = super().to_dict()  
        base_dict.update({  
            'questions': self.questions,  
            'passing_score': self.passing_score,  
            'time_limit': self.time_limit,  
            'randomize_questions': self.randomize_questions,  
            'show_feedback': self.show_feedback,  
            'question_count': self.get_question_count()  
        })  
        return base_dict

  
# Content factory functions  
def create_video_content(  
    content_id: str,  
    topic_id: str,  
    title: str,  
    difficulty: float,  
    duration: int,  
    video_url: str,  
    **kwargs  
) -> Content:  
    """Factory function for creating video content."""  
    return Content(  
        id=content_id,  
        topic_id=topic_id,  
        content_type=ContentType.VIDEO,  
        difficulty=difficulty,  
        title=title,  
        estimated_duration=duration,  
        content_data={'video_url': video_url, **kwargs},  
        **kwargs  
    )

  
def create_text_content(  
    content_id: str,  
    topic_id: str,  
    title: str,  
    difficulty: float,  
    text_body: str,  
    **kwargs  
) -> Content:  
    """Factory function for creating text content."""  
    # Estimate reading time (200 words per minute)  
    word_count = len(text_body.split())  
    duration = max(1, word_count // 200)
      
    return Content(  
        id=content_id,  
        topic_id=topic_id,  
        content_type=ContentType.TEXT,  
        difficulty=difficulty,  
        title=title,  
        estimated_duration=duration,  
        content_data={'text_body': text_body, 'word_count': word_count},  
        **kwargs  
    )

  
def create_interactive_content(  
    content_id: str,  
    topic_id: str,  
    title: str,  
    difficulty: float,  
    interaction_type: str,  
    **kwargs  
) -> Content:  
    """Factory function for creating interactive content."""  
    return Content(  
        id=content_id,  
        topic_id=topic_id,  
        content_type=ContentType.INTERACTIVE,  
        difficulty=difficulty,  
        title=title,  
        content_data={'interaction_type': interaction_type},  
        **kwargs  
    )  