"""
Cost Optimization Helper for Pareng Boyong.

This module implements intelligent cost optimization strategies,
prioritizing FREE services before paid alternatives.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from ..core.config import ParengBoyongConfig


class CostOptimizer:
    """
    Intelligent cost optimization system for Pareng Boyong.
    
    Implements cost-conscious decision making by:
    - Prioritizing FREE services first
    - Tracking daily/monthly spending
    - Suggesting cheaper alternatives
    - Monitoring usage patterns
    - Setting budget alerts
    """
    
    def __init__(self, config: ParengBoyongConfig):
        """
        Initialize cost optimizer.
        
        Args:
            config: Pareng Boyong configuration
        """
        self.config = config
        self.usage_file = config.data_dir / "cost_usage.json"
        self.daily_usage: Dict[str, float] = {}
        self.monthly_usage: Dict[str, float] = {}
        
        # Load existing usage data
        self._load_usage_data()
    
    def _load_usage_data(self):
        """Load usage data from file."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                    self.daily_usage = data.get('daily', {})
                    self.monthly_usage = data.get('monthly', {})
            except Exception:
                # Reset on error
                self.daily_usage = {}
                self.monthly_usage = {}
    
    def _save_usage_data(self):
        """Save usage data to file."""
        try:
            data = {
                'daily': self.daily_usage,
                'monthly': self.monthly_usage,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.usage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Graceful failure
    
    def initialize_session(self, session_id: str):
        """Initialize cost tracking for a session."""
        # Clean up old daily usage (keep last 7 days)
        cutoff_date = datetime.now() - timedelta(days=7)
        self.daily_usage = {
            date: cost for date, cost in self.daily_usage.items()
            if datetime.fromisoformat(date.split('_')[0] if '_' in date else date) > cutoff_date
        }
        self._save_usage_data()
    
    def analyze_request(self, message: str) -> Dict[str, Any]:
        """
        Analyze a request to determine optimal cost strategy.
        
        Args:
            message: User message/request
            
        Returns:
            Analysis with cost optimization recommendations
        """
        analysis = {
            'intent': self._classify_intent(message),
            'cost_budget': self._determine_budget(message),
            'prefer_free': self.config.prefer_free_services,
            'requires_multiple_tools': self._check_complexity(message),
            'quality_requirements': self._assess_quality_needs(message)
        }
        
        return analysis
    
    def _classify_intent(self, message: str) -> str:
        """Classify the intent of the message."""
        message_lower = message.lower()
        
        # Video generation
        if any(word in message_lower for word in ['video', 'animation', 'movie', 'clip']):
            return 'video_generation'
        
        # Image generation
        if any(word in message_lower for word in ['image', 'picture', 'photo', 'drawing', 'illustration']):
            return 'image_generation'
        
        # Audio generation
        if any(word in message_lower for word in ['audio', 'voice', 'music', 'sound', 'tts', 'speak']):
            return 'audio_generation'
        
        # Code execution
        if any(word in message_lower for word in ['code', 'run', 'execute', 'script', 'programming']):
            return 'code_execution'
        
        # General chat
        return 'general_chat'
    
    def _determine_budget(self, message: str) -> float:
        """Determine appropriate budget based on message."""
        message_lower = message.lower()
        
        # High budget keywords
        if any(word in message_lower for word in ['professional', 'commercial', 'client', 'premium']):
            return min(0.10, self.config.max_daily_cost * 0.2)
        
        # Medium budget keywords
        if any(word in message_lower for word in ['quality', 'important', 'presentation']):
            return min(0.05, self.config.max_daily_cost * 0.1)
        
        # Default: prefer FREE or very low cost
        return 0.01
    
    def _check_complexity(self, message: str) -> bool:
        """Check if request requires multiple tools."""
        complexity_indicators = [
            'and', 'then', 'also', 'plus', 'with', 'including',
            'multiple', 'several', 'both', 'all', 'various'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in complexity_indicators)
    
    def _assess_quality_needs(self, message: str) -> str:
        """Assess quality requirements from message."""
        message_lower = message.lower()
        
        # High quality indicators
        if any(word in message_lower for word in ['professional', 'high quality', 'premium', 'commercial']):
            return 'high'
        
        # Standard quality indicators
        if any(word in message_lower for word in ['good', 'nice', 'quality', 'presentation']):
            return 'standard'
        
        # Basic quality (prefer FREE)
        if any(word in message_lower for word in ['quick', 'simple', 'basic', 'test', 'draft']):
            return 'basic'
        
        return 'standard'
    
    def track_usage(self, session_id: str, cost: float):
        """
        Track usage and costs for a session.
        
        Args:
            session_id: Session identifier
            cost: Cost incurred
        """
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        # Track daily usage
        daily_key = f"{today}_{session_id}"
        self.daily_usage[daily_key] = self.daily_usage.get(daily_key, 0) + cost
        
        # Track monthly usage
        self.monthly_usage[month] = self.monthly_usage.get(month, 0) + cost
        
        # Save updated data
        self._save_usage_data()
        
        # Check for budget alerts
        self._check_budget_alerts(today, month)
    
    def _check_budget_alerts(self, today: str, month: str):
        """Check and alert if approaching budget limits."""
        daily_total = sum(
            cost for date_session, cost in self.daily_usage.items()
            if date_session.startswith(today)
        )
        
        monthly_total = self.monthly_usage.get(month, 0)
        
        # Daily budget alert
        if daily_total > self.config.cost_warning_threshold:
            print(f"💰 Daily cost alert: ${daily_total:.3f} (Limit: ${self.config.max_daily_cost})")
        
        # Monthly budget alert (assume monthly limit is 30x daily)
        monthly_limit = self.config.max_daily_cost * 30
        if monthly_total > monthly_limit * 0.8:
            print(f"📊 Monthly cost alert: ${monthly_total:.2f} (80% of ${monthly_limit:.2f})")
    
    def get_daily_usage(self, date: Optional[str] = None) -> float:
        """Get daily usage for a specific date."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        return sum(
            cost for date_session, cost in self.daily_usage.items()
            if date_session.startswith(date)
        )
    
    def get_monthly_usage(self, month: Optional[str] = None) -> float:
        """Get monthly usage for a specific month."""
        if month is None:
            month = datetime.now().strftime('%Y-%m')
            
        return self.monthly_usage.get(month, 0)
    
    def can_afford(self, estimated_cost: float) -> bool:
        """Check if we can afford an operation."""
        today = datetime.now().strftime('%Y-%m-%d')
        current_daily = self.get_daily_usage(today)
        
        return (current_daily + estimated_cost) <= self.config.max_daily_cost
    
    def suggest_alternatives(self, original_tool: str, budget: float) -> List[str]:
        """
        Suggest cheaper alternatives for a tool.
        
        Args:
            original_tool: Original tool name
            budget: Available budget
            
        Returns:
            List of alternative tools in cost order
        """
        alternatives = {
            'advanced_video_generator': [
                'cost_optimized_video_generator',
                'trending_video_generator', 
                'simple_video_generator'
            ],
            'trending_video_generator': [
                'cost_optimized_video_generator',
                'simple_video_generator'
            ],
            'imagen4_generator': [
                'multimedia_generator',
                'image_generator'
            ],
            'elevenlabs_tts': [
                'filipino_tts',
                'system_tts'
            ]
        }
        
        return alternatives.get(original_tool, [])
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Generate cost usage report."""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        daily_usage = self.get_daily_usage(today)
        monthly_usage = self.get_monthly_usage(month)
        
        # Calculate savings (assume we saved 80% by using FREE services)
        estimated_premium_cost = monthly_usage / 0.2  # If we used only 20% paid services
        estimated_savings = estimated_premium_cost - monthly_usage
        
        return {
            'daily_usage': daily_usage,
            'daily_limit': self.config.max_daily_cost,
            'daily_remaining': max(0, self.config.max_daily_cost - daily_usage),
            'monthly_usage': monthly_usage,
            'estimated_savings': max(0, estimated_savings),
            'optimization_active': self.config.cost_optimization,
            'prefer_free': self.config.prefer_free_services,
            'last_7_days': [
                {
                    'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'cost': self.get_daily_usage(
                        (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    )
                }
                for i in range(7)
            ]
        }
    
    def get_settings(self) -> Dict[str, Any]:
        """Get cost optimization settings."""
        return {
            'enabled': self.config.cost_optimization,
            'prefer_free': self.config.prefer_free_services,
            'daily_limit': self.config.max_daily_cost,
            'warning_threshold': self.config.cost_warning_threshold,
            'auto_escalate': self.config.auto_escalate_quality,
            'current_usage': self.get_daily_usage(),
        }
    
    def __str__(self) -> str:
        return f"CostOptimizer(daily_limit=${self.config.max_daily_cost}, prefer_free={self.config.prefer_free_services})"