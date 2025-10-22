# backend/journal/streak_manager.py
# Streak management and gamification logic

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from config import Config

# Import database models and repositories
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../Database'))
from Journal import (
    get_user_repository, get_streak_event_repository, 
    get_achievement_repository, ACHIEVEMENTS
)

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class StreakManager:
    """Manages user streaks and gamification"""
    
    def __init__(self):
        self.max_freezes = Config.MAX_FREEZES_PER_MONTH
        self.reset_after_days = Config.STREAK_RESET_AFTER_DAYS
        
    def update_user_streak(self, user_id: str, entry_date: date = None) -> Dict:
        """
        Update user streak based on new journal entry
        
        Args:
            user_id: User identifier
            entry_date: Date of the journal entry (defaults to today)
            
        Returns:
            Dictionary with updated streak information
        """
        if entry_date is None:
            entry_date = date.today()
            
        try:
            user_repo = get_user_repository()
            streak_repo = get_streak_event_repository()
            achievement_repo = get_achievement_repository()
            
            # Get or create user
            user = user_repo.get_user_by_id(user_id)
            if not user:
                user = user_repo.create_user(user_id)
                logger.info(f"Created new user: {user_id}")
            
            # Calculate new streak
            previous_streak = user.current_streak
            new_streak_info = self._calculate_new_streak(user, entry_date)
            
            # Update user record
            user = user_repo.update_user_streak(
                user_id, 
                new_streak_info['streak'], 
                entry_date
            )
            
            # Log streak event
            streak_repo.log_event(
                user_id=user_id,
                event_type=new_streak_info['event_type'],
                streak_count=new_streak_info['streak'],
                previous_streak=previous_streak,
                metadata=new_streak_info.get('metadata', {})
            )
            
            # Check for new achievements
            new_achievements = achievement_repo.check_and_award_achievements(
                user_id, new_streak_info['streak']
            )
            
            result = {
                'user_id': user_id,
                'current_streak': new_streak_info['streak'],
                'longest_streak': user.longest_streak,
                'total_entries': user.total_entries,
                'streak_event': new_streak_info['event_type'],
                'streak_frozen': user.streak_frozen,
                'freeze_count': user.freeze_count,
                'freezes_remaining': max(0, self.max_freezes - user.freeze_count),
                'new_achievements': [
                    {
                        'name': achievement.achievement_name,
                        'description': achievement.description,
                        'badge': achievement.badge_emoji,
                        'streak_when_earned': achievement.streak_count_when_earned
                    }
                    for achievement in new_achievements
                ],
                'next_milestone': self._get_next_milestone(new_streak_info['streak']),
                'last_entry_date': entry_date.isoformat()
            }
            
            logger.info(f"Streak updated for user {user_id}: {previous_streak} → {new_streak_info['streak']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update streak for user {user_id}: {e}")
            return self._create_error_result(user_id, str(e))
    
    def _calculate_new_streak(self, user, entry_date: date) -> Dict:
        """Calculate new streak count and event type"""
        current_streak = user.current_streak
        last_entry_date = user.last_entry_date
        
        # First entry ever
        if last_entry_date is None:
            return {
                'streak': 1,
                'event_type': 'started',
                'metadata': {'is_first_entry': True}
            }
        
        # Same day entry (no change)
        if entry_date == last_entry_date:
            return {
                'streak': current_streak,
                'event_type': 'same_day',
                'metadata': {'no_change': True}
            }
        
        days_difference = (entry_date - last_entry_date).days
        
        # Consecutive day (streak continues)
        if days_difference == 1:
            new_streak = current_streak + 1
            return {
                'streak': new_streak,
                'event_type': 'continued',
                'metadata': {'days_difference': days_difference}
            }
        
        # Gap of more than 1 day
        elif days_difference > 1:
            # Check if streak was frozen
            if user.streak_frozen and days_difference <= self.reset_after_days:
                # Unfreeze and continue
                user.streak_frozen = False
                return {
                    'streak': current_streak + 1,
                    'event_type': 'unfrozen',
                    'metadata': {
                        'days_difference': days_difference,
                        'was_frozen': True
                    }
                }
            else:
                # Streak broken - reset to 1
                return {
                    'streak': 1,
                    'event_type': 'broken',
                    'metadata': {
                        'days_difference': days_difference,
                        'previous_streak': current_streak,
                        'was_frozen': user.streak_frozen
                    }
                }
        
        # Past date entry (shouldn't happen normally)
        else:
            return {
                'streak': current_streak,
                'event_type': 'past_entry',
                'metadata': {
                    'days_difference': days_difference,
                    'entry_date': entry_date.isoformat()
                }
            }
    
    def use_streak_freeze(self, user_id: str) -> Dict:
        """
        Use a streak freeze for the user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with freeze result
        """
        try:
            user_repo = get_user_repository()
            
            # Try to use freeze
            success = user_repo.use_streak_freeze(user_id)
            
            if success:
                user = user_repo.get_user_by_id(user_id)
                
                # Log the freeze event
                streak_repo = get_streak_event_repository()
                streak_repo.log_event(
                    user_id=user_id,
                    event_type='frozen',
                    streak_count=user.current_streak,
                    metadata={'freeze_count': user.freeze_count}
                )
                
                logger.info(f"Streak frozen for user {user_id}")
                return {
                    'success': True,
                    'message': 'Streak frozen successfully!',
                    'current_streak': user.current_streak,
                    'freeze_count': user.freeze_count,
                    'freezes_remaining': max(0, self.max_freezes - user.freeze_count)
                }
            else:
                return {
                    'success': False,
                    'message': 'No freezes available or user not found',
                    'freeze_count': 0,
                    'freezes_remaining': 0
                }
                
        except Exception as e:
            logger.error(f"Failed to use freeze for user {user_id}: {e}")
            return {
                'success': False,
                'message': f'Error using freeze: {e}',
                'freeze_count': 0,
                'freezes_remaining': 0
            }
    
    def get_streak_status(self, user_id: str) -> Dict:
        """
        Get current streak status for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with current streak information
        """
        try:
            user_repo = get_user_repository()
            achievement_repo = get_achievement_repository()
            
            user = user_repo.get_user_by_id(user_id)
            if not user:
                return self._create_empty_status(user_id)
            
            # Get achievements
            achievements = achievement_repo.get_user_achievements(user_id)
            
            # Check if streak is at risk
            days_since_last_entry = 0
            if user.last_entry_date:
                days_since_last_entry = (date.today() - user.last_entry_date).days
            
            streak_at_risk = days_since_last_entry >= 1 and not user.streak_frozen
            
            return {
                'user_id': user_id,
                'current_streak': user.current_streak,
                'longest_streak': user.longest_streak,
                'total_entries': user.total_entries,
                'last_entry_date': user.last_entry_date.isoformat() if user.last_entry_date else None,
                'days_since_last_entry': days_since_last_entry,
                'streak_frozen': user.streak_frozen,
                'freeze_count': user.freeze_count,
                'freezes_remaining': max(0, self.max_freezes - user.freeze_count),
                'streak_at_risk': streak_at_risk,
                'next_milestone': self._get_next_milestone(user.current_streak),
                'achievements': [
                    {
                        'name': achievement.achievement_name,
                        'description': achievement.description,
                        'badge': achievement.badge_emoji,
                        'earned_at': achievement.earned_at.isoformat(),
                        'streak_when_earned': achievement.streak_count_when_earned
                    }
                    for achievement in achievements
                ],
                'created_at': user.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get streak status for user {user_id}: {e}")
            return self._create_error_status(user_id, str(e))
    
    def get_streak_analytics(self, user_id: str, days: int = 30) -> Dict:
        """
        Get streak analytics for the user
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Dictionary with analytics data
        """
        try:
            streak_repo = get_streak_event_repository()
            
            events = streak_repo.get_user_events(user_id, limit=100)
            
            # Filter events within the specified time period
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_events = [
                event for event in events 
                if event.created_at >= cutoff_date
            ]
            
            # Calculate statistics
            event_types = {}
            streak_progression = []
            
            for event in recent_events:
                event_type = event.event_type
                event_types[event_type] = event_types.get(event_type, 0) + 1
                
                streak_progression.append({
                    'date': event.created_at.date().isoformat(),
                    'streak_count': event.streak_count,
                    'event_type': event_type
                })
            
            # Calculate consistency metrics
            total_events = len(recent_events)
            continued_events = event_types.get('continued', 0)
            broken_events = event_types.get('broken', 0)
            
            consistency_rate = (continued_events / total_events * 100) if total_events > 0 else 0
            
            return {
                'user_id': user_id,
                'analysis_period_days': days,
                'total_events': total_events,
                'event_breakdown': event_types,
                'consistency_rate': round(consistency_rate, 2),
                'streak_progression': streak_progression[-30:],  # Last 30 events
                'average_streak_length': self._calculate_average_streak_length(events),
                'longest_streak_in_period': max([e.streak_count for e in recent_events]) if recent_events else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics for user {user_id}: {e}")
            return {'error': str(e), 'user_id': user_id}
    
    def _get_next_milestone(self, current_streak: int) -> Optional[Dict]:
        """Get the next milestone achievement"""
        for achievement_key, info in ACHIEVEMENTS.items():
            if current_streak < info['streak_required']:
                return {
                    'name': info['name'],
                    'badge': info['badge'],
                    'required_streak': info['streak_required'],
                    'days_remaining': info['streak_required'] - current_streak,
                    'progress_percentage': round((current_streak / info['streak_required']) * 100, 1)
                }
        return None  # Already achieved all milestones
    
    def _calculate_average_streak_length(self, events: List) -> float:
        """Calculate average streak length from events"""
        if not events:
            return 0.0
        
        streak_lengths = []
        current_streak_start = None
        
        for event in reversed(events):  # Process chronologically
            if event.event_type == 'started':
                current_streak_start = 1
            elif event.event_type == 'continued' and current_streak_start is not None:
                current_streak_start += 1
            elif event.event_type == 'broken' and current_streak_start is not None:
                streak_lengths.append(current_streak_start)
                current_streak_start = None
        
        # Add current ongoing streak if exists
        if current_streak_start is not None:
            streak_lengths.append(current_streak_start)
        
        return sum(streak_lengths) / len(streak_lengths) if streak_lengths else 0.0
    
    def _create_empty_status(self, user_id: str) -> Dict:
        """Create empty status for new user"""
        return {
            'user_id': user_id,
            'current_streak': 0,
            'longest_streak': 0,
            'total_entries': 0,
            'last_entry_date': None,
            'days_since_last_entry': 0,
            'streak_frozen': False,
            'freeze_count': 0,
            'freezes_remaining': self.max_freezes,
            'streak_at_risk': False,
            'next_milestone': self._get_next_milestone(0),
            'achievements': [],
            'created_at': None,
            'new_user': True
        }
    
    def _create_error_result(self, user_id: str, error_msg: str) -> Dict:
        """Create error result for streak update"""
        return {
            'user_id': user_id,
            'error': True,
            'message': error_msg,
            'current_streak': 0,
            'longest_streak': 0,
            'total_entries': 0,
            'new_achievements': [],
            'next_milestone': None
        }
    
    def _create_error_status(self, user_id: str, error_msg: str) -> Dict:
        """Create error status"""
        return {
            'user_id': user_id,
            'error': True,
            'message': error_msg,
            'current_streak': 0,
            'longest_streak': 0
        }