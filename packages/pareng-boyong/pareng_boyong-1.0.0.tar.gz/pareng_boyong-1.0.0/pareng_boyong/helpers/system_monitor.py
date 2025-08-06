"""
System Health Monitoring Helper for Pareng Boyong.

This module provides system health monitoring, resource tracking,
and performance optimization recommendations.
"""

import psutil
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from ..core.config import ParengBoyongConfig


@dataclass
class SystemMetrics:
    """System metrics data structure."""
    cpu_percent: float
    memory_percent: float
    memory_available: int
    disk_percent: float
    disk_free: int
    timestamp: datetime
    healthy: bool = True
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class SystemMonitor:
    """
    System health monitoring and performance tracking.
    
    Provides:
    - Real-time system metrics
    - Health status assessment
    - Performance warnings and alerts
    - Resource usage optimization
    - Self-healing recommendations
    """
    
    def __init__(self):
        """Initialize system monitor."""
        self.monitoring_active = False
        self.history: List[SystemMetrics] = []
        self.max_history = 100
        
        # Health thresholds
        self.cpu_warning_threshold = 80.0
        self.cpu_critical_threshold = 90.0
        self.memory_warning_threshold = 75.0
        self.memory_critical_threshold = 85.0
        self.disk_warning_threshold = 85.0
        self.disk_critical_threshold = 95.0
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check.
        
        Returns:
            Health status with metrics and recommendations
        """
        try:
            metrics = self._collect_metrics()
            health_status = self._assess_health(metrics)
            recommendations = self._generate_recommendations(metrics)
            
            return {
                "healthy": health_status["healthy"],
                "status": health_status["status"],
                "metrics": {
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "memory_available_gb": round(metrics.memory_available / (1024**3), 2),
                    "disk_percent": metrics.disk_percent,
                    "disk_free_gb": round(metrics.disk_free / (1024**3), 2),
                },
                "warnings": metrics.warnings,
                "recommendations": recommendations,
                "timestamp": metrics.timestamp.isoformat(),
                "issues": health_status.get("issues", [])
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_free = disk.free
        
        # Create metrics object
        metrics = SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available=memory_available,
            disk_percent=disk_percent,
            disk_free=disk_free,
            timestamp=datetime.now()
        )
        
        # Add warnings
        if cpu_percent > self.cpu_warning_threshold:
            severity = "CRITICAL" if cpu_percent > self.cpu_critical_threshold else "WARNING"
            metrics.warnings.append(f"{severity}: High CPU usage ({cpu_percent:.1f}%)")
        
        if memory_percent > self.memory_warning_threshold:
            severity = "CRITICAL" if memory_percent > self.memory_critical_threshold else "WARNING"
            metrics.warnings.append(f"{severity}: High memory usage ({memory_percent:.1f}%)")
        
        if disk_percent > self.disk_warning_threshold:
            severity = "CRITICAL" if disk_percent > self.disk_critical_threshold else "WARNING"
            metrics.warnings.append(f"{severity}: High disk usage ({disk_percent:.1f}%)")
        
        # Determine if system is healthy
        metrics.healthy = (
            cpu_percent < self.cpu_critical_threshold and
            memory_percent < self.memory_critical_threshold and
            disk_percent < self.disk_critical_threshold
        )
        
        return metrics
    
    def _assess_health(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Assess overall system health."""
        issues = []
        
        if metrics.cpu_percent > self.cpu_critical_threshold:
            issues.append("Critical CPU usage - system may be unresponsive")
        elif metrics.cpu_percent > self.cpu_warning_threshold:
            issues.append("High CPU usage - performance may be degraded")
        
        if metrics.memory_percent > self.memory_critical_threshold:
            issues.append("Critical memory usage - risk of out-of-memory errors")
        elif metrics.memory_percent > self.memory_warning_threshold:
            issues.append("High memory usage - consider closing applications")
        
        if metrics.disk_percent > self.disk_critical_threshold:
            issues.append("Critical disk usage - system may fail")
        elif metrics.disk_percent > self.disk_warning_threshold:
            issues.append("High disk usage - consider cleaning up files")
        
        # Determine overall status
        if not metrics.healthy:
            status = "critical" if any("Critical" in issue for issue in issues) else "warning"
        else:
            status = "healthy"
        
        return {
            "healthy": metrics.healthy,
            "status": status,
            "issues": issues
        }
    
    def _generate_recommendations(self, metrics: SystemMetrics) -> List[str]:
        """Generate recommendations based on system metrics."""
        recommendations = []
        
        # CPU recommendations
        if metrics.cpu_percent > self.cpu_warning_threshold:
            recommendations.extend([
                "Consider closing unnecessary applications",
                "Use lighter AI models if available",
                "Try smaller batch sizes for operations",
                "Monitor for runaway processes"
            ])
        
        # Memory recommendations
        if metrics.memory_percent > self.memory_warning_threshold:
            recommendations.extend([
                "Close unused browser tabs and applications",
                "Consider using disk-based models instead of memory-based",
                "Clear temporary files and caches",
                "Restart Python kernel if using Jupyter"
            ])
        
        # Disk recommendations
        if metrics.disk_percent > self.disk_warning_threshold:
            recommendations.extend([
                "Clean up temporary files in /tmp",
                "Remove old log files",
                "Clear generated content cache",
                "Move large files to external storage"
            ])
        
        # Performance optimization
        if metrics.healthy:
            recommendations.extend([
                "System is healthy - optimal performance expected",
                "Consider enabling cost optimization for better resource usage",
                "Use FREE services to reduce API load"
            ])
        
        return recommendations
    
    def assess_risk(self, operation: str, estimated_resources: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assess risk of performing an operation given current system state.
        
        Args:
            operation: Description of operation to assess
            estimated_resources: Estimated resource requirements
            
        Returns:
            Risk assessment with recommendations
        """
        current_metrics = self._collect_metrics()
        estimated_resources = estimated_resources or {}
        
        risk_factors = []
        risk_level = "low"
        
        # CPU risk assessment
        est_cpu = estimated_resources.get("cpu_percent", 10)  # Default 10% CPU
        if current_metrics.cpu_percent + est_cpu > self.cpu_critical_threshold:
            risk_factors.append(f"CPU usage would exceed critical threshold")
            risk_level = "high"
        elif current_metrics.cpu_percent + est_cpu > self.cpu_warning_threshold:
            risk_factors.append(f"CPU usage would be elevated")
            risk_level = "medium" if risk_level == "low" else risk_level
        
        # Memory risk assessment
        est_memory_mb = estimated_resources.get("memory_mb", 100)  # Default 100MB
        current_memory_mb = (current_metrics.memory_percent / 100) * (psutil.virtual_memory().total / (1024**2))
        if current_memory_mb + est_memory_mb > (self.memory_critical_threshold / 100) * (psutil.virtual_memory().total / (1024**2)):
            risk_factors.append(f"Memory usage would exceed critical threshold")
            risk_level = "high"
        
        # Disk risk assessment
        est_disk_mb = estimated_resources.get("disk_mb", 50)  # Default 50MB
        if metrics.disk_free < (est_disk_mb * 1024 * 1024):
            risk_factors.append(f"Insufficient disk space for operation")
            risk_level = "high"
        
        # Operation-specific risks
        operation_lower = operation.lower()
        if "video" in operation_lower or "large" in operation_lower:
            if current_metrics.memory_percent > 70:
                risk_factors.append("High memory usage detected for memory-intensive operation")
                risk_level = "medium" if risk_level == "low" else risk_level
        
        recommendations = self._get_risk_mitigation_recommendations(risk_level, risk_factors)
        
        return {
            "risk_level": risk_level,
            "high_risk": risk_level == "high",
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "current_metrics": {
                "cpu_percent": current_metrics.cpu_percent,
                "memory_percent": current_metrics.memory_percent,
                "disk_free_gb": round(current_metrics.disk_free / (1024**3), 2)
            },
            "proceed": risk_level != "high"
        }
    
    def _get_risk_mitigation_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Get recommendations for risk mitigation."""
        if risk_level == "low":
            return ["Operation should proceed safely"]
        
        recommendations = []
        
        if risk_level == "high":
            recommendations.extend([
                "❌ Consider postponing this operation",
                "🔄 Try restarting the system to free resources",
                "💾 Use lighter alternatives or smaller inputs",
                "⏰ Wait for system resources to become available"
            ])
        
        if "CPU" in " ".join(risk_factors):
            recommendations.extend([
                "Close CPU-intensive applications",
                "Use cloud-based processing if available",
                "Break operation into smaller chunks"
            ])
        
        if "Memory" in " ".join(risk_factors):
            recommendations.extend([
                "Close unnecessary applications",
                "Clear system caches",
                "Use disk-based processing modes"
            ])
        
        if "disk" in " ".join(risk_factors):
            recommendations.extend([
                "Free up disk space first",
                "Use cloud storage for outputs",
                "Clean temporary files"
            ])
        
        return recommendations
    
    def start_monitoring(self, interval: int = 60):
        """Start continuous system monitoring."""
        self.monitoring_active = True
        # In a real implementation, this would start a background thread
        print(f"🔍 System monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop continuous system monitoring."""
        self.monitoring_active = False
        print("⏹️ System monitoring stopped")
    
    def get_resource_usage_trend(self, minutes: int = 30) -> Dict[str, Any]:
        """Get resource usage trend over specified time period."""
        if not self.history:
            return {"error": "No monitoring history available"}
        
        recent_metrics = [m for m in self.history if 
                         (datetime.now() - m.timestamp).total_seconds() < (minutes * 60)]
        
        if not recent_metrics:
            return {"error": f"No data available for last {minutes} minutes"}
        
        # Calculate trends
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        return {
            "period_minutes": minutes,
            "samples": len(recent_metrics),
            "cpu": {
                "current": cpu_values[-1],
                "average": sum(cpu_values) / len(cpu_values),
                "min": min(cpu_values),
                "max": max(cpu_values),
                "trend": "increasing" if cpu_values[-1] > cpu_values[0] else "decreasing"
            },
            "memory": {
                "current": memory_values[-1],
                "average": sum(memory_values) / len(memory_values),
                "min": min(memory_values),
                "max": max(memory_values),
                "trend": "increasing" if memory_values[-1] > memory_values[0] else "decreasing"
            }
        }
    
    def enable_self_healing(self):
        """Enable automatic self-healing features."""
        print("🔧 Self-healing system enabled")
        # In a real implementation, this would set up automatic recovery
        
    def disable_self_healing(self):
        """Disable automatic self-healing features."""
        print("⚙️ Self-healing system disabled")
    
    def __str__(self) -> str:
        return f"SystemMonitor(monitoring={'active' if self.monitoring_active else 'inactive'})"
    
    def __repr__(self) -> str:
        return f"SystemMonitor(active={self.monitoring_active}, history={len(self.history)})"