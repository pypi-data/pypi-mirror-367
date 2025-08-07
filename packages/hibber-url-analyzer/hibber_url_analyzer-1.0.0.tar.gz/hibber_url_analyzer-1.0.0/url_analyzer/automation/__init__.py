"""
Automation Module

This module provides automation capabilities for the URL Analyzer, including
scripting interfaces, scheduled task support, batch processing, headless operation,
and workflow automation.
"""

from url_analyzer.automation.scheduler import (
    ScheduledTask, TaskScheduler, schedule_task, list_scheduled_tasks,
    remove_scheduled_task, run_scheduled_task
)

from url_analyzer.automation.scripting import (
    ScriptRunner, run_script, list_available_scripts, create_script_template
)

from url_analyzer.automation.workflow import (
    Workflow, WorkflowStep, WorkflowEngine, load_workflow, save_workflow,
    run_workflow, list_workflows
)

from url_analyzer.automation.batch import (
    BatchProcessor, process_batch_job, create_batch_job, list_batch_jobs
)

__all__ = [
    'ScheduledTask', 'TaskScheduler', 'schedule_task', 'list_scheduled_tasks',
    'remove_scheduled_task', 'run_scheduled_task',
    'ScriptRunner', 'run_script', 'list_available_scripts', 'create_script_template',
    'Workflow', 'WorkflowStep', 'WorkflowEngine', 'load_workflow', 'save_workflow',
    'run_workflow', 'list_workflows',
    'BatchProcessor', 'process_batch_job', 'create_batch_job', 'list_batch_jobs'
]