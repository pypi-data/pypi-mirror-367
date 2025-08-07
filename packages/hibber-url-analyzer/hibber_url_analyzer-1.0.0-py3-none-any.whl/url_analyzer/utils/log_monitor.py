"""
Log Monitoring Module

This module provides tools for monitoring and analyzing log files in real-time,
generating alerts, and providing insights into application behavior.
"""

import os
import time
import threading
import re
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque

from url_analyzer.utils.logging import get_logger, LogAnalyzer

# Create logger
logger = get_logger(__name__)


class LogMonitor:
    """
    A real-time log monitoring system that can detect patterns, generate alerts,
    and provide insights into application behavior.
    
    Features:
    - Real-time log file monitoring
    - Pattern-based alert generation
    - Error rate monitoring
    - Performance anomaly detection
    - Periodic statistics reporting
    """
    
    def __init__(
        self, 
        log_file: str,
        alert_patterns: Optional[Dict[str, str]] = None,
        error_threshold: int = 5,
        performance_threshold: float = 2.0,
        check_interval: float = 1.0,
        stats_interval: int = 60,
        max_history: int = 1000
    ):
        """
        Initialize the log monitor.
        
        Args:
            log_file: Path to the log file to monitor
            alert_patterns: Dictionary of alert name to regex pattern
            error_threshold: Number of errors per minute to trigger an alert
            performance_threshold: Performance multiplier to trigger an alert
            check_interval: Interval in seconds between log checks
            stats_interval: Interval in seconds between stats reports
            max_history: Maximum number of events to keep in history
        """
        self.log_file = log_file
        self.alert_patterns = alert_patterns or {
            "error": r"ERROR|CRITICAL",
            "warning": r"WARNING",
            "performance": r"Performance: .* completed in (\d+\.\d+)s"
        }
        self.error_threshold = error_threshold
        self.performance_threshold = performance_threshold
        self.check_interval = check_interval
        self.stats_interval = stats_interval
        self.max_history = max_history
        
        # Compile regex patterns
        self.compiled_patterns = {
            name: re.compile(pattern) for name, pattern in self.alert_patterns.items()
        }
        
        # Initialize state
        self.running = False
        self.last_position = 0
        self.last_check_time = datetime.now()
        self.last_stats_time = datetime.now()
        
        # Initialize counters and history
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0
        self.performance_times = defaultdict(list)
        self.alerts = []
        self.history = deque(maxlen=max_history)
        
        # Initialize callbacks
        self.alert_callbacks = []
        self.stats_callbacks = []
        
        # Initialize analyzer
        self.analyzer = LogAnalyzer(log_file)
    
    def register_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Register a callback function to be called when an alert is generated.
        
        Args:
            callback: Function to call with alert name and details
        """
        self.alert_callbacks.append(callback)
    
    def register_stats_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a callback function to be called when stats are generated.
        
        Args:
            callback: Function to call with stats dictionary
        """
        self.stats_callbacks.append(callback)
    
    def _trigger_alert(self, alert_type: str, details: Dict[str, Any]) -> None:
        """
        Trigger an alert and call all registered callbacks.
        
        Args:
            alert_type: Type of alert
            details: Alert details
        """
        timestamp = datetime.now()
        alert = {
            "type": alert_type,
            "timestamp": timestamp,
            "details": details
        }
        
        # Add to alerts list
        self.alerts.append(alert)
        
        # Log the alert
        logger.warning(f"Alert: {alert_type} - {details}")
        
        # Call callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, details)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def _generate_stats(self) -> Dict[str, Any]:
        """
        Generate statistics about the monitored log.
        
        Returns:
            Dictionary of statistics
        """
        now = datetime.now()
        time_window = (now - self.last_stats_time).total_seconds()
        
        # Calculate rates
        error_rate = self.error_count / (time_window / 60) if time_window > 0 else 0
        warning_rate = self.warning_count / (time_window / 60) if time_window > 0 else 0
        info_rate = self.info_count / (time_window / 60) if time_window > 0 else 0
        
        # Calculate performance statistics
        performance_stats = {}
        for operation, times in self.performance_times.items():
            if times:
                performance_stats[operation] = {
                    "min": min(times),
                    "max": max(times),
                    "avg": sum(times) / len(times),
                    "count": len(times)
                }
        
        # Create stats dictionary
        stats = {
            "timestamp": now,
            "window_seconds": time_window,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "error_rate_per_minute": error_rate,
            "warning_rate_per_minute": warning_rate,
            "info_rate_per_minute": info_rate,
            "performance": performance_stats,
            "alerts_count": len(self.alerts),
            "history_count": len(self.history)
        }
        
        # Reset counters
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0
        self.performance_times = defaultdict(list)
        self.last_stats_time = now
        
        # Call callbacks
        for callback in self.stats_callbacks:
            try:
                callback(stats)
            except Exception as e:
                logger.error(f"Error in stats callback: {e}")
        
        return stats
    
    def _check_log(self) -> None:
        """Check the log file for new entries and process them."""
        try:
            # Check if file exists
            if not os.path.exists(self.log_file):
                logger.warning(f"Log file not found: {self.log_file}")
                return
            
            # Get file size
            file_size = os.path.getsize(self.log_file)
            
            # If file was truncated, reset position
            if file_size < self.last_position:
                self.last_position = 0
            
            # If no new data, return
            if file_size <= self.last_position:
                return
            
            # Read new data
            with open(self.log_file, 'r', encoding='utf-8') as f:
                f.seek(self.last_position)
                new_data = f.read()
                self.last_position = f.tell()
            
            # Process new data
            self._process_log_data(new_data)
            
            # Check if it's time to generate stats
            now = datetime.now()
            if (now - self.last_stats_time).total_seconds() >= self.stats_interval:
                self._generate_stats()
        
        except Exception as e:
            logger.error(f"Error checking log: {e}")
    
    def _process_log_data(self, data: str) -> None:
        """
        Process log data and update counters and history.
        
        Args:
            data: Log data to process
        """
        # Split data into lines
        lines = data.splitlines()
        
        # Process each line
        for line in lines:
            if not line.strip():
                continue
            
            # Add to history
            self.history.append({
                "timestamp": datetime.now(),
                "line": line
            })
            
            # Check for error/warning/info messages
            if "ERROR" in line or "CRITICAL" in line:
                self.error_count += 1
            elif "WARNING" in line:
                self.warning_count += 1
            elif "INFO" in line:
                self.info_count += 1
            
            # Check for performance information
            perf_match = re.search(r"Performance: (.*) completed in (\d+\.\d+)s", line)
            if perf_match:
                operation = perf_match.group(1)
                time_taken = float(perf_match.group(2))
                self.performance_times[operation].append(time_taken)
            
            # Check for alert patterns
            for alert_name, pattern in self.compiled_patterns.items():
                if pattern.search(line):
                    self._trigger_alert(alert_name, {
                        "line": line,
                        "pattern": self.alert_patterns[alert_name]
                    })
            
            # Check for error rate threshold
            if self.error_count >= self.error_threshold:
                self._trigger_alert("high_error_rate", {
                    "count": self.error_count,
                    "threshold": self.error_threshold,
                    "window_minutes": (datetime.now() - self.last_stats_time).total_seconds() / 60
                })
            
            # Check for performance anomalies
            for operation, times in self.performance_times.items():
                if len(times) >= 3:  # Need at least 3 samples to detect anomalies
                    avg = sum(times[:-1]) / len(times[:-1])  # Average of previous times
                    latest = times[-1]  # Latest time
                    
                    if latest > avg * self.performance_threshold:
                        self._trigger_alert("performance_anomaly", {
                            "operation": operation,
                            "average_time": avg,
                            "current_time": latest,
                            "threshold_multiplier": self.performance_threshold
                        })
    
    def start(self) -> None:
        """Start monitoring the log file."""
        if self.running:
            logger.warning("Log monitor is already running")
            return
        
        self.running = True
        self.last_position = os.path.getsize(self.log_file) if os.path.exists(self.log_file) else 0
        self.last_check_time = datetime.now()
        self.last_stats_time = datetime.now()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info(f"Started monitoring log file: {self.log_file}")
    
    def stop(self) -> None:
        """Stop monitoring the log file."""
        if not self.running:
            logger.warning("Log monitor is not running")
            return
        
        self.running = False
        self.monitor_thread.join(timeout=2.0)
        
        logger.info(f"Stopped monitoring log file: {self.log_file}")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            self._check_log()
            time.sleep(self.check_interval)
    
    def get_alerts(self, alert_type: Optional[str] = None, 
                  since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get alerts, optionally filtered by type and time.
        
        Args:
            alert_type: Type of alerts to get (if None, get all)
            since: Get alerts since this time (if None, get all)
            
        Returns:
            List of alerts
        """
        filtered_alerts = self.alerts
        
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a["type"] == alert_type]
        
        if since:
            filtered_alerts = [a for a in filtered_alerts if a["timestamp"] >= since]
        
        return filtered_alerts
    
    def get_history(self, pattern: Optional[str] = None, 
                   since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get history entries, optionally filtered by pattern and time.
        
        Args:
            pattern: Regex pattern to filter by (if None, get all)
            since: Get entries since this time (if None, get all)
            
        Returns:
            List of history entries
        """
        filtered_history = list(self.history)
        
        if pattern:
            regex = re.compile(pattern)
            filtered_history = [h for h in filtered_history if regex.search(h["line"])]
        
        if since:
            filtered_history = [h for h in filtered_history if h["timestamp"] >= since]
        
        return filtered_history
    
    def analyze_logs(self) -> Dict[str, Any]:
        """
        Analyze the entire log file and return statistics.
        
        Returns:
            Dictionary of statistics
        """
        # Parse the log file
        self.analyzer.parse_file()
        
        # Get statistics
        return self.analyzer.get_statistics()
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a report of the log analysis.
        
        Args:
            output_file: Path to the output file (if None, returns the report as a string)
            
        Returns:
            Report as a string if output_file is None, otherwise the path to the output file
        """
        return self.analyzer.generate_report(output_file)


class AlertNotifier:
    """
    A utility class for sending notifications when alerts are triggered.
    
    Supports multiple notification channels:
    - Console output
    - Email
    - Webhook
    - Custom callback functions
    """
    
    def __init__(self):
        """Initialize the alert notifier."""
        self.notification_channels = []
        self.logger = get_logger(__name__)
    
    def add_console_channel(self) -> None:
        """Add console output as a notification channel."""
        def console_notifier(alert_type, details):
            print(f"\n[ALERT] {alert_type.upper()} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Details: {details}")
            print("-" * 50)
        
        self.notification_channels.append(("console", console_notifier))
        self.logger.info("Added console notification channel")
    
    def add_email_channel(self, 
                         recipients: List[str], 
                         smtp_server: str, 
                         smtp_port: int = 587,
                         username: Optional[str] = None,
                         password: Optional[str] = None,
                         sender: Optional[str] = None,
                         use_tls: bool = True) -> None:
        """
        Add email as a notification channel.
        
        Args:
            recipients: List of email addresses to send notifications to
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            username: SMTP username (if authentication is required)
            password: SMTP password (if authentication is required)
            sender: Sender email address (if None, uses username)
            use_tls: Whether to use TLS for the connection
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
        except ImportError:
            self.logger.error("Email notifications require the 'email' package")
            return
        
        if sender is None:
            sender = username or "url-analyzer@localhost"
        
        def email_notifier(alert_type, details):
            try:
                # Create message
                msg = MIMEMultipart()
                msg['From'] = sender
                msg['To'] = ", ".join(recipients)
                msg['Subject'] = f"URL Analyzer Alert: {alert_type.upper()}"
                
                # Create message body
                body = f"""
                Alert Type: {alert_type.upper()}
                Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                Details:
                {details}
                
                This is an automated message from the URL Analyzer log monitoring system.
                """
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Connect to server and send
                server = smtplib.SMTP(smtp_server, smtp_port)
                if use_tls:
                    server.starttls()
                
                if username and password:
                    server.login(username, password)
                
                server.send_message(msg)
                server.quit()
                
                self.logger.info(f"Sent email alert for {alert_type} to {recipients}")
            except Exception as e:
                self.logger.error(f"Error sending email alert: {e}")
        
        self.notification_channels.append(("email", email_notifier))
        self.logger.info(f"Added email notification channel for {recipients}")
    
    def add_webhook_channel(self, webhook_url: str, 
                           headers: Optional[Dict[str, str]] = None) -> None:
        """
        Add webhook as a notification channel.
        
        Args:
            webhook_url: URL to send webhook notifications to
            headers: Additional headers to include in the request
        """
        try:
            import requests
            import json
        except ImportError:
            self.logger.error("Webhook notifications require the 'requests' package")
            return
        
        def webhook_notifier(alert_type, details):
            try:
                # Create payload
                payload = {
                    "alert_type": alert_type,
                    "timestamp": datetime.now().isoformat(),
                    "details": details
                }
                
                # Send webhook
                response = requests.post(
                    webhook_url,
                    headers=headers or {"Content-Type": "application/json"},
                    data=json.dumps(payload)
                )
                
                if response.status_code >= 400:
                    self.logger.error(f"Webhook error: {response.status_code} - {response.text}")
                else:
                    self.logger.info(f"Sent webhook alert for {alert_type}")
            except Exception as e:
                self.logger.error(f"Error sending webhook alert: {e}")
        
        self.notification_channels.append(("webhook", webhook_notifier))
        self.logger.info(f"Added webhook notification channel for {webhook_url}")
    
    def add_custom_channel(self, name: str, 
                          callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Add a custom notification channel.
        
        Args:
            name: Name of the channel
            callback: Function to call with alert type and details
        """
        self.notification_channels.append((name, callback))
        self.logger.info(f"Added custom notification channel: {name}")
    
    def notify(self, alert_type: str, details: Dict[str, Any]) -> None:
        """
        Send a notification to all channels.
        
        Args:
            alert_type: Type of alert
            details: Alert details
        """
        for name, channel in self.notification_channels:
            try:
                channel(alert_type, details)
            except Exception as e:
                self.logger.error(f"Error in notification channel {name}: {e}")


def create_default_monitor(log_file: str = "logs/url_analyzer.log") -> LogMonitor:
    """
    Create a default log monitor with standard alert patterns.
    
    Args:
        log_file: Path to the log file to monitor
        
    Returns:
        Configured LogMonitor instance
    """
    # Create standard alert patterns
    alert_patterns = {
        "error": r"ERROR|CRITICAL",
        "warning": r"WARNING",
        "performance": r"Performance: .* completed in (\d+\.\d+)s",
        "security": r"security|unauthorized|permission denied|access denied",
        "api_key": r"API key|authentication failed|invalid credentials",
        "database": r"database error|query failed|connection failed",
        "memory": r"memory|out of memory|MemoryError",
        "timeout": r"timeout|timed out|TimeoutError",
        "file_access": r"file not found|permission denied|IOError|OSError"
    }
    
    # Create monitor
    monitor = LogMonitor(
        log_file=log_file,
        alert_patterns=alert_patterns,
        error_threshold=5,
        performance_threshold=2.0,
        check_interval=1.0,
        stats_interval=60,
        max_history=1000
    )
    
    return monitor


def setup_console_monitoring(log_file: str = "logs/url_analyzer.log") -> Tuple[LogMonitor, AlertNotifier]:
    """
    Set up a log monitor with console notifications.
    
    Args:
        log_file: Path to the log file to monitor
        
    Returns:
        Tuple of (LogMonitor, AlertNotifier)
    """
    # Create monitor
    monitor = create_default_monitor(log_file)
    
    # Create notifier
    notifier = AlertNotifier()
    notifier.add_console_channel()
    
    # Register notifier with monitor
    monitor.register_alert_callback(notifier.notify)
    
    # Start monitoring
    monitor.start()
    
    return monitor, notifier


if __name__ == "__main__":
    # Example usage
    monitor, notifier = setup_console_monitoring()
    
    try:
        print(f"Monitoring log file: {monitor.log_file}")
        print("Press Ctrl+C to stop...")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        monitor.stop()
        print("Monitor stopped.")