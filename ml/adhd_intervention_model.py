"""
ADHD Intervention Model - XGBoost
Predicts task abandonment probability and recommends interventions
For: Ariel Shapira Life OS
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import json

class ADHDInterventionModel:
    def __init__(self):
        self.model = None
        self.feature_names = [
            'task_complexity',          # 1-10
            'instruction_clarity',      # 1-10
            'estimated_minutes',        # Task duration estimate
            'hour_of_day',              # 0-23
            'day_of_week',              # 0-6 (Mon-Sun)
            'minutes_since_start',      # How long task has been active
            'tasks_completed_today',    # Momentum indicator
            'tasks_abandoned_today',    # Pattern indicator
            'is_peak_focus_time',       # 9-11 AM = 1
            'is_energy_dip_time',       # 2-4 PM = 1
            'domain_business',          # One-hot
            'domain_michael',           # One-hot
            'domain_family',            # One-hot
            'domain_personal',          # One-hot
            'context_switches_today',   # ADHD risk factor
            'avg_task_duration_week',   # Historical pattern
            'completion_rate_week',     # Historical pattern
            'last_break_minutes_ago',   # Fatigue indicator
            'is_shabbat',               # F-Su considerations
            'consecutive_focus_minutes' # Current focus streak
        ]
        
    def extract_features(self, task_data: dict) -> np.array:
        """Extract features from task data for prediction"""
        now = datetime.now()
        hour = now.hour
        
        features = [
            task_data.get('task_complexity', 5),
            task_data.get('instruction_clarity', 5),
            task_data.get('estimated_minutes', 30),
            hour,
            now.weekday(),
            task_data.get('minutes_since_start', 0),
            task_data.get('tasks_completed_today', 0),
            task_data.get('tasks_abandoned_today', 0),
            1 if 9 <= hour <= 11 else 0,  # Peak focus
            1 if 14 <= hour <= 16 else 0,  # Energy dip
            1 if task_data.get('domain') == 'BUSINESS' else 0,
            1 if task_data.get('domain') == 'MICHAEL' else 0,
            1 if task_data.get('domain') == 'FAMILY' else 0,
            1 if task_data.get('domain') == 'PERSONAL' else 0,
            task_data.get('context_switches_today', 0),
            task_data.get('avg_task_duration_week', 25),
            task_data.get('completion_rate_week', 0.7),
            task_data.get('last_break_minutes_ago', 60),
            1 if now.weekday() >= 4 else 0,  # Fri-Sun
            task_data.get('consecutive_focus_minutes', 0)
        ]
        return np.array(features).reshape(1, -1)
    
    def predict_abandonment_risk(self, task_data: dict) -> dict:
        """Predict abandonment probability and recommend intervention"""
        features = self.extract_features(task_data)
        
        # If no trained model, use heuristic scoring
        if self.model is None:
            risk_score = self._heuristic_risk_score(task_data)
        else:
            risk_score = self.model.predict_proba(features)[0][1]
        
        # Determine intervention level and type
        intervention = self._get_intervention(risk_score, task_data)
        
        return {
            'abandonment_probability': round(risk_score, 2),
            'risk_level': 'HIGH' if risk_score > 0.7 else 'MEDIUM' if risk_score > 0.4 else 'LOW',
            'intervention_type': intervention['type'],
            'intervention_message': intervention['message'],
            'recommended_action': intervention['action'],
            'reasoning': intervention['reasoning']
        }
    
    def _heuristic_risk_score(self, task_data: dict) -> float:
        """Calculate risk score using domain knowledge when no model trained"""
        score = 0.3  # Base risk
        
        # Time-based factors
        hour = datetime.now().hour
        if 14 <= hour <= 16:  # Energy dip
            score += 0.15
        if hour >= 21:  # Late evening
            score += 0.1
            
        # Task factors
        complexity = task_data.get('task_complexity', 5)
        clarity = task_data.get('instruction_clarity', 5)
        score += (complexity - 5) * 0.03
        score -= (clarity - 5) * 0.02
        
        # Duration factor
        minutes_active = task_data.get('minutes_since_start', 0)
        if minutes_active > 30:
            score += 0.1
        if minutes_active > 60:
            score += 0.15
            
        # Pattern factors
        abandoned_today = task_data.get('tasks_abandoned_today', 0)
        score += abandoned_today * 0.1
        
        context_switches = task_data.get('context_switches_today', 0)
        score += context_switches * 0.05
        
        # Momentum factors
        completed_today = task_data.get('tasks_completed_today', 0)
        score -= completed_today * 0.05
        
        return min(max(score, 0), 1)  # Clamp 0-1
    
    def _get_intervention(self, risk_score: float, task_data: dict) -> dict:
        """Determine appropriate intervention based on risk and context"""
        minutes_active = task_data.get('minutes_since_start', 0)
        task_desc = task_data.get('description', 'current task')
        
        if risk_score < 0.4:
            return {
                'type': 'NONE',
                'message': None,
                'action': 'Continue monitoring',
                'reasoning': 'Low abandonment risk - task progressing normally'
            }
        
        if minutes_active < 30:
            # Level 1 - Light check-in
            return {
                'type': 'MICRO_COMMITMENT',
                'message': f"📌 Quick check: {task_desc} - still on it? Just the next small step.",
                'action': 'Request status update',
                'reasoning': f'Risk at {risk_score:.0%}, early intervention to maintain momentum'
            }
        
        if minutes_active < 60:
            # Level 2 - Pattern awareness
            switches = task_data.get('context_switches_today', 0)
            return {
                'type': 'BODY_DOUBLING',
                'message': f"🔄 I notice {task_desc} from {minutes_active} min ago. {switches} context switches today. Let's do this together - what's the ONE next action?",
                'action': 'Offer body doubling support',
                'reasoning': f'Risk at {risk_score:.0%}, mid-session - pattern intervention needed'
            }
        
        # Level 3 - Direct accountability
        return {
            'type': 'ACCOUNTABILITY',
            'message': f"⚠️ ACCOUNTABILITY: {task_desc} started {minutes_active} min ago. Status? Be honest - complete, continue, or consciously defer?",
            'action': 'Force decision point',
            'reasoning': f'Risk at {risk_score:.0%}, extended duration - requires explicit closure'
        }

    def analyze_today_session(self, activities: list) -> dict:
        """Analyze today's session for patterns"""
        if not activities:
            return {'status': 'No activities logged today'}
        
        completed = sum(1 for a in activities if a.get('status') == 'COMPLETED')
        abandoned = sum(1 for a in activities if a.get('status') == 'ABANDONED')
        in_progress = sum(1 for a in activities if a.get('status') in ['IN_PROGRESS', 'SOLUTION_PROVIDED'])
        
        total_focus_minutes = sum(a.get('duration_minutes', 0) for a in activities)
        domains = {}
        for a in activities:
            d = a.get('domain', 'UNKNOWN')
            domains[d] = domains.get(d, 0) + 1
        
        # Calculate patterns
        completion_rate = completed / max(completed + abandoned, 1)
        
        return {
            'completed': completed,
            'abandoned': abandoned,
            'in_progress': in_progress,
            'total_focus_minutes': total_focus_minutes,
            'completion_rate': round(completion_rate, 2),
            'domains_distribution': domains,
            'recommendation': self._session_recommendation(completion_rate, in_progress, abandoned)
        }
    
    def _session_recommendation(self, rate: float, in_progress: int, abandoned: int) -> str:
        if in_progress > 2:
            return "⚠️ Multiple tasks open - close or defer before starting new"
        if abandoned > 2:
            return "📊 Pattern: High abandonment today - consider shorter task chunks"
        if rate >= 0.8:
            return "✅ Strong completion momentum - maintain focus"
        if rate >= 0.5:
            return "📌 Mixed session - consider micro-commitments for remaining tasks"
        return "🔄 Low completion rate - reset with a quick win (small task)"


# Instantiate for use
model = ADHDInterventionModel()

def predict_for_task(task_data: dict) -> dict:
    """Main entry point for predictions"""
    return model.predict_abandonment_risk(task_data)

def analyze_session(activities: list) -> dict:
    """Analyze full session"""
    return model.analyze_today_session(activities)


if __name__ == "__main__":
    # Test with sample data
    test_task = {
        'description': 'Vercel deployment for Life OS dashboard',
        'task_complexity': 6,
        'instruction_clarity': 7,
        'estimated_minutes': 45,
        'minutes_since_start': 35,
        'tasks_completed_today': 8,
        'tasks_abandoned_today': 0,
        'context_switches_today': 3,
        'domain': 'BUSINESS',
        'consecutive_focus_minutes': 120
    }
    
    result = predict_for_task(test_task)
    print(json.dumps(result, indent=2))
