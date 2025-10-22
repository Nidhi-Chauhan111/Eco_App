# backend/journal/journal_service.py
# Main service that orchestrates journal entry processing

import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from config import Config
from analyzer import EcoJournalAnalyzer, InspirationGenerator
from streak_manager import StreakManager

# Import database repositories
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../Database'))
from Journal import get_journal_repository

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class EcoJournalService:
    """Main service for processing eco-journal entries"""
    
    def __init__(self):
        # Initialize components
        self.analyzer = EcoJournalAnalyzer()
        self.inspiration_generator = InspirationGenerator()
        self.streak_manager = StreakManager()
        self.journal_repo = get_journal_repository()
        
        logger.info("✅ EcoJournalService initialized successfully")
    
    def process_journal_entry(self, user_id: str, content: str, entry_date: date = None) -> Dict[str, Any]:
        """
        Process a complete journal entry from start to finish
        
        Args:
            user_id: User identifier
            content: Journal entry text
            entry_date: Date of the entry (defaults to today)
            
        Returns:
            Complete processing result with analysis, inspiration, and streak updates
        """
        if not content or not content.strip():
            return self._create_error_response("Journal entry content cannot be empty")
        
        if entry_date is None:
            entry_date = date.today()
        
        try:
            logger.info(f"Processing journal entry for user {user_id}")
            
            # Step 1: Analyze sentiment and emotions
            logger.info("🧠 Analyzing emotions and sentiment...")
            analysis_result = self.analyzer.analyze_journal_entry(content)
            
            # Step 2: Update user streak
            logger.info("🔥 Updating user streak...")
            streak_result = self.streak_manager.update_user_streak(user_id, entry_date)
            
            # Step 3: Generate personalized inspiration
            logger.info("💡 Generating inspiration...")
            user_context = {
                'current_streak': streak_result.get('current_streak', 0),
                'total_entries': streak_result.get('total_entries', 0),
                'new_achievements': streak_result.get('new_achievements', [])
            }
            inspiration = self.inspiration_generator.generate_inspiration(
                analysis_result, user_context
            )
            
            # Step 4: Save to database
            logger.info("💾 Saving to database...")
            entry_id = self.journal_repo.save_entry(
                user_id=user_id,
                content=content,
                analysis_result=analysis_result,
                inspiration=inspiration,
                eco_tags=analysis_result.get('eco_tags', [])
            )
            
            # Step 5: Compile complete response
            response = self._create_success_response(
                entry_id=entry_id,
                analysis_result=analysis_result,
                inspiration=inspiration,
                streak_result=streak_result,
                user_id=user_id,
                entry_date=entry_date
            )
            
            logger.info(f"✅ Journal entry processed successfully for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to process journal entry for user {user_id}: {e}")
            return self._create_error_response(f"Processing failed: {str(e)}")
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user dashboard data
        
        Args:
            user_id: User identifier
            
        Returns:
            Dashboard data including streak, recent entries, achievements, etc.
        """
        try:
            logger.info(f"Generating dashboard for user {user_id}")
            
            # Get streak status
            streak_status = self.streak_manager.get_streak_status(user_id)
            
            # Get recent journal entries
            recent_entries = self.journal_repo.get_user_entries(user_id, limit=10)
            
            # Get streak analytics
            analytics = self.streak_manager.get_streak_analytics(user_id, days=30)
            
            # Process recent entries for summary
            entry_summary = self._create_entry_summary(recent_entries)
            
            dashboard = {
                'user_id': user_id,
                'streak_status': streak_status,
                'recent_entries': {
                    'count': len(recent_entries),
                    'entries': recent_entries[:5],  # Last 5 entries
                    'summary': entry_summary
                },
                'analytics': analytics,
                'recommendations': self._generate_recommendations(streak_status, analytics),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard for user {user_id}: {e}")
            return {'error': str(e), 'user_id': user_id}
    
    def get_inspiration_for_mood(self, user_id: str, mood: str) -> Dict[str, str]:
        """
        Get inspiration based on current mood
        
        Args:
            user_id: User identifier
            mood: Current mood/emotion
            
        Returns:
            Inspiration message and suggestions
        """
        try:
            # Create mock analysis result for the mood
            mock_analysis = {
                'sentiment': {'label': 'Neutral' if mood == 'neutral' else 'Positive' if mood in ['happy', 'excited', 'proud'] else 'Negative'},
                'emotions': {'top_emotions': [{'label': mood, 'score': 0.8}], 'breakdown': {'positive': [], 'negative': [], 'neutral': []}},
                'eco_tags': [],
                'mixed_emotions': False
            }
            
            # Get streak context
            streak_status = self.streak_manager.get_streak_status(user_id)
            user_context = {
                'current_streak': streak_status.get('current_streak', 0),
                'total_entries': streak_status.get('total_entries', 0)
            }
            
            inspiration = self.inspiration_generator.generate_inspiration(mock_analysis, user_context)
            
            return {
                'inspiration': inspiration,
                'mood': mood,
                'suggestions': self._get_mood_based_suggestions(mood)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate mood inspiration for user {user_id}: {e}")
            return {'error': str(e), 'mood': mood}
    
    def _create_success_response(self, entry_id: str, analysis_result: Dict, 
                               inspiration: str, streak_result: Dict, 
                               user_id: str, entry_date: date) -> Dict[str, Any]:
        """Create successful processing response"""
        return {
            'success': True,
            'entry_id': entry_id,
            'user_id': user_id,
            'entry_date': entry_date.isoformat(),
            'analysis': {
                'sentiment': analysis_result['sentiment'],
                'emotions': analysis_result['emotions'],
                'eco_tags': analysis_result['eco_tags'],
                'mixed_emotions': analysis_result['mixed_emotions'],
                'emotion_summary': self.analyzer.get_emotion_summary(analysis_result)
            },
            'inspiration': inspiration,
            'streak': {
                'current_streak': streak_result['current_streak'],
                'longest_streak': streak_result['longest_streak'],
                'total_entries': streak_result['total_entries'],
                'streak_event': streak_result['streak_event'],
                'new_achievements': streak_result['new_achievements'],
                'next_milestone': streak_result['next_milestone'],
                'freezes_remaining': streak_result['freezes_remaining']
            },
            'processed_at': datetime.utcnow().isoformat()
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'error': error_message,
            'processed_at': datetime.utcnow().isoformat()
        }
    
    def _create_entry_summary(self, entries: List[Dict]) -> Dict[str, Any]:
        """Create summary of recent journal entries"""
        if not entries:
            return {
                'total_entries': 0,
                'dominant_sentiment': 'None',
                'common_eco_tags': [],
                'recent_emotions': []
            }
        
        # Analyze sentiment distribution
        sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0, 'Mixed': 0}
        all_eco_tags = []
        all_emotions = []
        
        for entry in entries:
            analysis = entry.get('analysis', {})
            
            # Count sentiments
            sentiment = analysis.get('sentiment', {}).get('label', 'Neutral')
            if analysis.get('mixed_emotions', False):
                sentiment = 'Mixed'
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            # Collect eco tags
            all_eco_tags.extend(analysis.get('eco_tags', []))
            
            # Collect top emotions
            top_emotions = analysis.get('emotions', {}).get('top_emotions', [])
            for emotion in top_emotions[:2]:  # Top 2 emotions per entry
                all_emotions.append(emotion.get('label', ''))
        
        # Find dominant sentiment
        dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        
        # Find most common eco tags
        eco_tag_counts = {}
        for tag in all_eco_tags:
            eco_tag_counts[tag] = eco_tag_counts.get(tag, 0) + 1
        
        common_eco_tags = sorted(eco_tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Find most common emotions
        emotion_counts = {}
        for emotion in all_emotions:
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        recent_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_entries': len(entries),
            'sentiment_distribution': sentiment_counts,
            'dominant_sentiment': dominant_sentiment,
            'common_eco_tags': [tag for tag, count in common_eco_tags],
            'recent_emotions': [emotion for emotion, count in recent_emotions]
        }
    
    def _generate_recommendations(self, streak_status: Dict, analytics: Dict) -> List[str]:
        """Generate personalized recommendations based on user data"""
        recommendations = []
        
        current_streak = streak_status.get('current_streak', 0)
        consistency_rate = analytics.get('consistency_rate', 0)
        days_since_last_entry = streak_status.get('days_since_last_entry', 0)
        
        # Streak-based recommendations
        if current_streak == 0:
            recommendations.append("🌱 Start your eco-journey today! Even small actions count.")
        elif current_streak < 7:
            recommendations.append("🔥 You're building momentum! Try to reach your first week.")
        elif current_streak < 30:
            recommendations.append("💪 Great progress! Aim for the 30-day milestone.")
        
        # Consistency recommendations
        if consistency_rate < 70:
            recommendations.append("📅 Try setting a daily reminder to improve consistency.")
        elif consistency_rate > 90:
            recommendations.append("🏆 Excellent consistency! You're an eco-champion!")
        
        # Engagement recommendations
        if days_since_last_entry > 0:
            recommendations.append("⏰ Your streak is at risk! Make an entry today to keep it alive.")
        
        # Achievement recommendations
        if current_streak > 0:
            next_milestone = streak_status.get('next_milestone')
            if next_milestone:
                days_to_milestone = next_milestone.get('days_remaining', 0)
                if days_to_milestone <= 7:
                    recommendations.append(f"🎯 Only {days_to_milestone} days to earn '{next_milestone['name']}'!")
        
        return recommendations
    
    def _get_mood_based_suggestions(self, mood: str) -> List[str]:
        """Get eco-action suggestions based on mood"""
        mood_suggestions = {
            'happy': [
                "Share your positive energy by teaching someone about eco-habits!",
                "Use this upbeat mood to tackle a challenging eco-project!",
                "Celebrate by treating yourself to a sustainable product!"
            ],
            'sad': [
                "Take a mindful walk in nature to lift your spirits.",
                "Try a small eco-action like organizing your recycling.",
                "Remember: every small action helps heal our planet."
            ],
            'frustrated': [
                "Channel that energy into advocacy - write to a local representative!",
                "Start a small eco-project that gives you a sense of control.",
                "Take deep breaths and remember progress takes time."
            ],
            'motivated': [
                "Perfect time to start a new eco-challenge!",
                "Research a new sustainable practice to adopt.",
                "Plan your eco-actions for the week ahead!"
            ],
            'guilty': [
                "Transform guilt into action - every expert was once a beginner.",
                "Make one small eco-friendly choice right now.",
                "Focus on progress, not perfection in your eco-journey."
            ]
        }
        
        return mood_suggestions.get(mood.lower(), [
            "Every mood is valid on your eco-journey.",
            "Take one small step toward sustainability today.",
            "Remember: awareness is the first step to positive change."
        ])