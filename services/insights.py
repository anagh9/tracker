"""
Smart Insights Module - Generates behavior and discipline insights
Currently uses mock data, designed for future AI integration
"""


class SmartInsights:
    """
    Generates intelligent insights about user behavior and discipline
    Modular design supports future AI-powered analysis
    """

    @staticmethod
    def generate_daily_insights(user_id: int, tracker_data: dict) -> dict:
        """
        Generate daily insights based on tracker data
        
        Args:
            user_id: User ID
            tracker_data: Aggregated tracker data for the day
        
        Returns:
            {
                "primary_insight": {"title": str, "description": str, "icon": str},
                "insights_list": [{"text": str, "type": "positive|neutral|warning"}],
                "recommendations": [str],
                "trend": {"direction": "up|down|stable", "metric": str}
            }
        """
        insights = {
            "primary_insight": SmartInsights._get_primary_insight(tracker_data),
            "insights_list": SmartInsights._generate_insights_list(tracker_data),
            "recommendations": SmartInsights._generate_recommendations(tracker_data),
            "trend": SmartInsights._calculate_trend(tracker_data),
        }
        return insights

    @staticmethod
    def _get_primary_insight(tracker_data: dict) -> dict:
        """
        Get the main insight for the day
        Mock data implementation
        """
        # Mock data - would be replaced with AI analysis
        mock_insights = [
            {
                "title": "🎯 Consistency Champion",
                "description": "You've been consistently tracking both calories and habits for the past 5 days. This dedication is building strong discipline!",
                "icon": "🏆",
            },
            {
                "title": "📈 Upward Momentum",
                "description": "Your discipline score has improved 15% this week. You're making real progress!",
                "icon": "📊",
            },
            {
                "title": "🌟 Balanced Lifestyle",
                "description": "Great balance between nutrition tracking and habit management today. Your holistic approach is paying off!",
                "icon": "⚖️",
            },
            {
                "title": "💪 Habit Warrior",
                "description": "You've logged your habit tracking consistently. Small wins add up to big changes!",
                "icon": "⚔️",
            },
        ]
        import random
        return random.choice(mock_insights)

    @staticmethod
    def _generate_insights_list(tracker_data: dict) -> list:
        """
        Generate a list of behavioral insights
        Mock data implementation
        """
        insights = []

        # Calorie-related insights
        if tracker_data.get("calorie", {}).get("tracked"):
            insights.append({
                "text": "You logged your meals today. Consistent tracking helps identify patterns!",
                "type": "positive",
            })

        # Vices-related insights
        if tracker_data.get("vices", {}).get("tracked"):
            avoided = tracker_data["vices"].get("avoided_count", 0)
            if avoided > 0:
                insights.append({
                    "text": f"You avoided {avoided} unhealthy habit(s) today. That takes discipline!",
                    "type": "positive",
                })
            else:
                insights.append({
                    "text": "You're tracking your habits. Awareness is the first step to change.",
                    "type": "neutral",
                })

        # Add mock behavioral insights
        mock_insights = [
            {
                "text": "You're most consistent at tracking during morning hours.",
                "type": "neutral",
            },
            {
                "text": "Your discipline score reaches peak levels on weekends.",
                "type": "neutral",
            },
            {
                "text": "Regular tracking increases your consistency by 40% on average.",
                "type": "positive",
            },
        ]

        import random
        insights.extend(random.sample(mock_insights, 1))

        return insights[:3]  # Return top 3 insights

    @staticmethod
    def _generate_recommendations(tracker_data: dict) -> list:
        """
        Generate actionable recommendations
        Mock data implementation
        """
        recommendations = []

        # Check what trackers are active
        calorie_active = tracker_data.get("calorie", {}).get("tracked")
        vices_active = tracker_data.get("vices", {}).get("tracked")

        if not calorie_active and not vices_active:
            recommendations.append("Start logging your meals to track nutrition patterns")
            recommendations.append("Track one habit to build awareness before change")

        if calorie_active and not vices_active:
            recommendations.append("Consider tracking habits to create a holistic view of your discipline")

        if vices_active and not calorie_active:
            recommendations.append("Add calorie tracking for complete health visibility")

        # Add motivational recommendations
        mock_recs = [
            "Schedule a dedicated time each day for tracking - consistency builds discipline",
            "Schedule a dedicated time each day for tracking - consistency builds discipline",
            "Review your weekly insights to identify patterns and celebrate progress",
            "Review your weekly insights to identify patterns and celebrate progress",
            "Set a streak goal: can you log data for 30 consecutive days?",
            "Set a streak goal: can you log data for 30 consecutive days?",
        ]

        import random
        recommendations.extend(random.sample(mock_recs, 5))

        return recommendations

    @staticmethod
    def _calculate_trend(tracker_data: dict) -> dict:
        """
        Calculate behavior trends
        Mock data implementation
        """
        # Mock trend data
        trends = [
            {"direction": "up", "metric": "Discipline Score", "percentage": 12},
            {"direction": "up", "metric": "Tracking Consistency", "percentage": 8},
            {"direction": "stable", "metric": "Daily Average", "percentage": 0},
            {"direction": "down", "metric": "Bad Habits", "percentage": -5},
        ]

        import random
        return random.choice(trends)


class BehaviorAnalysis:
    """
    Analyzes user behavior patterns
    Modular for future ML integration
    """

    @staticmethod
    def get_behavior_summary(user_id: int) -> dict:
        """
        Get summary of user behavior patterns
        Mock data for now
        """
        return {
            "discipline_rating": "Excellent",
            "discipline_rating_icon": "🌟",
            "consistency_score": 85,
            "habit_adherence": 72,
            "tracking_frequency": "Very Consistent",
            "key_strengths": [
                "Consistent daily logging",
                "Balanced tracker usage",
                "Strong motivation",
            ],
            "areas_to_improve": [
                "Weekend consistency",
                "Late-evening tracking",
            ],
        }

    @staticmethod
    def get_weekly_overview(user_id: int) -> dict:
        """
        Get weekly behavior overview
        Mock data for now
        """
        return {
            "total_entries": 47,
            "tracking_days": 6,
            "average_daily_score": 78,
            "streak_days": 5,
            "best_day": "Tuesday",
            "busiest_day": "Wednesday",
            "insights_generated": 12,
        }

    @staticmethod
    def get_comparison(user_id: int) -> dict:
        """
        Get comparison with user's own history
        Mock data for now
        """
        return {
            "this_week_vs_last": {
                "direction": "up",
                "percentage": 15,
                "label": "Better than last week",
            },
            "this_month_vs_last": {
                "direction": "up",
                "percentage": 22,
                "label": "Best month yet!",
            },
            "discipline_trend": "Rising",
        }
