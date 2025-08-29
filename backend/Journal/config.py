# backend/journal/config.py
# Configuration settings for Eco-Journal

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for Eco-Journal"""
    
    # Database Settings
    POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:password@localhost:5432/ecoapp")
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    
    # ML Model Settings
    EMOTION_MODEL = "SamLowe/roberta-base-go_emotions"
    SENTIMENT_THRESHOLD_POSITIVE = 0.2
    SENTIMENT_THRESHOLD_NEGATIVE = -0.2
    EMOTION_CONFIDENCE_THRESHOLD = 0.1
    
    # Streak Settings
    MAX_FREEZES_PER_MONTH = 3
    STREAK_RESET_AFTER_DAYS = 2  # Reset streak if no entry for 2+ days
    
    # Inspiration Settings
    INSPIRATION_CACHE_SIZE = 100
    
    # Default User
    DEFAULT_USER_ID = "1"
    DEFAULT_USERNAME = "eco_user_1"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_emotion_weights(cls):
        """Return emotion weights for sentiment calculation"""
        return {
            'positive': {
                'joy': 1.0, 'pride': 1.0, 'optimism': 0.8, 
                'excitement': 0.9, 'love': 1.0, 'relief': 0.7,
                'gratitude': 0.8, 'admiration': 0.6, 'approval': 0.5,
                'caring': 0.6, 'desire': 0.4, 'amusement': 0.7
            },
            'negative': {
                'guilt': -1.0, 'sadness': -0.8, 'anger': -0.9,
                'fear': -0.7, 'disappointment': -0.8, 'shame': -1.0,
                'remorse': -0.9, 'frustration': -0.6, 'annoyance': -0.5,
                'embarrassment': -0.7, 'grief': -0.9, 'nervousness': -0.4
            },
            'neutral': {
                'surprise': 0.0, 'confusion': 0.0, 'curiosity': 0.1,
                'neutral': 0.0, 'realization': 0.0, 'disapproval': -0.1
            }
        }
    
    @classmethod
    def get_eco_keywords(cls):
        """Return eco-related keywords for categorization"""
        return {
            'transport': [
                'bicycle', 'bike', 'walk', 'walking', 'public transport', 
                'carpool', 'metro', 'bus', 'train', 'electric vehicle'
            ],
            'energy': [
                'solar', 'LED', 'electricity', 'energy saving', 'unplug',
                'renewable', 'wind power', 'hydroelectric', 'battery'
            ],
            'waste': [
                'recycle', 'recycling', 'reuse', 'compost', 'composting',
                'plastic', 'zero waste', 'reduce', 'upcycle'
            ],
            'food': [
                'organic', 'local', 'plant-based', 'vegetarian', 'vegan',
                'sustainable', 'farm', 'seasonal', 'food waste'
            ],
            'water': [
                'conservation', 'shower', 'tap', 'rain water', 'drought',
                'water saving', 'irrigation', 'greywater'
            ],
            'consumption': [
                'minimalism', 'second-hand', 'thrift', 'repair', 'diy',
                'sustainable shopping', 'eco-friendly', 'green products'
            ]
        }