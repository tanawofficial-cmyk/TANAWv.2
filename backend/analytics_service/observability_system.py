"""
Observability & Alerting System for TANAW
Comprehensive monitoring, logging, and alerting for production deployment.

Features:
- Metrics collection and monitoring
- Structured logging with PII scrubbing
- Alert system for critical issues
- Dashboard generation
- Performance tracking
- Error monitoring
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import re
import hashlib

# Import existing configuration
from config_manager import get_config

@dataclass
class Metric:
    """Represents a metric measurement."""
    name: str
    value: float
    timestamp: str
    tags: Dict[str, str]
    unit: str = "count"

@dataclass
class LogEntry:
    """Represents a structured log entry."""
    ingest_id: str
    analysis_id: str
    user_id: str
    stage: str
    error_code: Optional[str]
    message: str
    sample_row: Optional[Dict[str, Any]]
    timestamp: str
    level: str

@dataclass
class Alert:
    """Represents an alert."""
    alert_id: str
    severity: str  # 'critical', 'warning', 'info'
    title: str
    message: str
    metric_name: str
    threshold: float
    current_value: float
    timestamp: str
    resolved: bool = False

class ObservabilitySystem:
    """
    Comprehensive observability system for TANAW.
    
    Features:
    - Metrics collection and monitoring
    - Structured logging with PII scrubbing
    - Alert system for critical issues
    - Dashboard generation
    - Performance tracking
    - Error monitoring
    """
    
    def __init__(self, config=None):
        """Initialize observability system."""
        self.config = config or get_config()
        self.observability_version = "1.0.0"
        
        # Metrics storage
        self.metrics = defaultdict(list)
        self.metric_thresholds = {
            'ingest.success_rate': 0.95,
            'parse.retries': 3,
            'mapping.auto_rate': 0.8,
            'gpt.error_rate': 0.05,
            'analytics.success': 0.9,
            'cache.hit_rate': 0.8,
            'kb.insert_rate': 0.95
        }
        
        # Logging setup
        self.logger = self._setup_logging()
        
        # Alert system
        self.alerts = []
        self.alert_rules = self._setup_alert_rules()
        
        # Performance tracking
        self.performance_data = defaultdict(list)
        
        # PII scrubbing patterns
        self.pii_patterns = [
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card numbers
            r'\b\d{3}-\d{2}-\d{4}\b',        # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{3}-\d{4}\b',       # Phone numbers
        ]
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logger = logging.getLogger('tanaw_observability')
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create handler
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _setup_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Setup alert rules for monitoring."""
        return {
            'gpt_parse_error_rate': {
                'metric': 'gpt.error_rate',
                'threshold': 0.05,
                'severity': 'critical',
                'title': 'GPT Parse Error Rate High',
                'message': 'GPT parse error rate exceeds 5%'
            },
            'kb_insert_failure': {
                'metric': 'kb.insert_rate',
                'threshold': 0.95,
                'severity': 'warning',
                'title': 'KB Insert Failure Rate High',
                'message': 'Knowledge base insert failure rate exceeds threshold'
            },
            'ingestion_parse_failures': {
                'metric': 'parse.retries',
                'threshold': 3,
                'severity': 'critical',
                'title': 'High Ingestion Parse Failures',
                'message': 'Parse retry count exceeds threshold'
            },
            'low_success_rate': {
                'metric': 'ingest.success_rate',
                'threshold': 0.95,
                'severity': 'warning',
                'title': 'Low Success Rate',
                'message': 'Overall success rate below threshold'
            }
        }
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None, unit: str = "count"):
        """Record a metric measurement."""
        try:
            metric = Metric(
                name=name,
                value=value,
                timestamp=datetime.now().isoformat(),
                tags=tags or {},
                unit=unit
            )
            
            self.metrics[name].append(metric)
            
            # Check for alerts
            self._check_alerts(name, value)
            
            # Keep only last 1000 metrics per name
            if len(self.metrics[name]) > 1000:
                self.metrics[name] = self.metrics[name][-1000:]
                
        except Exception as e:
            self.logger.error(f"Error recording metric {name}: {e}")
    
    def log_event(self, ingest_id: str, analysis_id: str, user_id: str, 
                  stage: str, message: str, error_code: str = None, 
                  sample_row: Dict[str, Any] = None, level: str = "INFO"):
        """Log a structured event."""
        try:
            # Scrub PII from sample row
            scrubbed_sample = self._scrub_pii(sample_row) if sample_row else None
            
            log_entry = LogEntry(
                ingest_id=ingest_id,
                analysis_id=analysis_id,
                user_id=user_id,
                stage=stage,
                error_code=error_code,
                message=message,
                sample_row=scrubbed_sample,
                timestamp=datetime.now().isoformat(),
                level=level
            )
            
            # Log to structured logger
            self.logger.info(json.dumps(asdict(log_entry)))
            
        except Exception as e:
            self.logger.error(f"Error logging event: {e}")
    
    def _scrub_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub PII from data."""
        if not data:
            return data
        
        scrubbed = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Apply PII scrubbing patterns
                scrubbed_value = value
                for pattern in self.pii_patterns:
                    scrubbed_value = re.sub(pattern, '[REDACTED]', scrubbed_value)
                scrubbed[key] = scrubbed_value
            else:
                scrubbed[key] = value
        
        return scrubbed
    
    def _check_alerts(self, metric_name: str, value: float):
        """Check if metric triggers any alerts."""
        try:
            for alert_name, rule in self.alert_rules.items():
                if rule['metric'] == metric_name:
                    threshold = rule['threshold']
                    severity = rule['severity']
                    
                    # Check if threshold is exceeded
                    if (severity == 'critical' and value > threshold) or \
                       (severity == 'warning' and value > threshold):
                        
                        alert = Alert(
                            alert_id=f"{alert_name}_{int(time.time())}",
                            severity=severity,
                            title=rule['title'],
                            message=rule['message'],
                            metric_name=metric_name,
                            threshold=threshold,
                            current_value=value,
                            timestamp=datetime.now().isoformat()
                        )
                        
                        self.alerts.append(alert)
                        self.logger.warning(f"ALERT: {alert.title} - {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for dashboard."""
        try:
            summary = {}
            
            for metric_name, measurements in self.metrics.items():
                if measurements:
                    values = [m.value for m in measurements]
                    summary[metric_name] = {
                        'current': values[-1] if values else 0,
                        'average': sum(values) / len(values) if values else 0,
                        'min': min(values) if values else 0,
                        'max': max(values) if values else 0,
                        'count': len(values),
                        'last_updated': measurements[-1].timestamp if measurements else None
                    }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting metrics summary: {e}")
            return {}
    
    def get_alerts_summary(self) -> Dict[str, Any]:
        """Get alerts summary."""
        try:
            active_alerts = [alert for alert in self.alerts if not alert.resolved]
            
            summary = {
                'total_alerts': len(self.alerts),
                'active_alerts': len(active_alerts),
                'critical_alerts': len([a for a in active_alerts if a.severity == 'critical']),
                'warning_alerts': len([a for a in active_alerts if a.severity == 'warning']),
                'recent_alerts': active_alerts[-10:] if active_alerts else []
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting alerts summary: {e}")
            return {}
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate dashboard data."""
        try:
            metrics_summary = self.get_metrics_summary()
            alerts_summary = self.get_alerts_summary()
            
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics_summary,
                'alerts': alerts_summary,
                'system_health': self._calculate_system_health(metrics_summary),
                'performance_trends': self._calculate_performance_trends()
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error generating dashboard data: {e}")
            return {}
    
    def _calculate_system_health(self, metrics_summary: Dict[str, Any]) -> str:
        """Calculate overall system health."""
        try:
            health_score = 100
            
            # Check critical metrics
            if 'ingest.success_rate' in metrics_summary:
                success_rate = metrics_summary['ingest.success_rate']['current']
                if success_rate < 0.95:
                    health_score -= 20
            
            if 'gpt.error_rate' in metrics_summary:
                error_rate = metrics_summary['gpt.error_rate']['current']
                if error_rate > 0.05:
                    health_score -= 30
            
            if 'cache.hit_rate' in metrics_summary:
                hit_rate = metrics_summary['cache.hit_rate']['current']
                if hit_rate < 0.8:
                    health_score -= 10
            
            # Determine health status
            if health_score >= 90:
                return "healthy"
            elif health_score >= 70:
                return "degraded"
            else:
                return "critical"
                
        except Exception as e:
            self.logger.error(f"Error calculating system health: {e}")
            return "unknown"
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends."""
        try:
            trends = {}
            
            for metric_name, measurements in self.metrics.items():
                if len(measurements) >= 2:
                    recent_values = [m.value for m in measurements[-10:]]
                    if len(recent_values) >= 2:
                        trend = "stable"
                        if recent_values[-1] > recent_values[0]:
                            trend = "increasing"
                        elif recent_values[-1] < recent_values[0]:
                            trend = "decreasing"
                        
                        trends[metric_name] = {
                            'trend': trend,
                            'change_percent': ((recent_values[-1] - recent_values[0]) / recent_values[0]) * 100 if recent_values[0] != 0 else 0
                        }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error calculating performance trends: {e}")
            return {}
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    self.logger.info(f"Alert {alert_id} resolved")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'metrics_summary': self.get_metrics_summary(),
                'alerts_summary': self.get_alerts_summary(),
                'system_health': self._calculate_system_health(self.get_metrics_summary()),
                'performance_trends': self._calculate_performance_trends(),
                'recommendations': self._generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate system recommendations based on metrics."""
        recommendations = []
        
        try:
            metrics_summary = self.get_metrics_summary()
            
            # Check success rate
            if 'ingest.success_rate' in metrics_summary:
                success_rate = metrics_summary['ingest.success_rate']['current']
                if success_rate < 0.95:
                    recommendations.append("Consider improving file parsing logic to increase success rate")
            
            # Check cache hit rate
            if 'cache.hit_rate' in metrics_summary:
                hit_rate = metrics_summary['cache.hit_rate']['current']
                if hit_rate < 0.8:
                    recommendations.append("Consider increasing cache TTL or improving cache key generation")
            
            # Check GPT error rate
            if 'gpt.error_rate' in metrics_summary:
                error_rate = metrics_summary['gpt.error_rate']['current']
                if error_rate > 0.05:
                    recommendations.append("Consider improving GPT prompt quality or adding more retry logic")
            
            # Check KB insert rate
            if 'kb.insert_rate' in metrics_summary:
                insert_rate = metrics_summary['kb.insert_rate']['current']
                if insert_rate < 0.95:
                    recommendations.append("Consider improving knowledge base error handling")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations

# Global observability instance
observability_system = ObservabilitySystem()

def record_metric(name: str, value: float, tags: Dict[str, str] = None, unit: str = "count"):
    """Convenience function to record a metric."""
    observability_system.record_metric(name, value, tags, unit)

def log_event(ingest_id: str, analysis_id: str, user_id: str, stage: str, 
              message: str, error_code: str = None, sample_row: Dict[str, Any] = None, level: str = "INFO"):
    """Convenience function to log an event."""
    observability_system.log_event(ingest_id, analysis_id, user_id, stage, message, error_code, sample_row, level)

def get_dashboard_data() -> Dict[str, Any]:
    """Convenience function to get dashboard data."""
    return observability_system.get_dashboard_data()

if __name__ == "__main__":
    # Test the observability system
    print("🧪 Testing Observability System")
    print("=" * 50)
    
    # Test metric recording
    record_metric('ingest.success_rate', 0.95, {'user_id': 'test_user'})
    record_metric('gpt.error_rate', 0.03, {'model': 'gpt-4o-mini'})
    record_metric('cache.hit_rate', 0.85, {'cache_type': 'analytics'})
    
    # Test event logging
    log_event('ingest_123', 'analysis_456', 'user_789', 'parsing', 'File parsed successfully')
    log_event('ingest_123', 'analysis_456', 'user_789', 'mapping', 'Mapping completed', 'MAPPING_SUCCESS')
    
    # Test dashboard data
    dashboard_data = get_dashboard_data()
    print(f"✅ Dashboard data generated: {len(dashboard_data)} sections")
    print(f"✅ System health: {dashboard_data.get('system_health', 'unknown')}")
    print(f"✅ Active alerts: {dashboard_data.get('alerts', {}).get('active_alerts', 0)}")
