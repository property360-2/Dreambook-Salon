"""
Chatbot Analytics Engine - Provides insights on chatbot performance,
conversation patterns, and recommendations for improvement.
"""
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from collections import Counter
from .models import ConversationHistory


class ChatbotAnalytics:
    """
    Analyzes chatbot conversations and provides performance metrics,
    trends, and recommendations.
    """

    @staticmethod
    def get_overall_stats(days=30):
        """
        Get overall chatbot statistics for the past N days.

        Returns:
            dict: Comprehensive statistics
        """
        since = timezone.now() - timedelta(days=days)
        conversations = ConversationHistory.objects.filter(created_at__gte=since)

        total_messages = conversations.count()
        avg_confidence = conversations.aggregate(
            avg_conf=Avg('confidence_score')
        )['avg_conf'] or 0.0

        # Helpful feedback stats
        feedback_stats = conversations.aggregate(
            total_feedback=Count('was_helpful'),
            helpful_count=Count('was_helpful', filter=Q(was_helpful=True)),
            unhelpful_count=Count('was_helpful', filter=Q(was_helpful=False))
        )

        helpful_rate = 0.0
        if feedback_stats['total_feedback'] > 0:
            helpful_rate = (feedback_stats['helpful_count'] / feedback_stats['total_feedback']) * 100

        return {
            'total_messages': total_messages,
            'average_confidence': round(avg_confidence, 2),
            'helpful_responses': feedback_stats['helpful_count'],
            'unhelpful_responses': feedback_stats['unhelpful_count'],
            'feedback_rate': round((feedback_stats['total_feedback'] / max(total_messages, 1)) * 100, 1),
            'helpfulness_percentage': round(helpful_rate, 1),
            'period_days': days,
        }

    @staticmethod
    def get_intent_distribution(days=30, top_n=10):
        """
        Get distribution of intents detected in conversations.

        Returns:
            dict: Intent names with counts and percentages
        """
        since = timezone.now() - timedelta(days=days)
        conversations = ConversationHistory.objects.filter(
            created_at__gte=since,
            intent_detected__isnull=False
        ).exclude(intent_detected='')

        intent_counts = conversations.values('intent_detected').annotate(
            count=Count('intent_detected')
        ).order_by('-count')[:top_n]

        total = conversations.count()
        results = []
        for item in intent_counts:
            results.append({
                'intent': item['intent_detected'],
                'count': item['count'],
                'percentage': round((item['count'] / max(total, 1)) * 100, 1),
            })

        return {
            'intents': results,
            'total_conversations': total,
            'period_days': days,
        }

    @staticmethod
    def get_confidence_distribution(days=30):
        """
        Get distribution of confidence scores.

        Returns:
            dict: Confidence tiers with counts
        """
        since = timezone.now() - timedelta(days=days)
        conversations = ConversationHistory.objects.filter(created_at__gte=since)

        total = conversations.count()

        high_confidence = conversations.filter(confidence_score__gte=0.85).count()
        medium_confidence = conversations.filter(
            confidence_score__gte=0.70, confidence_score__lt=0.85
        ).count()
        low_confidence = conversations.filter(confidence_score__lt=0.70).count()

        return {
            'high_confidence': {
                'count': high_confidence,
                'percentage': round((high_confidence / max(total, 1)) * 100, 1),
                'threshold': '≥ 0.85'
            },
            'medium_confidence': {
                'count': medium_confidence,
                'percentage': round((medium_confidence / max(total, 1)) * 100, 1),
                'threshold': '0.70 - 0.85'
            },
            'low_confidence': {
                'count': low_confidence,
                'percentage': round((low_confidence / max(total, 1)) * 100, 1),
                'threshold': '< 0.70'
            },
            'total': total,
        }

    @staticmethod
    def get_problematic_intents(days=30, threshold=0.70):
        """
        Identify intents with low average confidence (needs improvement).

        Returns:
            list: Intents that are frequently misunderstood
        """
        since = timezone.now() - timedelta(days=days)
        problem_intents = ConversationHistory.objects.filter(
            created_at__gte=since,
            intent_detected__isnull=False
        ).exclude(intent_detected='').values('intent_detected').annotate(
            avg_confidence=Avg('confidence_score'),
            count=Count('intent_detected')
        ).filter(
            avg_confidence__lt=threshold
        ).order_by('avg_confidence')[:10]

        results = []
        for item in problem_intents:
            results.append({
                'intent': item['intent_detected'],
                'average_confidence': round(item['avg_confidence'], 2),
                'occurrences': item['count'],
                'recommendation': f"Improve patterns/training for {item['intent_detected']}"
            })

        return results

    @staticmethod
    def get_user_satisfaction(days=30):
        """
        Get user satisfaction metrics based on feedback.

        Returns:
            dict: Satisfaction statistics
        """
        since = timezone.now() - timedelta(days=days)
        conversations = ConversationHistory.objects.filter(
            created_at__gte=since,
            was_helpful__isnull=False
        )

        total_feedback = conversations.count()
        helpful = conversations.filter(was_helpful=True).count()
        unhelpful = conversations.filter(was_helpful=False).count()

        satisfaction_rate = 0.0
        if total_feedback > 0:
            satisfaction_rate = (helpful / total_feedback) * 100

        return {
            'total_responses_rated': total_feedback,
            'helpful_count': helpful,
            'unhelpful_count': unhelpful,
            'satisfaction_percentage': round(satisfaction_rate, 1),
            'improvement_needed': unhelpful,
            'period_days': days,
        }

    @staticmethod
    def get_session_analytics(days=30):
        """
        Analyze conversation sessions.

        Returns:
            dict: Session statistics
        """
        since = timezone.now() - timedelta(days=days)
        conversations = ConversationHistory.objects.filter(created_at__gte=since)

        total_sessions = conversations.values('session_id').distinct().count()
        avg_messages_per_session = conversations.count() / max(total_sessions, 1)

        # Find longest/shortest sessions
        session_lengths = conversations.values('session_id').annotate(
            message_count=Count('id')
        ).order_by('-message_count')

        longest_session = session_lengths.first()
        shortest_session = session_lengths.last()

        return {
            'total_sessions': total_sessions,
            'average_messages_per_session': round(avg_messages_per_session, 1),
            'longest_session_messages': longest_session['message_count'] if longest_session else 0,
            'shortest_session_messages': shortest_session['message_count'] if shortest_session else 0,
            'period_days': days,
        }

    @staticmethod
    def get_trends(days=30):
        """
        Get trends in chatbot usage and performance over time.

        Returns:
            dict: Trend analysis by week
        """
        since = timezone.now() - timedelta(days=days)
        conversations = ConversationHistory.objects.filter(created_at__gte=since)

        # Group by week
        from django.db.models.functions import TruncWeek

        weekly_stats = conversations.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            message_count=Count('id'),
            avg_confidence=Avg('confidence_score')
        ).order_by('week')

        trends = []
        for week in weekly_stats:
            trends.append({
                'week': week['week'].strftime('%Y-%m-%d') if week['week'] else 'Unknown',
                'message_count': week['message_count'],
                'average_confidence': round(week['avg_confidence'], 2),
            })

        return {
            'weekly_trends': trends,
            'period_days': days,
        }

    @staticmethod
    def get_recommendations():
        """
        Generate recommendations based on analytics.

        Returns:
            list: Actionable recommendations
        """
        recommendations = []

        # Check confidence levels
        low_confidence_intents = ChatbotAnalytics.get_problematic_intents()
        if low_confidence_intents:
            recommendations.append({
                'category': 'Intent Recognition',
                'priority': 'high',
                'title': 'Improve Low-Confidence Intent Detection',
                'description': f"Found {len(low_confidence_intents)} intents with low confidence scores",
                'action': 'Review and improve patterns for: ' + ', '.join([i['intent'] for i in low_confidence_intents[:3]]),
            })

        # Check satisfaction
        satisfaction = ChatbotAnalytics.get_user_satisfaction()
        if satisfaction['satisfaction_percentage'] < 70:
            recommendations.append({
                'category': 'User Satisfaction',
                'priority': 'high',
                'title': 'Low User Satisfaction Detected',
                'description': f"Only {satisfaction['satisfaction_percentage']}% of rated responses were helpful",
                'action': 'Review unhelpful responses and improve response generation logic',
            })
        elif satisfaction['satisfaction_percentage'] > 85:
            recommendations.append({
                'category': 'User Satisfaction',
                'priority': 'low',
                'title': 'High User Satisfaction!',
                'description': f"Great job! {satisfaction['satisfaction_percentage']}% of users found responses helpful",
                'action': 'Continue current approach and monitor for regressions',
            })

        # Check feedback collection
        overall = ChatbotAnalytics.get_overall_stats()
        if overall['feedback_rate'] < 10:
            recommendations.append({
                'category': 'Data Collection',
                'priority': 'medium',
                'title': 'Increase Feedback Collection',
                'description': f"Only {overall['feedback_rate']}% of users are rating responses",
                'action': 'Encourage more user feedback to improve analytics',
            })

        # Check session patterns
        sessions = ChatbotAnalytics.get_session_analytics()
        if sessions['average_messages_per_session'] < 2:
            recommendations.append({
                'category': 'Engagement',
                'priority': 'medium',
                'title': 'Short Session Duration',
                'description': "Users are leaving conversations quickly",
                'action': 'Improve first-response quality and add clarifying questions',
            })

        return recommendations

    @staticmethod
    def get_dashboard_data():
        """
        Get all dashboard data in one call.

        Returns:
            dict: Complete dashboard data
        """
        return {
            'overall_stats': ChatbotAnalytics.get_overall_stats(),
            'intent_distribution': ChatbotAnalytics.get_intent_distribution(),
            'confidence_distribution': ChatbotAnalytics.get_confidence_distribution(),
            'user_satisfaction': ChatbotAnalytics.get_user_satisfaction(),
            'session_analytics': ChatbotAnalytics.get_session_analytics(),
            'trends': ChatbotAnalytics.get_trends(),
            'recommendations': ChatbotAnalytics.get_recommendations(),
            'problematic_intents': ChatbotAnalytics.get_problematic_intents(),
        }
