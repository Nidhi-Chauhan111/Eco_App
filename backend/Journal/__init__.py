# backend/journal/__init__.py
# Eco-Journal Package Initialization

"""
Eco-Journal Backend Package

This package provides comprehensive eco-journal functionality including:
- Sentiment and emotion analysis using HuggingFace models
- Streak tracking and gamification
- Personalized inspiration generation
- Database management for PostgreSQL and MongoDB
- Terminal-based interface for testing

Main Components:
- EcoJournalService: Main orchestration service
- EcoJournalAnalyzer: Sentiment/emotion analysis
- StreakManager: Gamification and streak tracking
- InspirationGenerator: Personalized motivation messages

Usage:
    from journal_service import EcoJournalService
    service = EcoJournalService()
    result = service.process_journal_entry("1", "I feel great about cycling today!")
"""

__version__ = "1.0.0"
__author__ = "Eco-App Development Team"

# Import main classes for easy access
from .journal_service import EcoJournalService
from .analyzer import EcoJournalAnalyzer, InspirationGenerator  
from .streak_manager import StreakManager
from .config import Config

__all__ = [
    'EcoJournalService',
    'EcoJournalAnalyzer', 
    'InspirationGenerator',
    'StreakManager',
    'Config'
]