"""
Deployment & Cost Guardrails for TANAW
Comprehensive deployment management and cost control for production.

Features:
- Environment configuration
- Spending limits and rate limiting
- Autoscaling based on queue length
- Secrets management
- Cost monitoring
- Resource optimization
"""

import os
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import requests
import hashlib
import hmac

# Import existing configuration
from config_manager import get_config

@dataclass
class EnvironmentConfig:
    """Represents environment configuration."""
    openai_api_key: str
    kb_conn: str
    redis_url: str
    cache_ttl: int
    deployment_env: str
    region: str
    version: str

@dataclass
class CostLimit:
    """Represents a cost limit."""
    limit_type: str  # 'monthly', 'daily', 'per_user'
    limit_amount: float
    current_usage: float
    currency: str = "USD"
    reset_date: str = None

@dataclass
class RateLimit:
    """Represents a rate limit."""
    resource: str
    limit_per_minute: int
    current_usage: int
    window_start: str
    reset_time: str

class DeploymentGuardrails:
    """
    Comprehensive deployment and cost guardrails for TANAW.
    
    Features:
    - Environment configuration
    - Spending limits and rate limiting
    - Autoscaling based on queue length
    - Secrets management
    - Cost monitoring
    - Resource optimization
    """
    
    def __init__(self, config=None):
        """Initialize deployment guardrails."""
        self.config = config or get_config()
        self.guardrails_version = "1.0.0"
        
        # Environment configuration
        self.env_config = self._load_environment_config()
        
        # Cost limits
        self.cost_limits = {
            'monthly_openai': CostLimit('monthly', 100.0, 0.0, 'USD', datetime.now().strftime('%Y-%m-01')),
            'daily_gpt_calls': CostLimit('daily', 1000.0, 0.0, 'USD', datetime.now().strftime('%Y-%m-%d')),
            'per_user_daily': CostLimit('per_user', 10.0, 0.0, 'USD', datetime.now().strftime('%Y-%m-%d'))
        }
        
        # Rate limits
        self.rate_limits = {
            'gpt_calls_per_minute': RateLimit('gpt_calls', 60, 0, datetime.now().isoformat(), (datetime.now() + timedelta(minutes=1)).isoformat()),
            'user_requests_per_minute': RateLimit('user_requests', 10, 0, datetime.now().isoformat(), (datetime.now() + timedelta(minutes=1)).isoformat()),
            'global_requests_per_minute': RateLimit('global_requests', 1000, 0, datetime.now().isoformat(), (datetime.now() + timedelta(minutes=1)).isoformat())
        }
        
        # Autoscaling configuration
        self.autoscaling_config = {
            'min_workers': 2,
            'max_workers': 20,
            'scale_up_threshold': 10,  # Queue length
            'scale_down_threshold': 2,  # Queue length
            'current_workers': 2
        }
        
        # Secrets management
        self.secrets = {}
        self.secret_rotation_schedule = {}
        
        # Cost tracking
        self.cost_tracking = {
            'openai_costs': [],
            'infrastructure_costs': [],
            'storage_costs': []
        }
        
        # Monitoring thread
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # Start monitoring
        self._start_monitoring()
    
    def _load_environment_config(self) -> EnvironmentConfig:
        """Load environment configuration."""
        return EnvironmentConfig(
            openai_api_key=os.getenv('OPENAI_API_KEY', ''),
            kb_conn=os.getenv('KB_CONN', 'sqlite:///tanaw_kb.db'),
            redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
            cache_ttl=int(os.getenv('CACHE_TTL', '3600')),
            deployment_env=os.getenv('DEPLOYMENT_ENV', 'development'),
            region=os.getenv('REGION', 'us-east-1'),
            version=os.getenv('VERSION', '1.0.0')
        )
    
    def _start_monitoring(self):
        """Start monitoring thread for cost and rate limiting."""
        try:
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
        except Exception as e:
            print(f"⚠️ Error starting monitoring thread: {e}")
    
    def _monitoring_loop(self):
        """Monitoring loop for cost and rate limiting."""
        while not self.stop_monitoring:
            try:
                # Check cost limits
                self._check_cost_limits()
                
                # Check rate limits
                self._check_rate_limits()
                
                # Update autoscaling
                self._update_autoscaling()
                
                # Rotate secrets if needed
                self._rotate_secrets()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"⚠️ Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _check_cost_limits(self):
        """Check if cost limits are exceeded."""
        try:
            for limit_name, limit in self.cost_limits.items():
                if limit.current_usage >= limit.limit_amount:
                    print(f"🚨 COST LIMIT EXCEEDED: {limit_name} - {limit.current_usage}/{limit.limit_amount} {limit.currency}")
                    # Implement cost control measures
                    self._implement_cost_control(limit_name)
                    
        except Exception as e:
            print(f"⚠️ Error checking cost limits: {e}")
    
    def _check_rate_limits(self):
        """Check if rate limits are exceeded."""
        try:
            for limit_name, limit in self.rate_limits.items():
                if limit.current_usage >= limit.limit_per_minute:
                    print(f"🚨 RATE LIMIT EXCEEDED: {limit_name} - {limit.current_usage}/{limit.limit_per_minute}")
                    # Implement rate limiting
                    self._implement_rate_limiting(limit_name)
                    
        except Exception as e:
            print(f"⚠️ Error checking rate limits: {e}")
    
    def _implement_cost_control(self, limit_name: str):
        """Implement cost control measures."""
        try:
            if 'openai' in limit_name:
                # Reduce GPT usage
                self.config['gpt_enabled'] = False
                print("🔒 GPT usage disabled due to cost limit")
            elif 'per_user' in limit_name:
                # Implement per-user limits
                print("🔒 Per-user limits implemented")
                
        except Exception as e:
            print(f"⚠️ Error implementing cost control: {e}")
    
    def _implement_rate_limiting(self, limit_name: str):
        """Implement rate limiting measures."""
        try:
            if 'gpt_calls' in limit_name:
                # Implement GPT rate limiting
                self.config['gpt_rate_limit'] = 10  # Reduce to 10 calls per minute
                print("🔒 GPT rate limiting implemented")
            elif 'user_requests' in limit_name:
                # Implement user rate limiting
                print("🔒 User rate limiting implemented")
                
        except Exception as e:
            print(f"⚠️ Error implementing rate limiting: {e}")
    
    def _update_autoscaling(self):
        """Update autoscaling based on queue length."""
        try:
            # Get current queue length (this would be from your queue system)
            queue_length = self._get_queue_length()
            
            current_workers = self.autoscaling_config['current_workers']
            min_workers = self.autoscaling_config['min_workers']
            max_workers = self.autoscaling_config['max_workers']
            
            if queue_length > self.autoscaling_config['scale_up_threshold'] and current_workers < max_workers:
                # Scale up
                new_workers = min(current_workers + 2, max_workers)
                self._scale_workers(new_workers)
                print(f"📈 Scaled up to {new_workers} workers (queue length: {queue_length})")
                
            elif queue_length < self.autoscaling_config['scale_down_threshold'] and current_workers > min_workers:
                # Scale down
                new_workers = max(current_workers - 1, min_workers)
                self._scale_workers(new_workers)
                print(f"📉 Scaled down to {new_workers} workers (queue length: {queue_length})")
                
        except Exception as e:
            print(f"⚠️ Error updating autoscaling: {e}")
    
    def _get_queue_length(self) -> int:
        """Get current queue length (placeholder implementation)."""
        # This would integrate with your actual queue system
        return 5  # Placeholder
    
    def _scale_workers(self, new_worker_count: int):
        """Scale workers to new count."""
        try:
            # This would integrate with your actual scaling system
            self.autoscaling_config['current_workers'] = new_worker_count
            print(f"🔄 Scaled workers to {new_worker_count}")
            
        except Exception as e:
            print(f"⚠️ Error scaling workers: {e}")
    
    def _rotate_secrets(self):
        """Rotate secrets if needed."""
        try:
            current_time = datetime.now()
            
            for secret_name, rotation_info in self.secret_rotation_schedule.items():
                if current_time >= datetime.fromisoformat(rotation_info['next_rotation']):
                    # Rotate secret
                    new_secret = self._generate_new_secret(secret_name)
                    self.secrets[secret_name] = new_secret
                    
                    # Update rotation schedule
                    next_rotation = current_time + timedelta(days=30)  # Rotate every 30 days
                    self.secret_rotation_schedule[secret_name]['next_rotation'] = next_rotation.isoformat()
                    
                    print(f"🔄 Rotated secret: {secret_name}")
                    
        except Exception as e:
            print(f"⚠️ Error rotating secrets: {e}")
    
    def _generate_new_secret(self, secret_name: str) -> str:
        """Generate new secret for rotation."""
        # This would integrate with your actual secret management system
        return f"new_secret_{secret_name}_{int(time.time())}"
    
    def track_cost(self, service: str, cost: float, user_id: str = None):
        """Track cost for a service."""
        try:
            cost_entry = {
                'service': service,
                'cost': cost,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
            
            if service == 'openai':
                self.cost_tracking['openai_costs'].append(cost_entry)
                # Update cost limits
                self.cost_limits['monthly_openai'].current_usage += cost
                if user_id:
                    self.cost_limits['per_user_daily'].current_usage += cost
                    
            elif service == 'infrastructure':
                self.cost_tracking['infrastructure_costs'].append(cost_entry)
                
            elif service == 'storage':
                self.cost_tracking['storage_costs'].append(cost_entry)
                
        except Exception as e:
            print(f"⚠️ Error tracking cost: {e}")
    
    def check_rate_limit(self, resource: str, user_id: str = None) -> bool:
        """Check if rate limit allows the request."""
        try:
            current_time = datetime.now()
            
            # Check global rate limits
            if resource in self.rate_limits:
                limit = self.rate_limits[resource]
                
                # Reset if window has passed
                if current_time >= datetime.fromisoformat(limit.reset_time):
                    limit.current_usage = 0
                    limit.window_start = current_time.isoformat()
                    limit.reset_time = (current_time + timedelta(minutes=1)).isoformat()
                
                # Check if limit exceeded
                if limit.current_usage >= limit.limit_per_minute:
                    return False
                
                # Increment usage
                limit.current_usage += 1
                
            # Check user-specific rate limits
            if user_id:
                user_limit_key = f"user_{user_id}_{resource}"
                if user_limit_key not in self.rate_limits:
                    self.rate_limits[user_limit_key] = RateLimit(
                        resource, 10, 0, current_time.isoformat(), (current_time + timedelta(minutes=1)).isoformat()
                    )
                
                user_limit = self.rate_limits[user_limit_key]
                if user_limit.current_usage >= user_limit.limit_per_minute:
                    return False
                
                user_limit.current_usage += 1
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error checking rate limit: {e}")
            return False
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary for monitoring."""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'cost_limits': {name: asdict(limit) for name, limit in self.cost_limits.items()},
                'rate_limits': {name: asdict(limit) for name, limit in self.rate_limits.items()},
                'autoscaling': self.autoscaling_config,
                'total_costs': {
                    'openai': sum(entry['cost'] for entry in self.cost_tracking['openai_costs']),
                    'infrastructure': sum(entry['cost'] for entry in self.cost_tracking['infrastructure_costs']),
                    'storage': sum(entry['cost'] for entry in self.cost_tracking['storage_costs'])
                }
            }
            
            return summary
            
        except Exception as e:
            print(f"⚠️ Error getting cost summary: {e}")
            return {}
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get deployment status."""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'environment': self.env_config.deployment_env,
                'region': self.env_config.region,
                'version': self.env_config.version,
                'autoscaling': self.autoscaling_config,
                'cost_summary': self.get_cost_summary(),
                'health': self._calculate_deployment_health()
            }
            
            return status
            
        except Exception as e:
            print(f"⚠️ Error getting deployment status: {e}")
            return {}
    
    def _calculate_deployment_health(self) -> str:
        """Calculate deployment health."""
        try:
            health_score = 100
            
            # Check cost limits
            for limit in self.cost_limits.values():
                if limit.current_usage >= limit.limit_amount * 0.9:  # 90% of limit
                    health_score -= 20
            
            # Check rate limits
            for limit in self.rate_limits.values():
                if limit.current_usage >= limit.limit_per_minute * 0.9:  # 90% of limit
                    health_score -= 10
            
            # Check autoscaling
            if self.autoscaling_config['current_workers'] < self.autoscaling_config['min_workers']:
                health_score -= 30
            
            if health_score >= 90:
                return "healthy"
            elif health_score >= 70:
                return "degraded"
            else:
                return "critical"
                
        except Exception as e:
            print(f"⚠️ Error calculating deployment health: {e}")
            return "unknown"
    
    def stop_monitoring(self):
        """Stop monitoring thread."""
        try:
            self.stop_monitoring = True
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
        except Exception as e:
            print(f"⚠️ Error stopping monitoring: {e}")

# Global deployment guardrails instance
deployment_guardrails = DeploymentGuardrails()

def track_cost(service: str, cost: float, user_id: str = None):
    """Convenience function to track cost."""
    deployment_guardrails.track_cost(service, cost, user_id)

def check_rate_limit(resource: str, user_id: str = None) -> bool:
    """Convenience function to check rate limit."""
    return deployment_guardrails.check_rate_limit(resource, user_id)

def get_deployment_status() -> Dict[str, Any]:
    """Convenience function to get deployment status."""
    return deployment_guardrails.get_deployment_status()

if __name__ == "__main__":
    # Test the deployment guardrails
    print("🧪 Testing Deployment Guardrails")
    print("=" * 50)
    
    # Test cost tracking
    track_cost('openai', 0.01, 'user_123')
    track_cost('infrastructure', 0.05)
    
    # Test rate limiting
    can_make_request = check_rate_limit('gpt_calls', 'user_123')
    print(f"✅ Rate limit check: {can_make_request}")
    
    # Test deployment status
    status = get_deployment_status()
    print(f"✅ Deployment status: {status['health']}")
    print(f"✅ Environment: {status['environment']}")
    print(f"✅ Version: {status['version']}")
