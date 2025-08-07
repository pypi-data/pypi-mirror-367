"""
Report Scheduling Module

This module provides functionality for scheduling reports to be generated
at specified intervals or times.
"""

import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
import threading
import time
import uuid

from url_analyzer.reporting.domain import Report, ReportGenerationResult
from url_analyzer.reporting.interfaces import ReportingService

logger = logging.getLogger(__name__)


class ScheduledReport:
    """
    Represents a scheduled report configuration.
    
    This class encapsulates the information needed to schedule a report,
    including the report ID, schedule type, and schedule parameters.
    """
    
    def __init__(
        self,
        report_id: str,
        schedule_type: str,
        schedule_params: Dict[str, Any],
        enabled: bool = True,
        last_run: Optional[datetime] = None,
        next_run: Optional[datetime] = None,
        description: str = ""
    ):
        """
        Initialize a scheduled report.
        
        Args:
            report_id: ID of the report to schedule
            schedule_type: Type of schedule (daily, weekly, monthly, interval)
            schedule_params: Parameters for the schedule
            enabled: Whether the schedule is enabled
            last_run: When the report was last run
            next_run: When the report is next scheduled to run
            description: Description of the scheduled report
        """
        self.id = f"sched-{uuid.uuid4()}"
        self.report_id = report_id
        self.schedule_type = schedule_type
        self.schedule_params = schedule_params
        self.enabled = enabled
        self.last_run = last_run
        self.next_run = next_run
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the scheduled report to a dictionary.
        
        Returns:
            Dictionary representation of the scheduled report
        """
        return {
            "id": self.id,
            "report_id": self.report_id,
            "schedule_type": self.schedule_type,
            "schedule_params": self.schedule_params,
            "enabled": self.enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledReport':
        """
        Create a scheduled report from a dictionary.
        
        Args:
            data: Dictionary representation of the scheduled report
            
        Returns:
            ScheduledReport object
        """
        report = cls(
            report_id=data["report_id"],
            schedule_type=data["schedule_type"],
            schedule_params=data["schedule_params"],
            enabled=data.get("enabled", True),
            description=data.get("description", "")
        )
        
        report.id = data.get("id", report.id)
        
        if data.get("last_run"):
            report.last_run = datetime.fromisoformat(data["last_run"])
        
        if data.get("next_run"):
            report.next_run = datetime.fromisoformat(data["next_run"])
        
        if data.get("created_at"):
            report.created_at = datetime.fromisoformat(data["created_at"])
        
        if data.get("updated_at"):
            report.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return report
    
    def update_next_run(self) -> None:
        """
        Update the next run time based on the schedule.
        """
        now = datetime.now()
        
        if self.schedule_type == "daily":
            # Schedule for the next day at the specified time
            hour = self.schedule_params.get("hour", 0)
            minute = self.schedule_params.get("minute", 0)
            
            next_run = now.replace(hour=hour, minute=minute)
            if next_run <= now:
                next_run = next_run + timedelta(days=1)
            
            self.next_run = next_run
        
        elif self.schedule_type == "weekly":
            # Schedule for the next occurrence of the specified day of week
            day_of_week = self.schedule_params.get("day_of_week", 0)  # 0 = Monday
            hour = self.schedule_params.get("hour", 0)
            minute = self.schedule_params.get("minute", 0)
            
            days_ahead = day_of_week - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            
            next_run = now.replace(hour=hour, minute=minute) + timedelta(days=days_ahead)
            self.next_run = next_run
        
        elif self.schedule_type == "monthly":
            # Schedule for the specified day of the month
            day_of_month = self.schedule_params.get("day_of_month", 1)
            hour = self.schedule_params.get("hour", 0)
            minute = self.schedule_params.get("minute", 0)
            
            # Get the next month
            if now.month == 12:
                next_month = 1
                next_year = now.year + 1
            else:
                next_month = now.month + 1
                next_year = now.year
            
            # Handle cases where the day might not exist in the next month
            import calendar
            last_day = calendar.monthrange(next_year, next_month)[1]
            day = min(day_of_month, last_day)
            
            next_run = datetime(next_year, next_month, day, hour, minute)
            self.next_run = next_run
        
        elif self.schedule_type == "interval":
            # Schedule for the specified interval from now
            hours = self.schedule_params.get("hours", 0)
            minutes = self.schedule_params.get("minutes", 0)
            
            self.next_run = now + timedelta(hours=hours, minutes=minutes)
        
        else:
            logger.warning(f"Unknown schedule type: {self.schedule_type}")
            self.next_run = None
        
        self.updated_at = now


class ReportScheduler:
    """
    Manages scheduled reports.
    
    This class provides functionality for scheduling reports to be generated
    at specified intervals or times.
    """
    
    def __init__(
        self,
        reporting_service: ReportingService,
        schedule_file: Optional[str] = None,
        auto_start: bool = True
    ):
        """
        Initialize the report scheduler.
        
        Args:
            reporting_service: Service for generating reports
            schedule_file: Path to the file storing scheduled reports
            auto_start: Whether to automatically start the scheduler
        """
        self.reporting_service = reporting_service
        self.schedule_file = schedule_file
        self.scheduled_reports: Dict[str, ScheduledReport] = {}
        self.running = False
        self.scheduler_thread = None
        self.lock = threading.Lock()
        
        # Load scheduled reports if file exists
        if schedule_file and os.path.exists(schedule_file):
            self.load_schedules()
        
        # Start the scheduler if auto_start is True
        if auto_start:
            self.start()
    
    def start(self) -> None:
        """
        Start the scheduler.
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Report scheduler started")
    
    def stop(self) -> None:
        """
        Stop the scheduler.
        """
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Report scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """
        Main loop for the scheduler.
        """
        while self.running:
            now = datetime.now()
            
            # Check for reports that need to be run
            with self.lock:
                for report_id, scheduled_report in list(self.scheduled_reports.items()):
                    if not scheduled_report.enabled:
                        continue
                    
                    if scheduled_report.next_run and scheduled_report.next_run <= now:
                        # Run the report
                        try:
                            logger.info(f"Running scheduled report: {scheduled_report.id}")
                            result = self.reporting_service.generate_report(scheduled_report.report_id)
                            
                            # Update last run time
                            scheduled_report.last_run = now
                            
                            # Update next run time
                            scheduled_report.update_next_run()
                            
                            logger.info(f"Scheduled report {scheduled_report.id} completed. Next run: {scheduled_report.next_run}")
                        except Exception as e:
                            logger.error(f"Error running scheduled report {scheduled_report.id}: {str(e)}")
            
            # Save schedules
            self.save_schedules()
            
            # Sleep for a short time
            time.sleep(60)  # Check every minute
    
    def schedule_report(
        self,
        report_id: str,
        schedule_type: str,
        schedule_params: Dict[str, Any],
        description: str = ""
    ) -> ScheduledReport:
        """
        Schedule a report.
        
        Args:
            report_id: ID of the report to schedule
            schedule_type: Type of schedule (daily, weekly, monthly, interval)
            schedule_params: Parameters for the schedule
            description: Description of the scheduled report
            
        Returns:
            ScheduledReport object
        """
        # Verify that the report exists
        try:
            report = self.reporting_service.get_report(report_id)
        except Exception as e:
            raise ValueError(f"Report not found: {report_id}")
        
        # Create scheduled report
        scheduled_report = ScheduledReport(
            report_id=report_id,
            schedule_type=schedule_type,
            schedule_params=schedule_params,
            description=description
        )
        
        # Update next run time
        scheduled_report.update_next_run()
        
        # Add to scheduled reports
        with self.lock:
            self.scheduled_reports[scheduled_report.id] = scheduled_report
        
        # Save schedules
        self.save_schedules()
        
        return scheduled_report
    
    def get_scheduled_report(self, schedule_id: str) -> Optional[ScheduledReport]:
        """
        Get a scheduled report by ID.
        
        Args:
            schedule_id: ID of the scheduled report
            
        Returns:
            ScheduledReport object or None if not found
        """
        return self.scheduled_reports.get(schedule_id)
    
    def get_scheduled_reports(self) -> List[ScheduledReport]:
        """
        Get all scheduled reports.
        
        Returns:
            List of ScheduledReport objects
        """
        return list(self.scheduled_reports.values())
    
    def update_scheduled_report(
        self,
        schedule_id: str,
        enabled: Optional[bool] = None,
        schedule_type: Optional[str] = None,
        schedule_params: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> Optional[ScheduledReport]:
        """
        Update a scheduled report.
        
        Args:
            schedule_id: ID of the scheduled report
            enabled: Whether the schedule is enabled
            schedule_type: Type of schedule
            schedule_params: Parameters for the schedule
            description: Description of the scheduled report
            
        Returns:
            Updated ScheduledReport object or None if not found
        """
        with self.lock:
            scheduled_report = self.scheduled_reports.get(schedule_id)
            if not scheduled_report:
                return None
            
            if enabled is not None:
                scheduled_report.enabled = enabled
            
            if schedule_type is not None:
                scheduled_report.schedule_type = schedule_type
            
            if schedule_params is not None:
                scheduled_report.schedule_params = schedule_params
            
            if description is not None:
                scheduled_report.description = description
            
            scheduled_report.updated_at = datetime.now()
            
            # Update next run time
            scheduled_report.update_next_run()
        
        # Save schedules
        self.save_schedules()
        
        return scheduled_report
    
    def delete_scheduled_report(self, schedule_id: str) -> bool:
        """
        Delete a scheduled report.
        
        Args:
            schedule_id: ID of the scheduled report
            
        Returns:
            True if the report was deleted, False otherwise
        """
        with self.lock:
            if schedule_id not in self.scheduled_reports:
                return False
            
            del self.scheduled_reports[schedule_id]
        
        # Save schedules
        self.save_schedules()
        
        return True
    
    def load_schedules(self) -> None:
        """
        Load scheduled reports from the schedule file.
        """
        if not self.schedule_file:
            logger.warning("No schedule file specified")
            return
        
        try:
            with open(self.schedule_file, 'r') as f:
                data = json.load(f)
            
            with self.lock:
                self.scheduled_reports = {}
                for item in data:
                    scheduled_report = ScheduledReport.from_dict(item)
                    self.scheduled_reports[scheduled_report.id] = scheduled_report
            
            logger.info(f"Loaded {len(self.scheduled_reports)} scheduled reports from {self.schedule_file}")
        except Exception as e:
            logger.error(f"Error loading scheduled reports: {str(e)}")
    
    def save_schedules(self) -> None:
        """
        Save scheduled reports to the schedule file.
        """
        if not self.schedule_file:
            logger.warning("No schedule file specified")
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.schedule_file), exist_ok=True)
            
            with self.lock:
                data = [report.to_dict() for report in self.scheduled_reports.values()]
            
            with open(self.schedule_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved {len(self.scheduled_reports)} scheduled reports to {self.schedule_file}")
        except Exception as e:
            logger.error(f"Error saving scheduled reports: {str(e)}")
    
    def run_report_now(self, schedule_id: str) -> Optional[ReportGenerationResult]:
        """
        Run a scheduled report immediately.
        
        Args:
            schedule_id: ID of the scheduled report
            
        Returns:
            ReportGenerationResult or None if the report was not found
        """
        scheduled_report = self.get_scheduled_report(schedule_id)
        if not scheduled_report:
            return None
        
        try:
            # Run the report
            result = self.reporting_service.generate_report(scheduled_report.report_id)
            
            # Update last run time
            with self.lock:
                scheduled_report.last_run = datetime.now()
                scheduled_report.updated_at = datetime.now()
            
            # Save schedules
            self.save_schedules()
            
            return result
        except Exception as e:
            logger.error(f"Error running scheduled report {schedule_id}: {str(e)}")
            return None