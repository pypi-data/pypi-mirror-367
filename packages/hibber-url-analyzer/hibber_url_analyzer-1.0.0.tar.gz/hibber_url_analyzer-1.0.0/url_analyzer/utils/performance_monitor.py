"""
Performance Monitoring Module

This module provides comprehensive performance monitoring capabilities to track
the effectiveness of optimizations including concurrent processing, caching,
memory usage, and overall system performance.
"""

import time
import threading
import psutil
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Concurrent processing metrics
    thread_pool_efficiency: float = 0.0
    active_threads: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_task_duration: float = 0.0
    thread_pool_utilization: float = 0.0
    
    # Cache performance metrics
    cache_hit_rate: float = 0.0
    cache_miss_rate: float = 0.0
    cache_size: int = 0
    cache_memory_usage: float = 0.0
    cache_evictions: int = 0
    average_cache_access_time: float = 0.0
    
    # Memory usage metrics
    memory_usage_mb: float = 0.0
    memory_peak_mb: float = 0.0
    memory_growth_rate: float = 0.0
    gc_collections: int = 0
    
    # System performance metrics
    cpu_usage_percent: float = 0.0
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    network_io_sent_mb: float = 0.0
    network_io_recv_mb: float = 0.0
    
    # Application-specific metrics
    urls_processed_per_second: float = 0.0
    classification_accuracy: float = 0.0
    analysis_throughput: float = 0.0
    error_rate: float = 0.0


