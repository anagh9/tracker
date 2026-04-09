"""
Services module - Business logic and utilities
Includes gamification, insights, and other service layers
"""

from .gamification import GamificationEngine, StreakTracker
from .insights import SmartInsights, BehaviorAnalysis
from .personalization import PersonalizationService
from .calorie_goals import CalorieGoalService

__all__ = [
    'GamificationEngine',
    'StreakTracker',
    'SmartInsights',
    'BehaviorAnalysis',
    'PersonalizationService',
    'CalorieGoalService',
]
