# backend/journal/analyzer.py
# Sentiment and Emotion Analysis for Eco-Journal

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from transformers import pipeline
import numpy as np
from config import Config

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class EcoJournalAnalyzer:
    """Handles sentiment analysis and emotion detection for journal entries"""
    
    def __init__(self):
        self.emotion_classifier = None
        self.emotion_weights = Config.get_emotion_weights()
        self.eco_keywords = Config.get_eco_keywords()
        self.confidence_threshold = Config.EMOTION_CONFIDENCE_THRESHOLD
        self._load_model()
        
    def _load_model(self):
        """Load HuggingFace emotion classification model"""
        try:
            logger.info("Loading emotion classification model...")
            self.emotion_classifier = pipeline(
                "text-classification",
                model=Config.EMOTION_MODEL,
                return_all_scores=True
            )
            logger.info("✅ Model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def analyze_journal_entry(self, text: str) -> Dict[str, Any]:
        """
        Analyze journal entry for emotions and sentiment
        
        Args:
            text: Journal entry text
            
        Returns:
            Dictionary containing sentiment, emotions, and metadata
        """
        if not text or not text.strip():
            return self._create_empty_analysis()
        
        try:
            # Get emotion predictions
            raw_emotions = self.emotion_classifier(text)
            
            # Filter significant emotions
            significant_emotions = [
                e for e in raw_emotions 
                if e['score'] >= self.confidence_threshold
            ]
            
            # Calculate weighted sentiment
            sentiment_result = self._calculate_weighted_sentiment(significant_emotions)
            
            # Categorize emotions
            emotion_breakdown = self._categorize_emotions(significant_emotions)
            
            # Extract eco-related tags
            eco_tags = self._extract_eco_tags(text)
            
            # Determine if mixed emotions
            mixed_emotions = self._has_mixed_emotions(emotion_breakdown)
            
            return {
                'sentiment': sentiment_result,
                'emotions': {
                    'top_emotions': sorted(significant_emotions, key=lambda x: x['score'], reverse=True)[:3],
                    'breakdown': emotion_breakdown,
                    'total_emotions_detected': len(significant_emotions)
                },
                'eco_tags': eco_tags,
                'mixed_emotions': mixed_emotions,
                'analysis_metadata': {
                    'confidence_threshold': self.confidence_threshold,
                    'total_raw_emotions': len(raw_emotions),
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for text: {text[:50]}... Error: {e}")
            return self._create_empty_analysis()
    
    def _calculate_weighted_sentiment(self, emotions: List[Dict]) -> Dict[str, Any]:
        """Calculate weighted sentiment score from emotions"""
        sentiment_score = 0.0
        total_weight = 0.0
        
        for emotion in emotions:
            label = emotion['label']
            score = emotion['score']
            
            # Find emotion weight
            weight = self._get_emotion_weight(label)
            weighted_contribution = weight * score
            sentiment_score += weighted_contribution
            total_weight += abs(weight) * score
        
        # Normalize sentiment score
        if total_weight > 0:
            sentiment_score = sentiment_score / total_weight * 2  # Scale factor
        
        # Determine sentiment label
        if sentiment_score > Config.SENTIMENT_THRESHOLD_POSITIVE:
            sentiment_label = "Positive"
        elif sentiment_score < Config.SENTIMENT_THRESHOLD_NEGATIVE:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
        
        return {
            'label': sentiment_label,
            'score': round(sentiment_score, 3),
            'confidence': round(abs(sentiment_score), 3),
            'raw_score': sentiment_score
        }
    
    def _get_emotion_weight(self, emotion_label: str) -> float:
        """Get weight for specific emotion"""
        for category, emotions in self.emotion_weights.items():
            if emotion_label in emotions:
                return emotions[emotion_label]
        return 0.0  # Unknown emotion
    
    def _categorize_emotions(self, emotions: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize emotions into positive, negative, neutral"""
        categorized = {'positive': [], 'negative': [], 'neutral': []}
        
        for emotion in emotions:
            label = emotion['label']
            weight = self._get_emotion_weight(label)
            
            category = 'neutral'
            if weight > 0:
                category = 'positive'
            elif weight < 0:
                category = 'negative'
            
            categorized[category].append({
                'emotion': label,
                'score': round(emotion['score'], 3),
                'weight': weight
            })
        
        # Sort by score within each category
        for category in categorized:
            categorized[category].sort(key=lambda x: x['score'], reverse=True)
        
        return categorized
    
    def _extract_eco_tags(self, text: str) -> List[str]:
        """Extract eco-related tags from text"""
        text_lower = text.lower()
        found_tags = set()
        
        for category, keywords in self.eco_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_tags.add(category)
                    break
        
        return list(found_tags)
    
    def _has_mixed_emotions(self, emotion_breakdown: Dict) -> bool:
        """Check if entry has mixed emotions"""
        positive_count = len(emotion_breakdown['positive'])
        negative_count = len(emotion_breakdown['negative'])
        
        # Mixed if both positive and negative emotions present with reasonable scores
        return positive_count > 0 and negative_count > 0
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create empty analysis result for error cases"""
        return {
            'sentiment': {
                'label': 'Neutral',
                'score': 0.0,
                'confidence': 0.0,
                'raw_score': 0.0
            },
            'emotions': {
                'top_emotions': [],
                'breakdown': {'positive': [], 'negative': [], 'neutral': []},
                'total_emotions_detected': 0
            },
            'eco_tags': [],
            'mixed_emotions': False,
            'analysis_metadata': {
                'confidence_threshold': self.confidence_threshold,
                'total_raw_emotions': 0,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'error': True
            }
        }
    
    async def analyze_async(self, text: str) -> Dict[str, Any]:
        """Async wrapper for analysis (useful for web APIs)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analyze_journal_entry, text)
    
    def get_emotion_summary(self, analysis_result: Dict) -> str:
        """Generate human-readable emotion summary"""
        emotions = analysis_result['emotions']
        sentiment = analysis_result['sentiment']
        
        if not emotions['top_emotions']:
            return "No strong emotions detected"
        
        top_emotion = emotions['top_emotions'][0]
        emotion_name = top_emotion['label'].replace('_', ' ').title()
        confidence = int(top_emotion['score'] * 100)
        
        if analysis_result['mixed_emotions']:
            positive_emotions = [e['emotion'] for e in emotions['breakdown']['positive'][:2]]
            negative_emotions = [e['emotion'] for e in emotions['breakdown']['negative'][:2]]
            
            pos_str = ', '.join(positive_emotions) if positive_emotions else ''
            neg_str = ', '.join(negative_emotions) if negative_emotions else ''
            
            return f"Mixed feelings detected: {pos_str} and {neg_str} ({sentiment['label']} overall)"
        else:
            return f"Primary emotion: {emotion_name} ({confidence}% confidence, {sentiment['label']} sentiment)"

class InspirationGenerator:
    """Generates personalized inspiration messages based on analysis results"""
    
    def __init__(self):
        self.inspiration_templates = self._load_inspiration_templates()
    
    def generate_inspiration(self, analysis_result: Dict, user_context: Dict = None) -> str:
        """
        Generate personalized inspiration message
        
        Args:
            analysis_result: Result from EcoJournalAnalyzer
            user_context: Additional user context (streak, history, etc.)
            
        Returns:
            Personalized inspiration message
        """
        sentiment = analysis_result['sentiment']
        emotions = analysis_result['emotions']
        eco_tags = analysis_result['eco_tags']
        mixed_emotions = analysis_result['mixed_emotions']
        
        if mixed_emotions:
            return self._generate_mixed_emotion_inspiration(emotions, eco_tags)
        elif sentiment['label'] == 'Positive':
            return self._generate_positive_inspiration(emotions, eco_tags, user_context)
        elif sentiment['label'] == 'Negative':
            return self._generate_recovery_inspiration(emotions, eco_tags, user_context)
        else:
            return self._generate_neutral_inspiration(eco_tags, user_context)
    
    def _generate_mixed_emotion_inspiration(self, emotions: Dict, eco_tags: List[str]) -> str:
        """Generate inspiration for mixed emotions"""
        templates = self.inspiration_templates['mixed']
        
        positive_emotions = emotions['breakdown']['positive']
        negative_emotions = emotions['breakdown']['negative']
        
        if positive_emotions and negative_emotions:
            pos_emotion = positive_emotions[0]['emotion']
            neg_emotion = negative_emotions[0]['emotion']
            
            # Look for specific emotion combinations
            combo_key = f"{pos_emotion}_{neg_emotion}"
            if combo_key in templates:
                return templates[combo_key]
            
            # Fallback to general mixed emotion message
            return templates['general'].format(
                positive_emotion=pos_emotion.replace('_', ' '),
                negative_emotion=neg_emotion.replace('_', ' ')
            )
        
        return templates['default']
    
    def _generate_positive_inspiration(self, emotions: Dict, eco_tags: List[str], user_context: Dict) -> str:
        """Generate positive reinforcement inspiration"""
        templates = self.inspiration_templates['positive']
        
        top_emotion = emotions['top_emotions'][0]['label'] if emotions['top_emotions'] else 'joy'
        
        # Use emotion-specific template if available
        if top_emotion in templates:
            message = templates[top_emotion]
        else:
            message = templates['general']
        
        # Add eco-specific context
        if eco_tags:
            eco_tag = eco_tags[0]
            if eco_tag in templates.get('eco_specific', {}):
                message += " " + templates['eco_specific'][eco_tag]
        
        return message
    
    def _generate_recovery_inspiration(self, emotions: Dict, eco_tags: List[str], user_context: Dict) -> str:
        """Generate recovery and motivation inspiration"""
        templates = self.inspiration_templates['negative']
        
        top_emotion = emotions['top_emotions'][0]['label'] if emotions['top_emotions'] else 'disappointment'
        
        if top_emotion in templates:
            return templates[top_emotion]
        else:
            return templates['general']
    
    def _generate_neutral_inspiration(self, eco_tags: List[str], user_context: Dict) -> str:
        """Generate gentle encouragement for neutral sentiment"""
        templates = self.inspiration_templates['neutral']
        
        if eco_tags:
            return templates['with_eco_tags']
        else:
            return templates['general']
    
    def _load_inspiration_templates(self) -> Dict[str, Dict[str, str]]:
        """Load inspiration message templates"""
        return {
            'positive': {
                'joy': "Your joy is contagious! 😊 Keep spreading those positive eco-vibes! 🌱",
                'pride': "That pride you feel? It's well-deserved! 🏆 Every eco-action counts! 🌍",
                'optimism': "Your optimism lights the way for others! ✨ Keep shining bright! 🌟",
                'excitement': "That excitement is fuel for change! 🚀 Channel it into more eco-wins! 💚",
                'gratitude': "Gratitude is the heart of sustainability! 🙏 Thank you for caring! 🌿",
                'general': "You're doing amazing! 🌟 Every step towards sustainability matters! 🌱",
                'eco_specific': {
                    'transport': "Your sustainable transport choices make a real difference! 🚲",
                    'energy': "Energy consciousness leads to a brighter future! ⚡",
                    'waste': "Reducing waste is reducing worry for our planet! ♻️",
                    'food': "Mindful eating feeds both you and the Earth! 🌱",
                    'water': "Every drop saved is a gift to future generations! 💧"
                }
            },
            'negative': {
                'guilt': "Guilt shows you care deeply. Transform it into positive action tomorrow! 💪🌱",
                'disappointment': "Setbacks are setups for comebacks! Tomorrow is a fresh eco-opportunity! 🌅",
                'frustration': "Your frustration shows passion! Channel it into sustainable solutions! 🔥",
                'sadness': "It's okay to feel sad about our planet. Your awareness is the first step to healing! 💚",
                'shame': "No shame in the sustainability game! Every expert was once a beginner! 🌱",
                'general': "Every eco-champion has tough days. What matters is that you keep caring! 🌍💚"
            },
            'mixed': {
                'pride_guilt': "It's natural to feel both proud and reflective. Balance leads to growth! 🌱⚖️",
                'joy_disappointment': "Joy and disappointment can coexist. Focus on the progress! 🌈",
                'optimism_frustration': "Your optimism will outlast the frustration. Keep believing! 🌟",
                'general': "Complex feelings about our planet show deep caring. That's beautiful! 💚🌍",
                'default': "Mixed emotions are perfectly normal on the eco-journey! 🌈🌱"
            },
            'neutral': {
                'general': "Every day is a chance to make a difference. What will you choose today? 🌱",
                'with_eco_tags': "You're already thinking about eco-actions. That's the first step! 🌿"
            }
        }