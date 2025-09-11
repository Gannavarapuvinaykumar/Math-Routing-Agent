# Performance Metrics and Analytics for Math Routing Agent

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import statistics

class PerformanceAnalytics:
    """Comprehensive performance tracking and analytics system"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.request_history: deque = deque(maxlen=max_history)
        self.route_performance: Dict[str, List[float]] = defaultdict(list)
        self.error_tracking: Dict[str, int] = defaultdict(int)
        self.user_satisfaction: Dict[str, List[int]] = defaultdict(list)
        self.response_quality: Dict[str, List[float]] = defaultdict(list)
        self.concurrent_requests = 0
        self.peak_concurrent = 0
        
    def log_request_start(self, query: str, user_id: str = "anonymous") -> str:
        """Log the start of a request and return tracking ID"""
        tracking_id = f"req_{int(time.time() * 1000)}_{hash(query) % 10000}"
        
        request_data = {
            'tracking_id': tracking_id,
            'query': query,
            'user_id': user_id,
            'start_time': time.time(),
            'timestamp': datetime.now().isoformat(),
            'route': None,
            'response_time': None,
            'success': None,
            'error': None,
            'confidence': None
        }
        
        self.request_history.append(request_data)
        self.concurrent_requests += 1
        self.peak_concurrent = max(self.peak_concurrent, self.concurrent_requests)
        
        return tracking_id
    
    def log_request_end(self, tracking_id: str, route: str, success: bool, 
                       confidence: float = None, error: str = None) -> None:
        """Log the completion of a request"""
        end_time = time.time()
        
        # Find the request in history
        for request_data in reversed(self.request_history):
            if request_data['tracking_id'] == tracking_id:
                response_time = end_time - request_data['start_time']
                
                request_data.update({
                    'route': route,
                    'response_time': response_time,
                    'success': success,
                    'confidence': confidence,
                    'error': error,
                    'end_time': end_time
                })
                
                # Track route performance
                if success and response_time:
                    self.route_performance[route].append(response_time)
                
                # Track errors
                if not success and error:
                    self.error_tracking[error] += 1
                
                break
        
        self.concurrent_requests = max(0, self.concurrent_requests - 1)
    
    def log_user_feedback(self, tracking_id: str, rating: int, feedback_text: str = "") -> None:
        """Log user feedback for quality tracking"""
        for request_data in reversed(self.request_history):
            if request_data['tracking_id'] == tracking_id:
                route = request_data.get('route', 'unknown')
                self.user_satisfaction[route].append(rating)
                
                # Calculate response quality score based on multiple factors
                quality_score = self._calculate_quality_score(request_data, rating, feedback_text)
                self.response_quality[route].append(quality_score)
                
                request_data['user_rating'] = rating
                request_data['user_feedback'] = feedback_text
                request_data['quality_score'] = quality_score
                break
    
    def _calculate_quality_score(self, request_data: Dict, rating: int, feedback: str) -> float:
        """Calculate comprehensive quality score (0-100)"""
        # Base score from user rating (1-5 scale to 0-100)
        base_score = ((rating - 1) / 4) * 100
        
        # Adjust based on response time (faster is better)
        response_time = request_data.get('response_time', 5.0)
        time_penalty = min(20, max(0, (response_time - 1.0) * 5))  # Penalty for slow responses
        
        # Adjust based on confidence
        confidence = request_data.get('confidence', 0.5)
        confidence_bonus = (confidence - 0.5) * 20  # Bonus/penalty for confidence
        
        # Adjust based on route (KB is generally more reliable)
        route = request_data.get('route', 'unknown')
        route_modifiers = {
            'KB': 5,      # Knowledge base is most reliable
            'Web': 0,     # Web search is neutral
            'AI': -2,     # AI generation has slight uncertainty
            'Human': 10   # Human expert is most accurate but slower
        }
        route_modifier = route_modifiers.get(route, 0)
        
        # Sentiment analysis of feedback text (simplified)
        feedback_modifier = 0
        if feedback:
            positive_words = ['good', 'great', 'excellent', 'helpful', 'accurate', 'clear', 'perfect']
            negative_words = ['bad', 'wrong', 'unclear', 'confusing', 'incorrect', 'useless']
            
            feedback_lower = feedback.lower()
            positive_count = sum(1 for word in positive_words if word in feedback_lower)
            negative_count = sum(1 for word in negative_words if word in feedback_lower)
            
            feedback_modifier = (positive_count - negative_count) * 5
        
        final_score = max(0, min(100, 
            base_score - time_penalty + confidence_bonus + route_modifier + feedback_modifier
        ))
        
        return round(final_score, 2)
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive performance analytics"""
        cutoff_time = time.time() - (hours * 3600)
        recent_requests = [
            req for req in self.request_history 
            if req.get('start_time', 0) > cutoff_time
        ]
        
        if not recent_requests:
            return {"message": f"No requests in the last {hours} hours"}
        
        # Basic metrics
        total_requests = len(recent_requests)
        successful_requests = len([req for req in recent_requests if req.get('success')])
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        # Response time analytics
        response_times = [req['response_time'] for req in recent_requests if req.get('response_time')]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0
        
        # Route distribution
        route_distribution = defaultdict(int)
        for req in recent_requests:
            route = req.get('route', 'unknown')
            route_distribution[route] += 1
        
        # Route performance
        route_stats = {}
        for route in ['KB', 'Web', 'AI', 'Human']:
            route_requests = [req for req in recent_requests if req.get('route') == route]
            if route_requests:
                route_times = [req['response_time'] for req in route_requests if req.get('response_time')]
                route_success = len([req for req in route_requests if req.get('success')])
                
                route_stats[route] = {
                    'count': len(route_requests),
                    'success_rate': (route_success / len(route_requests)) * 100,
                    'avg_response_time': statistics.mean(route_times) if route_times else 0,
                    'satisfaction': statistics.mean(self.user_satisfaction[route]) if self.user_satisfaction[route] else 0,
                    'quality_score': statistics.mean(self.response_quality[route]) if self.response_quality[route] else 0
                }
        
        # Error analysis
        error_summary = dict(self.error_tracking)
        
        # Quality metrics
        overall_satisfaction = []
        overall_quality = []
        for route_ratings in self.user_satisfaction.values():
            overall_satisfaction.extend(route_ratings)
        for route_quality in self.response_quality.values():
            overall_quality.extend(route_quality)
        
        return {
            'time_period': f"Last {hours} hours",
            'total_requests': total_requests,
            'success_rate': round(success_rate, 2),
            'avg_response_time': round(avg_response_time, 3),
            'p95_response_time': round(p95_response_time, 3),
            'concurrent_requests': self.concurrent_requests,
            'peak_concurrent': self.peak_concurrent,
            'route_distribution': dict(route_distribution),
            'route_performance': route_stats,
            'error_summary': error_summary,
            'user_satisfaction': {
                'average_rating': round(statistics.mean(overall_satisfaction), 2) if overall_satisfaction else 0,
                'total_ratings': len(overall_satisfaction),
                'rating_distribution': self._get_rating_distribution(overall_satisfaction)
            },
            'quality_metrics': {
                'average_quality_score': round(statistics.mean(overall_quality), 2) if overall_quality else 0,
                'quality_by_route': {
                    route: round(statistics.mean(scores), 2) 
                    for route, scores in self.response_quality.items() if scores
                }
            },
            'system_health': self._calculate_system_health(success_rate, avg_response_time, overall_satisfaction)
        }
    
    def _get_rating_distribution(self, ratings: List[int]) -> Dict[int, int]:
        """Get distribution of user ratings"""
        distribution = defaultdict(int)
        for rating in ratings:
            distribution[rating] += 1
        return dict(distribution)
    
    def _calculate_system_health(self, success_rate: float, avg_response_time: float, 
                                satisfaction: List[int]) -> Dict[str, Any]:
        """Calculate overall system health score"""
        # Success rate component (0-40 points)
        success_score = min(40, success_rate * 0.4)
        
        # Response time component (0-30 points)
        # Ideal response time is under 2 seconds
        time_score = max(0, 30 - (avg_response_time - 2.0) * 10) if avg_response_time > 2.0 else 30
        
        # User satisfaction component (0-30 points)
        avg_satisfaction = statistics.mean(satisfaction) if satisfaction else 3.0
        satisfaction_score = ((avg_satisfaction - 1) / 4) * 30
        
        overall_health = success_score + time_score + satisfaction_score
        
        health_status = "Excellent" if overall_health >= 90 else \
                       "Good" if overall_health >= 75 else \
                       "Fair" if overall_health >= 60 else \
                       "Poor"
        
        return {
            'overall_score': round(overall_health, 1),
            'status': health_status,
            'components': {
                'success_rate_score': round(success_score, 1),
                'response_time_score': round(time_score, 1),
                'satisfaction_score': round(satisfaction_score, 1)
            },
            'recommendations': self._get_health_recommendations(success_score, time_score, satisfaction_score)
        }
    
    def _get_health_recommendations(self, success_score: float, time_score: float, 
                                  satisfaction_score: float) -> List[str]:
        """Generate system improvement recommendations"""
        recommendations = []
        
        if success_score < 30:
            recommendations.append("Improve error handling and fallback mechanisms")
        if time_score < 20:
            recommendations.append("Optimize response times with caching and performance tuning")
        if satisfaction_score < 20:
            recommendations.append("Enhance response quality and user experience")
        
        if not recommendations:
            recommendations.append("System is performing well - maintain current standards")
        
        return recommendations

# Global analytics instance
performance_analytics = PerformanceAnalytics()
