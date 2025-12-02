"""
Claude.ai Session Logger
Tracks chat sessions, tasks, tool calls, and decisions in Supabase
Alternative to Claude Trace for web chat monitoring

Usage by Claude:
- At session start: log_session_start()
- On each task: log_task(task_id, description, ...)
- On tool calls: log_tool_call(tool_name, success, ...)
- On decisions: log_decision(decision_type, decision, reasoning)
- On task completion: update_task_status(task_id, 'COMPLETED', verification)
- At session end: log_session_end()
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, List, Dict

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # Service role key required

class SessionLogger:
    def __init__(self, supabase_key: str = None):
        self.key = supabase_key or SUPABASE_KEY
        self.headers = {
            "Authorization": f"Bearer {self.key}",
            "apikey": self.key,
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.session_id = None
        self.message_count = 0
        self.tool_call_count = 0
        self.tasks_initiated = 0
        self.tasks_completed = 0
        self.tasks_abandoned = 0
        self.domains_touched = set()
        
    def _post(self, table: str, data: dict) -> dict:
        """POST to Supabase table"""
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers=self.headers,
            json=data
        )
        return resp.json() if resp.status_code in [200, 201] else {"error": resp.text}
    
    def _patch(self, table: str, match: dict, data: dict) -> dict:
        """PATCH Supabase record"""
        query = "&".join([f"{k}=eq.{v}" for k, v in match.items()])
        resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/{table}?{query}",
            headers=self.headers,
            json=data
        )
        return resp.json() if resp.status_code in [200, 204] else {"error": resp.text}
    
    def log_session_start(self, session_id: str = None) -> str:
        """Start a new chat session"""
        self.session_id = session_id or f"claude-ai-{datetime.now().strftime('%Y-%m-%d-%H%M')}"
        result = self._post("chat_sessions", {
            "session_id": self.session_id,
            "started_at": datetime.utcnow().isoformat()
        })
        return self.session_id
    
    def log_message(self, role: str, message_type: str, content_summary: str, 
                    domain: str = None, task_id: str = None, tool_calls: int = 0):
        """Log a chat message"""
        self.message_count += 1
        self.tool_call_count += tool_calls
        if domain:
            self.domains_touched.add(domain)
            
        return self._post("chat_messages", {
            "session_id": self.session_id,
            "message_number": self.message_count,
            "role": role,
            "message_type": message_type,
            "content_summary": content_summary[:500],  # Truncate
            "domain": domain,
            "task_id": task_id,
            "tool_calls_count": tool_calls
        })
    
    def log_task(self, task_id: str, description: str, domain: str = "BUSINESS",
                 complexity: int = 5, clarity: int = 5, estimated_minutes: int = 30):
        """Log a new task"""
        self.tasks_initiated += 1
        return self._post("task_states", {
            "session_id": self.session_id,
            "task_id": task_id,
            "description": description,
            "domain": domain,
            "complexity": complexity,
            "clarity": clarity,
            "estimated_minutes": estimated_minutes,
            "status": "INITIATED"
        })
    
    def update_task_status(self, task_id: str, status: str, 
                           verification_status: str = None,
                           verification_details: str = None,
                           artifacts: List[str] = None):
        """Update task status with verification"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if status == "COMPLETED":
            self.tasks_completed += 1
            update_data["completed_at"] = datetime.utcnow().isoformat()
        elif status == "ABANDONED":
            self.tasks_abandoned += 1
            update_data["abandoned_at"] = datetime.utcnow().isoformat()
        elif status == "SOLUTION_PROVIDED":
            update_data["solution_provided_at"] = datetime.utcnow().isoformat()
        elif status == "IN_PROGRESS":
            update_data["in_progress_at"] = datetime.utcnow().isoformat()
            
        if verification_status:
            update_data["verification_status"] = verification_status
        if verification_details:
            update_data["verification_details"] = verification_details
        if artifacts:
            update_data["artifacts_created"] = artifacts
            
        return self._patch("task_states", {"task_id": task_id}, update_data)
    
    def log_tool_call(self, tool_name: str, description: str = None,
                      success: bool = True, error: str = None,
                      execution_time_ms: int = None, result_summary: str = None):
        """Log a tool call"""
        return self._post("tool_calls", {
            "session_id": self.session_id,
            "tool_name": tool_name,
            "tool_description": description,
            "success": success,
            "error_message": error,
            "execution_time_ms": execution_time_ms,
            "result_summary": result_summary[:200] if result_summary else None
        })
    
    def log_decision(self, decision_type: str, decision: str, reasoning: str = None,
                     alternatives: List[str] = None, task_id: str = None):
        """Log a decision"""
        return self._post("decision_log", {
            "session_id": self.session_id,
            "task_id": task_id,
            "decision_type": decision_type,
            "decision": decision,
            "reasoning": reasoning,
            "alternatives_considered": alternatives
        })
    
    def log_adhd_intervention(self, task_description: str, risk_level: str,
                              probability: float, intervention_type: str,
                              message: str, reasoning: str):
        """Log an ADHD intervention trigger"""
        return self._post("task_interventions", {
            "user_id": 1,
            "task_description": task_description,
            "intervention_type": intervention_type,
            "risk_level": risk_level,
            "abandonment_probability": probability,
            "message": message,
            "reasoning": reasoning,
            "intervention_level": 3 if probability > 0.6 else 2 if probability > 0.4 else 1
        })
    
    def log_session_end(self, summary: str = None):
        """End the session with summary"""
        return self._patch("chat_sessions", {"session_id": self.session_id}, {
            "ended_at": datetime.utcnow().isoformat(),
            "total_messages": self.message_count,
            "total_tool_calls": self.tool_call_count,
            "tasks_initiated": self.tasks_initiated,
            "tasks_completed": self.tasks_completed,
            "tasks_abandoned": self.tasks_abandoned,
            "domains_touched": list(self.domains_touched),
            "primary_domain": list(self.domains_touched)[0] if self.domains_touched else None,
            "session_summary": summary
        })
    
    def get_open_tasks(self) -> List[dict]:
        """Get all open tasks"""
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/v_open_tasks",
            headers=self.headers
        )
        return resp.json() if resp.status_code == 200 else []
    
    def get_session_stats(self) -> dict:
        """Get current session statistics"""
        return {
            "session_id": self.session_id,
            "messages": self.message_count,
            "tool_calls": self.tool_call_count,
            "tasks_initiated": self.tasks_initiated,
            "tasks_completed": self.tasks_completed,
            "tasks_abandoned": self.tasks_abandoned,
            "completion_rate": round(self.tasks_completed / max(self.tasks_initiated, 1) * 100, 1),
            "domains": list(self.domains_touched)
        }


# Singleton instance for easy import
logger = SessionLogger()

# Convenience functions
def start_session(session_id: str = None) -> str:
    return logger.log_session_start(session_id)

def log_task(task_id: str, description: str, **kwargs):
    return logger.log_task(task_id, description, **kwargs)

def complete_task(task_id: str, verification_status: str, verification_details: str, artifacts: List[str] = None):
    return logger.update_task_status(task_id, "COMPLETED", verification_status, verification_details, artifacts)

def abandon_task(task_id: str, reason: str):
    return logger.update_task_status(task_id, "ABANDONED", "FAILED", reason)

def end_session(summary: str = None):
    return logger.log_session_end(summary)

def get_stats():
    return logger.get_session_stats()


if __name__ == "__main__":
    # Test the logger
    print("Testing Session Logger...")
    
    # Would need actual key to test
    # logger = SessionLogger("your-key-here")
    # session_id = logger.log_session_start()
    # print(f"Started session: {session_id}")