@dataclass
class PerformanceAlert:
    """Performance alert for threshold violations."""
    metric_name: str
    current_value: float
    threshold: float
    severity: str  # 'warning', 'critical'
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    """
    
    def __init__(
        self,
        collection_interval: float = 5.0,
        history_size: int = 1000,
        enable_alerts: bool = True,
        enable_auto_export: bool = False,
        export_interval: float = 300.0
    ):
        """
        Initialize the performance monitor.
        
        Args:
            collection_interval: Interval between metric collections in seconds
            history_size: Maximum number of metric snapshots to keep
            enable_alerts: Whether to enable performance alerts
            enable_auto_export: Whether to automatically export metrics
            export_interval: Interval for automatic metric export in seconds
        """
        self.collection_interval = collection_interval
        self.history_size = history_size
        self.enable_alerts = enable_alerts
        self.enable_auto_export = enable_auto_export
        self.export_interval = export_interval
        
        # Metrics storage
        self.metrics_history: deque = deque(maxlen=history_size)
        self.current_metrics = PerformanceMetrics()
        self.alerts: List[PerformanceAlert] = []
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.export_thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()
        
        # Performance thresholds for alerts
        self.thresholds = {
            'memory_usage_mb': {'warning': 500, 'critical': 1000},
            'cpu_usage_percent': {'warning': 80, 'critical': 95},
            'cache_hit_rate': {'warning': 0.7, 'critical': 0.5},  # Lower is worse
            'error_rate': {'warning': 0.05, 'critical': 0.1},
            'thread_pool_efficiency': {'warning': 0.7, 'critical': 0.5}  # Lower is worse
        }
        
        # Metric collectors
        self.custom_collectors: Dict[str, Callable[[], Dict[str, Any]]] = {}
        
        # System monitoring
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = self.initial_memory
        
        logger.info("Performance monitor initialized")
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        if self.is_monitoring:
            logger.warning("Performance monitoring is already running")
            return
        
        self.is_monitoring = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="PerformanceMonitor"
        )
        self.monitor_thread.start()
        
        # Start export thread if enabled
        if self.enable_auto_export:
            self.export_thread = threading.Thread(
                target=self._export_loop,
                daemon=True,
                name="PerformanceExporter"
            )
            self.export_thread.start()
        
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        if self.export_thread:
            self.export_thread.join(timeout=5.0)
        
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Collect metrics
                metrics = self._collect_metrics()
                
                with self.lock:
                    self.current_metrics = metrics
                    self.metrics_history.append(metrics)
                
                # Check for alerts
                if self.enable_alerts:
                    self._check_alerts(metrics)
                
                # Sleep until next collection
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.collection_interval)
    
    def _export_loop(self) -> None:
        """Automatic export loop."""
        while self.is_monitoring:
            try:
                time.sleep(self.export_interval)
                if self.is_monitoring:
                    self.export_metrics()
            except Exception as e:
                logger.error(f"Error in export loop: {e}")
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        metrics = PerformanceMetrics()
        
        try:
            # System metrics
            metrics.cpu_usage_percent = psutil.cpu_percent()
            
            # Memory metrics
            memory_info = self.process.memory_info()
            metrics.memory_usage_mb = memory_info.rss / 1024 / 1024
            
            if metrics.memory_usage_mb > self.peak_memory:
                self.peak_memory = metrics.memory_usage_mb
            metrics.memory_peak_mb = self.peak_memory
            
            # Calculate memory growth rate
            if len(self.metrics_history) > 0:
                previous_memory = self.metrics_history[-1].memory_usage_mb
                time_diff = (metrics.timestamp - self.metrics_history[-1].timestamp).total_seconds()
                if time_diff > 0:
                    metrics.memory_growth_rate = (metrics.memory_usage_mb - previous_memory) / time_diff
            
            # I/O metrics
            io_counters = self.process.io_counters()
            metrics.disk_io_read_mb = io_counters.read_bytes / 1024 / 1024
            metrics.disk_io_write_mb = io_counters.write_bytes / 1024 / 1024
            
            # Network I/O (system-wide)
            net_io = psutil.net_io_counters()
            if net_io:
                metrics.network_io_sent_mb = net_io.bytes_sent / 1024 / 1024
                metrics.network_io_recv_mb = net_io.bytes_recv / 1024 / 1024
            
            # Thread metrics
            metrics.active_threads = threading.active_count()
            
            # Collect custom metrics
            for name, collector in self.custom_collectors.items():
                try:
                    custom_metrics = collector()
                    for key, value in custom_metrics.items():
                        if hasattr(metrics, key):
                            setattr(metrics, key, value)
                except Exception as e:
                    logger.error(f"Error collecting custom metrics from {name}: {e}")
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
        
        return metrics
    
    def _check_alerts(self, metrics: PerformanceMetrics) -> None:
        """Check for performance threshold violations."""
        for metric_name, thresholds in self.thresholds.items():
            if not hasattr(metrics, metric_name):
                continue
            
            current_value = getattr(metrics, metric_name)
            
            # Handle metrics where lower is worse (like cache hit rate)
            if metric_name in ['cache_hit_rate', 'thread_pool_efficiency']:
                if current_value < thresholds['critical']:
                    self._create_alert(metric_name, current_value, thresholds['critical'], 'critical')
                elif current_value < thresholds['warning']:
                    self._create_alert(metric_name, current_value, thresholds['warning'], 'warning')
            else:
                # Handle metrics where higher is worse
                if current_value > thresholds['critical']:
                    self._create_alert(metric_name, current_value, thresholds['critical'], 'critical')
                elif current_value > thresholds['warning']:
                    self._create_alert(metric_name, current_value, thresholds['warning'], 'warning')
    
    def _create_alert(self, metric_name: str, current_value: float, threshold: float, severity: str) -> None:
        """Create a performance alert."""
        # Avoid duplicate alerts for the same metric within a short time
        recent_alerts = [
            alert for alert in self.alerts[-10:]  # Check last 10 alerts
            if alert.metric_name == metric_name and 
            (datetime.now() - alert.timestamp).total_seconds() < 60  # Within last minute
        ]
        
        if recent_alerts:
            return
        
        message = f"{metric_name} is {current_value:.2f}, threshold: {threshold:.2f}"
        alert = PerformanceAlert(
            metric_name=metric_name,
            current_value=current_value,
            threshold=threshold,
            severity=severity,
            message=message
        )
        
        self.alerts.append(alert)
        
        # Log the alert
        if severity == 'critical':
            logger.critical(f"CRITICAL ALERT: {message}")
        else:
            logger.warning(f"WARNING ALERT: {message}")
    
    def register_custom_collector(self, name: str, collector: Callable[[], Dict[str, Any]]) -> None:
        """
        Register a custom metric collector.
        
        Args:
            name: Name of the collector
            collector: Function that returns a dictionary of metrics
        """
        self.custom_collectors[name] = collector
        logger.info(f"Registered custom metric collector: {name}")
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get the current performance metrics."""
        with self.lock:
            return self.current_metrics
    
    def get_metrics_history(self, minutes: Optional[int] = None) -> List[PerformanceMetrics]:
        """
        Get metrics history.
        
        Args:
            minutes: Number of minutes of history to return (None for all)
            
        Returns:
            List of performance metrics
        """
        with self.lock:
            if minutes is None:
                return list(self.metrics_history)
            
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            return [
                metrics for metrics in self.metrics_history
                if metrics.timestamp >= cutoff_time
            ]
    
    def get_alerts(self, severity: Optional[str] = None, minutes: Optional[int] = None) -> List[PerformanceAlert]:
        """
        Get performance alerts.
        
        Args:
            severity: Filter by severity ('warning', 'critical', None for all)
            minutes: Number of minutes of alerts to return (None for all)
            
        Returns:
            List of performance alerts
        """
        alerts = self.alerts
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        if minutes:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            alerts = [alert for alert in alerts if alert.timestamp >= cutoff_time]
        
        return alerts
    
    def export_metrics(self, filename: Optional[str] = None) -> str:
        """
        Export metrics to a JSON file.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"
        
        with self.lock:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'metrics_count': len(self.metrics_history),
                'current_metrics': self._metrics_to_dict(self.current_metrics),
                'metrics_history': [self._metrics_to_dict(m) for m in self.metrics_history],
                'alerts': [self._alert_to_dict(a) for a in self.alerts],
                'thresholds': self.thresholds
            }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Performance metrics exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            raise
    
    def _metrics_to_dict(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Convert PerformanceMetrics to dictionary."""
        return {
            'timestamp': metrics.timestamp.isoformat(),
            'thread_pool_efficiency': metrics.thread_pool_efficiency,
            'active_threads': metrics.active_threads,
            'completed_tasks': metrics.completed_tasks,
            'failed_tasks': metrics.failed_tasks,
            'average_task_duration': metrics.average_task_duration,
            'thread_pool_utilization': metrics.thread_pool_utilization,
            'cache_hit_rate': metrics.cache_hit_rate,
            'cache_miss_rate': metrics.cache_miss_rate,
            'cache_size': metrics.cache_size,
            'cache_memory_usage': metrics.cache_memory_usage,
            'cache_evictions': metrics.cache_evictions,
            'average_cache_access_time': metrics.average_cache_access_time,
            'memory_usage_mb': metrics.memory_usage_mb,
            'memory_peak_mb': metrics.memory_peak_mb,
            'memory_growth_rate': metrics.memory_growth_rate,
            'gc_collections': metrics.gc_collections,
            'cpu_usage_percent': metrics.cpu_usage_percent,
            'disk_io_read_mb': metrics.disk_io_read_mb,
            'disk_io_write_mb': metrics.disk_io_write_mb,
            'network_io_sent_mb': metrics.network_io_sent_mb,
            'network_io_recv_mb': metrics.network_io_recv_mb,
            'urls_processed_per_second': metrics.urls_processed_per_second,
            'classification_accuracy': metrics.classification_accuracy,
            'analysis_throughput': metrics.analysis_throughput,
            'error_rate': metrics.error_rate
        }
    
    def _alert_to_dict(self, alert: PerformanceAlert) -> Dict[str, Any]:
        """Convert PerformanceAlert to dictionary."""
        return {
            'metric_name': alert.metric_name,
            'current_value': alert.current_value,
            'threshold': alert.threshold,
            'severity': alert.severity,
            'timestamp': alert.timestamp.isoformat(),
            'message': alert.message
        }
    
    def get_summary_report(self) -> Dict[str, Any]:
        """Generate a summary performance report."""
        with self.lock:
            if not self.metrics_history:
                return {'error': 'No metrics available'}
            
            recent_metrics = self.get_metrics_history(minutes=30)  # Last 30 minutes
            
            if not recent_metrics:
                return {'error': 'No recent metrics available'}
            
            # Calculate averages and trends
            avg_memory = sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics)
            avg_cpu = sum(m.cpu_usage_percent for m in recent_metrics) / len(recent_metrics)
            avg_cache_hit_rate = sum(m.cache_hit_rate for m in recent_metrics) / len(recent_metrics)
            
            # Count alerts by severity
            recent_alerts = self.get_alerts(minutes=30)
            warning_count = len([a for a in recent_alerts if a.severity == 'warning'])
            critical_count = len([a for a in recent_alerts if a.severity == 'critical'])
            
            return {
                'summary_period': '30 minutes',
                'metrics_collected': len(recent_metrics),
                'averages': {
                    'memory_usage_mb': round(avg_memory, 2),
                    'cpu_usage_percent': round(avg_cpu, 2),
                    'cache_hit_rate': round(avg_cache_hit_rate, 3)
                },
                'current': self._metrics_to_dict(self.current_metrics),
                'alerts': {
                    'warning_count': warning_count,
                    'critical_count': critical_count,
                    'total_count': len(recent_alerts)
                },
                'peak_memory_mb': self.peak_memory,
                'monitoring_status': 'active' if self.is_monitoring else 'stopped'
            }


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def start_performance_monitoring() -> None:
    """Start global performance monitoring."""
    monitor = get_performance_monitor()
    monitor.start_monitoring()


def stop_performance_monitoring() -> None:
    """Stop global performance monitoring."""
    monitor = get_performance_monitor()
    monitor.stop_monitoring()