"""
Gamification Module - Calculates and tracks discipline/health score
Supports scalable tracker integration with modular scoring
"""

from datetime import date, timedelta


class GamificationEngine:
    """
    Modular gamification system that calculates daily health score
    Designed to work with any tracker type
    """

    # Achievement thresholds
    ACHIEVEMENT_LEVELS = {
        1: {"min_score": 0, "title": "Novice", "badge": "🌱"},
        2: {"min_score": 100, "title": "Committed", "badge": "🔥"},
        3: {"min_score": 300, "title": "Dedicated", "badge": "⛓️"},
        4: {"min_score": 500, "title": "Master", "badge": "👑"},
    }

    @staticmethod
    def calculate_daily_score(tracker_data: dict) -> dict:
        """
        Calculate daily health/discipline score from tracker data
        
        Args:
            tracker_data: Dictionary with tracker stats
                {
                    "calorie": {"tracked": bool, "adherence": 0-100},
                    "vices": {"avoided_count": int, "total_tracked": int},
                    ...
                }
        
        Returns:
            {
                "score": int (0-100),
                "breakdown": dict,
                "message": str,
                "level": int,
                "next_level_points": int
            }
        """
        score = 0
        breakdown = {}

        # Calorie Tracker (max 40 points)
        if "calorie" in tracker_data and tracker_data["calorie"]:
            calorie_score = GamificationEngine._score_calorie(tracker_data["calorie"])
            breakdown["calorie"] = calorie_score
            score += calorie_score

        # Vices/Habits Tracker (max 30 points)
        if "vices" in tracker_data and tracker_data["vices"]:
            vices_score = GamificationEngine._score_vices(tracker_data["vices"])
            breakdown["vices"] = vices_score
            score += vices_score

        # Financial Tracker (max 20 points)
        if "financial" in tracker_data and tracker_data["financial"]:
            financial_score = GamificationEngine._score_financial(tracker_data["financial"])
            breakdown["financial"] = financial_score
            score += financial_score

        # Consistency bonus (max 20 points)
        consistency_bonus = GamificationEngine._calculate_consistency_bonus(tracker_data)
        breakdown["consistency"] = consistency_bonus
        score += consistency_bonus

        # Streak bonus (max 10 points)
        streak_bonus = GamificationEngine._calculate_streak_bonus(tracker_data.get("streak", 0))
        breakdown["streak"] = streak_bonus
        score += streak_bonus

        # Cap score at 100
        score = min(score, 100)

        # Generate motivational message
        message = GamificationEngine._get_message(score)

        return {
            "score": score,
            "breakdown": breakdown,
            "message": message,
            "level": GamificationEngine._get_level(score),
            "level_title": GamificationEngine._get_level_title(score),
            "level_badge": GamificationEngine._get_level_badge(score),
            "progress_to_next": GamificationEngine._get_progress_to_next_level(score),
        }

    @staticmethod
    def _score_calorie(calorie_data: dict) -> int:
        """Score calorie tracking (max 40 points)"""
        if not calorie_data:
            return 0

        score = 0
        
        # 20 points for logging today
        if calorie_data.get("tracked"):
            score += 20

        # Up to 20 points for adherence to target
        adherence = calorie_data.get("adherence", 0)
        if adherence > 0:
            score += min(20, int(adherence / 5))

        return min(score, 40)

    @staticmethod
    def _score_vices(vices_data: dict) -> int:
        """Score vices/habits tracking (max 30 points)"""
        if not vices_data:
            return 0

        score = 0

        # 20 points for tracking
        if vices_data.get("tracked"):
            score += 20

        # 10 points if avoided habits
        avoided = vices_data.get("avoided_count", 0)
        if avoided > 0:
            score += min(10, avoided * 2)

        return min(score, 30)

    @staticmethod
    def _score_financial(financial_data: dict) -> int:
        """Score expense tracking (max 20 points)."""
        if not financial_data:
            return 0

        score = 0
        if financial_data.get("tracked"):
            score += 12

        entry_count = financial_data.get("entries_count", 0)
        if entry_count:
            score += min(8, entry_count * 2)

        return min(score, 20)

    @staticmethod
    def _calculate_consistency_bonus(tracker_data: dict) -> int:
        """Bonus for using multiple trackers (max 20 points)"""
        active_trackers = sum(1 for tracker in ["calorie", "vices", "financial"]
                             if tracker_data.get(tracker, {}).get("tracked"))
        return min(20, active_trackers * 7)

    @staticmethod
    def _calculate_streak_bonus(streak: int) -> int:
        """Bonus for maintaining streak (max 10 points)"""
        if streak >= 7:
            return 10
        elif streak >= 3:
            return 5
        elif streak > 0:
            return 2
        return 0

    @staticmethod
    def _get_level(score: int) -> int:
        """Get level based on score"""
        for level in sorted(GamificationEngine.ACHIEVEMENT_LEVELS.keys(), reverse=True):
            if score >= GamificationEngine.ACHIEVEMENT_LEVELS[level]["min_score"]:
                return level
        return 1

    @staticmethod
    def _get_level_title(score: int) -> str:
        """Get level title"""
        level = GamificationEngine._get_level(score)
        return GamificationEngine.ACHIEVEMENT_LEVELS[level]["title"]

    @staticmethod
    def _get_level_badge(score: int) -> str:
        """Get level badge emoji"""
        level = GamificationEngine._get_level(score)
        return GamificationEngine.ACHIEVEMENT_LEVELS[level]["badge"]

    @staticmethod
    def _get_progress_to_next_level(score: int) -> dict:
        """Get progress info for next level"""
        current_level = GamificationEngine._get_level(score)
        next_level = current_level + 1

        if next_level not in GamificationEngine.ACHIEVEMENT_LEVELS:
            return {"current": 100, "next": 100, "remaining": 0}

        current_threshold = GamificationEngine.ACHIEVEMENT_LEVELS[current_level]["min_score"]
        next_threshold = GamificationEngine.ACHIEVEMENT_LEVELS[next_level]["min_score"]

        progress = score - current_threshold
        total = next_threshold - current_threshold
        remaining = next_threshold - score

        return {
            "current": current_threshold,
            "next": next_threshold,
            "progress": progress,
            "total": total,
            "remaining": max(0, remaining),
            "percentage": min(100, int((progress / total * 100) if total > 0 else 100)),
        }

    @staticmethod
    def _get_message(score: int) -> str:
        """Get motivational message based on score"""
        if score >= 90:
            return "🌟 Exceptional discipline! You're crushing it!"
        elif score >= 75:
            return "✨ Outstanding effort! Keep up the momentum!"
        elif score >= 60:
            return "🔥 Great work! You're staying consistent!"
        elif score >= 45:
            return "💪 Good effort! Keep pushing forward!"
        elif score >= 30:
            return "🚀 You're making progress! Keep it up!"
        else:
            return "✅ Every day is a new opportunity to improve!"


