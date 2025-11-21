"""Configuration settings for the adaptive learning system."""  
import os  
from pathlib import Path  
from pydantic_settings import BaseSettings  
from typing import List  
import os  
from pathlib import Path
  
# Algorithm configuration  
ALGORITHM_CONFIG = {  
    'weights': {  
        'learning_style': 0.15,  
        'difficulty': 0.25,  
        'cognitive_load': 0.20,  
        'knowledge_gap': 0.25,  
        'engagement': 0.15,  
    },  
    'zpd_delta': 0.2,  
    'zpd_sigma': 0.15,  
    'cl_optimal': 0.7,  
    'cl_max': 0.9,  
    'beta_0': 1.0,  
    'mastery_threshold': 0.7,  
}
  
# BKT parameters  
BKT_CONFIG = {  
    'p_init': 0.0,  
    'p_learn': 0.3,  
    'p_slip': 0.1,  
    'p_guess': 0.2,  
}
  

class Settings(BaseSettings):  
    """  
    API settings loaded from environment variables.
      
    Create a .env file with these variables for local development.  
    """
      
     
    # Algorithm Weights (from paper - Equation 5)  
    # These are the default weights, can be overridden by A/B tests  
    @property  
    def ALGORITHM_WEIGHTS(self) -> dict:  
        """Get algorithm component weights (must sum to 1.0)."""  
        return ALGORITHM_CONFIG['weights']
      
    
    class Config:  
        env_file = ".env"  
        case_sensitive = True

  
# Create settings instance  
settings = Settings()
  