class StreakTracker:
    """
    Tracks user streaks across different metrics
    Currently using mock data, easily extensible
    """

    @staticmethod
    def get_user_streaks(user_id: int) -> dict:
        """
        Get current streaks for user
        Returns mock data structure for now
        """
        # Mock data - in future, this would query actual tracker data
        return {
            "daily_checkin": 7,
            "calorie_logging": 5,
            "vices_tracking": 3,
            "financial_logging": 4,
            "consistent_week": True,
            "all_trackers_active": 5,
        }

    @staticmethod
    def get_achievements(user_id: int) -> list:
        """
        Get user achievements/badges
        Currently mock data
        """
        return [
            {
                "title": "Week Warrior",
                "description": "Logged data for 7 consecutive days",
                "badge": "🗓️",
                "unlocked": True,
                "date": "2024-03-20",
            },
            {
                "title": "Health Alert",
                "description": "Track both calories and habits",
                "badge": "🏥",
                "unlocked": True,
                "date": "2024-03-15",
            },
            {
                "title": "Money Mapped",
                "description": "Log expenses or import a statement",
                "badge": "💳",
                "unlocked": True,
                "date": "2024-03-18",
            },
            {
                "title": "Discipline Master",
                "description": "Score 90+ on daily discipline score",
                "badge": "👑",
                "unlocked": False,
                "date": None,
            },
        ]
