"""
Automation CLI Module

This module provides command-line interface for the URL Analyzer automation features,
including scripting, scheduled tasks, workflow automation, and batch processing.
"""

import os
import sys
import argparse
import json
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import AutomationError
from url_analyzer.automation.scripting import (
    list_available_scripts, run_script, create_script_template
)
from url_analyzer.automation.scheduler import (
    list_scheduled_tasks, schedule_task, remove_scheduled_task,
    run_scheduled_task, start_scheduler, stop_scheduler
)
from url_analyzer.automation.workflow import (
    list_workflows, create_workflow, add_workflow_step,
    run_workflow, delete_workflow, get_workflow
)
from url_analyzer.automation.batch import (
    list_batch_jobs, create_batch_job, process_batch_job,
    cancel_batch_job, delete_batch_job, get_batch_job
)

# Create logger
logger = get_logger(__name__)


def add_automation_commands(subparsers: argparse._SubParsersAction) -> None:
    """
    Add automation commands to the command-line interface.
    
    Args:
        subparsers: Subparsers object to add commands to
    """
    # Automation command
    automation_parser = subparsers.add_parser('automation', 
                                            help='Automation features for URL Analyzer',
                                            description="""
Automation features for URL Analyzer.

This command provides access to automation features like scripting, scheduled tasks,
workflow automation, and batch processing. These features allow you to automate
URL analysis tasks and integrate them into your workflows.

Examples:
  # List available scripts
  python -m url_analyzer automation scripts list
  
  # Run a script
  python -m url_analyzer automation scripts run my_script arg1 arg2
  
  # Create a new script from a template
  python -m url_analyzer automation scripts create my_script --template basic
  
  # List scheduled tasks
  python -m url_analyzer automation schedule list
  
  # Schedule a task
  python -m url_analyzer automation schedule add "Daily Analysis" --command "analyze --path data.csv" --type daily --hour 8 --minute 0
  
  # List workflows
  python -m url_analyzer automation workflow list
  
  # Create a workflow
  python -m url_analyzer automation workflow create "Data Processing Workflow" --description "Process and analyze data files"
  
  # List batch jobs
  python -m url_analyzer automation batch list
  
  # Create a batch job
  python -m url_analyzer automation batch create "Process CSV Files" --input-dir data --output-dir reports --pattern "*.csv"
""")
    
    # Create subparsers for automation commands
    automation_subparsers = automation_parser.add_subparsers(dest='automation_command', help='Automation command')
    
    # Scripts command
    scripts_parser = automation_subparsers.add_parser('scripts', 
                                                    help='Manage and run scripts',
                                                    description="Manage and run URL Analyzer scripts.")
    scripts_subparsers = scripts_parser.add_subparsers(dest='scripts_command', help='Scripts command')
    
    # Scripts list command
    scripts_list_parser = scripts_subparsers.add_parser('list', 
                                                      help='List available scripts',
                                                      description="List available URL Analyzer scripts.")
    scripts_list_parser.add_argument('--details', action='store_true',
                                   help="Show detailed information about scripts")
    scripts_list_parser.add_argument('--filter',
                                   help="Filter scripts by name or tag")
    
    # Scripts run command
    scripts_run_parser = scripts_subparsers.add_parser('run', 
                                                     help='Run a script',
                                                     description="Run a URL Analyzer script.")
    scripts_run_parser.add_argument('script_name',
                                  help="Name of the script to run")
    scripts_run_parser.add_argument('args', nargs='*',
                                  help="Arguments to pass to the script")
    
    # Scripts create command
    scripts_create_parser = scripts_subparsers.add_parser('create', 
                                                        help='Create a new script',
                                                        description="Create a new URL Analyzer script from a template.")
    scripts_create_parser.add_argument('script_name',
                                     help="Name of the script to create")
    scripts_create_parser.add_argument('--template', default='basic',
                                     choices=['basic', 'batch', 'report'],
                                     help="Template to use for the script")
    
    # Schedule command
    schedule_parser = automation_subparsers.add_parser('schedule', 
                                                     help='Manage scheduled tasks',
                                                     description="Manage scheduled URL Analyzer tasks.")
    schedule_subparsers = schedule_parser.add_subparsers(dest='schedule_command', help='Schedule command')
    
    # Schedule list command
    schedule_list_parser = schedule_subparsers.add_parser('list', 
                                                        help='List scheduled tasks',
                                                        description="List scheduled URL Analyzer tasks.")
    schedule_list_parser.add_argument('--details', action='store_true',
                                    help="Show detailed information about tasks")
    schedule_list_parser.add_argument('--filter',
                                    help="Filter tasks by name or tag")
    
    # Schedule add command
    schedule_add_parser = schedule_subparsers.add_parser('add', 
                                                       help='Add a scheduled task',
                                                       description="Add a scheduled URL Analyzer task.")
    schedule_add_parser.add_argument('name',
                                   help="Name of the task")
    schedule_add_parser.add_argument('--command', required=True,
                                   help="Command to execute (e.g., 'analyze --path data.csv')")
    schedule_add_parser.add_argument('--type', required=True,
                                   choices=['once', 'daily', 'weekly', 'monthly', 'interval'],
                                   help="Type of schedule")
    schedule_add_parser.add_argument('--description',
                                   help="Description of the task")
    schedule_add_parser.add_argument('--tags', nargs='+',
                                   help="Tags for the task")
    
    # Schedule type-specific arguments
    schedule_add_parser.add_argument('--timestamp',
                                   help="Timestamp for 'once' schedule (format: YYYY-MM-DD HH:MM)")
    schedule_add_parser.add_argument('--hour', type=int,
                                   help="Hour for 'daily', 'weekly', and 'monthly' schedules (0-23)")
    schedule_add_parser.add_argument('--minute', type=int,
                                   help="Minute for 'daily', 'weekly', and 'monthly' schedules (0-59)")
    schedule_add_parser.add_argument('--day-of-week', type=int,
                                   help="Day of week for 'weekly' schedule (0=Monday, 6=Sunday)")
    schedule_add_parser.add_argument('--day', type=int,
                                   help="Day of month for 'monthly' schedule (1-31)")
    schedule_add_parser.add_argument('--minutes', type=int,
                                   help="Interval in minutes for 'interval' schedule")
    
    # Schedule remove command
    schedule_remove_parser = schedule_subparsers.add_parser('remove', 
                                                          help='Remove a scheduled task',
                                                          description="Remove a scheduled URL Analyzer task.")
    schedule_remove_parser.add_argument('task_id',
                                      help="ID of the task to remove")
    
    # Schedule run command
    schedule_run_parser = schedule_subparsers.add_parser('run', 
                                                       help='Run a scheduled task',
                                                       description="Run a scheduled URL Analyzer task immediately.")
    schedule_run_parser.add_argument('task_id',
                                   help="ID of the task to run")
    
    # Schedule start command
    schedule_start_parser = schedule_subparsers.add_parser('start', 
                                                         help='Start the scheduler',
                                                         description="Start the URL Analyzer task scheduler.")
    
    # Schedule stop command
    schedule_stop_parser = schedule_subparsers.add_parser('stop', 
                                                        help='Stop the scheduler',
                                                        description="Stop the URL Analyzer task scheduler.")
    
    # Workflow command
    workflow_parser = automation_subparsers.add_parser('workflow', 
                                                     help='Manage workflows',
                                                     description="Manage URL Analyzer workflows.")
    workflow_subparsers = workflow_parser.add_subparsers(dest='workflow_command', help='Workflow command')
    
    # Workflow list command
    workflow_list_parser = workflow_subparsers.add_parser('list', 
                                                        help='List workflows',
                                                        description="List URL Analyzer workflows.")
    workflow_list_parser.add_argument('--details', action='store_true',
                                    help="Show detailed information about workflows")
    workflow_list_parser.add_argument('--filter',
                                    help="Filter workflows by name")
    
    # Workflow create command
    workflow_create_parser = workflow_subparsers.add_parser('create', 
                                                          help='Create a workflow',
                                                          description="Create a URL Analyzer workflow.")
    workflow_create_parser.add_argument('name',
                                      help="Name of the workflow")
    workflow_create_parser.add_argument('--description',
                                      help="Description of the workflow")
    
    # Workflow add-step command
    workflow_add_step_parser = workflow_subparsers.add_parser('add-step', 
                                                            help='Add a step to a workflow',
                                                            description="Add a step to a URL Analyzer workflow.")
    workflow_add_step_parser.add_argument('workflow_id',
                                        help="ID of the workflow")
    workflow_add_step_parser.add_argument('name',
                                        help="Name of the step")
    workflow_add_step_parser.add_argument('--command', required=True,
                                        help="Command to execute (e.g., 'analyze --path data.csv')")
    workflow_add_step_parser.add_argument('--depends-on', nargs='+',
                                        help="IDs of steps that this step depends on")
    workflow_add_step_parser.add_argument('--condition',
                                        help="Condition for executing the step")
    workflow_add_step_parser.add_argument('--timeout', type=int,
                                        help="Timeout in seconds")
    workflow_add_step_parser.add_argument('--retry', type=int, default=0,
                                        help="Number of retry attempts")
    
    # Workflow run command
    workflow_run_parser = workflow_subparsers.add_parser('run', 
                                                       help='Run a workflow',
                                                       description="Run a URL Analyzer workflow.")
    workflow_run_parser.add_argument('workflow_id',
                                   help="ID of the workflow to run")
    workflow_run_parser.add_argument('--variables', nargs='+',
                                   help="Variables for the workflow (format: key=value)")
    workflow_run_parser.add_argument('--async', action='store_true', dest='async_mode',
                                   help="Run the workflow asynchronously")
    
    # Workflow delete command
    workflow_delete_parser = workflow_subparsers.add_parser('delete', 
                                                          help='Delete a workflow',
                                                          description="Delete a URL Analyzer workflow.")
    workflow_delete_parser.add_argument('workflow_id',
                                      help="ID of the workflow to delete")
    
    # Batch command
    batch_parser = automation_subparsers.add_parser('batch', 
                                                  help='Manage batch jobs',
                                                  description="Manage URL Analyzer batch jobs.")
    batch_subparsers = batch_parser.add_subparsers(dest='batch_command', help='Batch command')
    
    # Batch list command
    batch_list_parser = batch_subparsers.add_parser('list', 
                                                  help='List batch jobs',
                                                  description="List URL Analyzer batch jobs.")
    batch_list_parser.add_argument('--details', action='store_true',
                                 help="Show detailed information about batch jobs")
    batch_list_parser.add_argument('--filter',
                                 help="Filter batch jobs by name or status")
    
    # Batch create command
    batch_create_parser = batch_subparsers.add_parser('create', 
                                                    help='Create a batch job',
                                                    description="Create a URL Analyzer batch job.")
    batch_create_parser.add_argument('name',
                                   help="Name of the batch job")
    batch_create_parser.add_argument('--input-dir', required=True,
                                   help="Input directory containing files to process")
    batch_create_parser.add_argument('--output-dir', required=True,
                                   help="Output directory for processed files")
    batch_create_parser.add_argument('--pattern', default="*.csv",
                                   help="File pattern to match (default: *.csv)")
    batch_create_parser.add_argument('--description',
                                   help="Description of the batch job")
    batch_create_parser.add_argument('--max-workers', type=int, default=4,
                                   help="Maximum number of worker threads (default: 4)")
    batch_create_parser.add_argument('--skip-errors', action='store_true',
                                   help="Continue processing even if some files have errors")
    batch_create_parser.add_argument('--checkpoint-interval', type=int, default=5,
                                   help="Interval for saving checkpoints in minutes (default: 5)")
    
    # Batch run command
    batch_run_parser = batch_subparsers.add_parser('run', 
                                                 help='Run a batch job',
                                                 description="Run a URL Analyzer batch job.")
    batch_run_parser.add_argument('job_id',
                                help="ID of the batch job to run")
    batch_run_parser.add_argument('--async', action='store_true', dest='async_mode',
                                help="Run the batch job asynchronously")
    
    # Batch cancel command
    batch_cancel_parser = batch_subparsers.add_parser('cancel', 
                                                    help='Cancel a batch job',
                                                    description="Cancel a running URL Analyzer batch job.")
    batch_cancel_parser.add_argument('job_id',
                                   help="ID of the batch job to cancel")
    
    # Batch delete command
    batch_delete_parser = batch_subparsers.add_parser('delete', 
                                                    help='Delete a batch job',
                                                    description="Delete a URL Analyzer batch job.")
    batch_delete_parser.add_argument('job_id',
                                   help="ID of the batch job to delete")


def handle_automation_command(args: argparse.Namespace) -> int:
    """
    Handle the 'automation' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    if args.automation_command == 'scripts':
        return handle_scripts_command(args)
    elif args.automation_command == 'schedule':
        return handle_schedule_command(args)
    elif args.automation_command == 'workflow':
        return handle_workflow_command(args)
    elif args.automation_command == 'batch':
        return handle_batch_command(args)
    else:
        print("Please specify an automation command. Use --help for more information.")
        return 1


def handle_scripts_command(args: argparse.Namespace) -> int:
    """
    Handle the 'scripts' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        if args.scripts_command == 'list':
            # List available scripts
            scripts = list_available_scripts()
            
            if not scripts:
                print("No scripts found.")
                return 0
            
            print(f"\nAvailable Scripts ({len(scripts)}):\n")
            
            for script in scripts:
                if args.details:
                    print(f"  {script['name']}")
                    print(f"  Path: {script['path']}")
                    if script['description']:
                        print(f"  Description: {script['description']}")
                    if script['author']:
                        print(f"  Author: {script['author']}")
                    print(f"  Version: {script['version']}")
                    if script['tags']:
                        print(f"  Tags: {', '.join(script['tags'])}")
                    if script['parameters']:
                        print("  Parameters:")
                        for param_name, param_info in script['parameters'].items():
                            required = "required" if param_info['required'] else "optional"
                            default = f", default={param_info['default']}" if not param_info['required'] else ""
                            print(f"    {param_name} ({param_info['type']}, {required}{default})")
                    print()
                else:
                    description = f" - {script['description']}" if script['description'] else ""
                    print(f"  {script['name']}{description}")
            
            return 0
        
        elif args.scripts_command == 'run':
            # Run a script
            script_name = args.script_name
            script_args = args.args
            
            print(f"Running script: {script_name}")
            result = run_script(script_name, script_args)
            
            return result if isinstance(result, int) else 0
        
        elif args.scripts_command == 'create':
            # Create a new script
            script_name = args.script_name
            template = args.template
            
            script_path = create_script_template(script_name, template)
            
            print(f"Created script: {script_path}")
            print(f"You can now edit the script and run it with: python -m url_analyzer automation scripts run {script_name}")
            
            return 0
        
        else:
            print("Please specify a scripts command. Use --help for more information.")
            return 1
    
    except AutomationError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        return 1


def handle_schedule_command(args: argparse.Namespace) -> int:
    """
    Handle the 'schedule' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        if args.schedule_command == 'list':
            # List scheduled tasks
            tasks = list_scheduled_tasks()
            
            if not tasks:
                print("No scheduled tasks found.")
                return 0
            
            print(f"\nScheduled Tasks ({len(tasks)}):\n")
            
            for task in tasks:
                if args.details:
                    print(f"  ID: {task['id']}")
                    print(f"  Name: {task['name']}")
                    if task['description']:
                        print(f"  Description: {task['description']}")
                    print(f"  Command: {' '.join(task['command'])}")
                    print(f"  Schedule: {task['schedule_type']}")
                    print(f"  Schedule Parameters: {task['schedule_params']}")
                    print(f"  Enabled: {task['enabled']}")
                    if task['last_run']:
                        last_run = datetime.datetime.fromtimestamp(task['last_run']).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  Last Run: {last_run}")
                    if task['next_run']:
                        next_run = datetime.datetime.fromtimestamp(task['next_run']).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  Next Run: {next_run}")
                    if task['tags']:
                        print(f"  Tags: {', '.join(task['tags'])}")
                    print()
                else:
                    next_run = ""
                    if task['next_run']:
                        next_run = f", Next Run: {datetime.datetime.fromtimestamp(task['next_run']).strftime('%Y-%m-%d %H:%M:%S')}"
                    print(f"  {task['name']} ({task['schedule_type']}){next_run}")
            
            return 0
        
        elif args.schedule_command == 'add':
            # Add a scheduled task
            name = args.name
            command = args.command.split()
            schedule_type = args.type
            description = args.description
            tags = args.tags
            
            # Build schedule parameters based on schedule type
            schedule_params = {}
            
            if schedule_type == 'once':
                if not args.timestamp:
                    print("Error: --timestamp is required for 'once' schedule")
                    return 1
                
                try:
                    timestamp = datetime.datetime.strptime(args.timestamp, '%Y-%m-%d %H:%M')
                    schedule_params['timestamp'] = timestamp.timestamp()
                except ValueError:
                    print("Error: Invalid timestamp format. Use YYYY-MM-DD HH:MM")
                    return 1
            
            elif schedule_type in ['daily', 'weekly', 'monthly']:
                if args.hour is None:
                    print(f"Error: --hour is required for '{schedule_type}' schedule")
                    return 1
                
                if args.minute is None:
                    print(f"Error: --minute is required for '{schedule_type}' schedule")
                    return 1
                
                schedule_params['hour'] = args.hour
                schedule_params['minute'] = args.minute
                
                if schedule_type == 'weekly':
                    if args.day_of_week is None:
                        print("Error: --day-of-week is required for 'weekly' schedule")
                        return 1
                    
                    schedule_params['day_of_week'] = args.day_of_week
                
                elif schedule_type == 'monthly':
                    if args.day is None:
                        print("Error: --day is required for 'monthly' schedule")
                        return 1
                    
                    schedule_params['day'] = args.day
            
            elif schedule_type == 'interval':
                if args.minutes is None:
                    print("Error: --minutes is required for 'interval' schedule")
                    return 1
                
                schedule_params['minutes'] = args.minutes
            
            # Schedule the task
            task_id = schedule_task(
                name=name,
                command=command,
                schedule_type=schedule_type,
                schedule_params=schedule_params,
                description=description,
                tags=tags
            )
            
            print(f"Scheduled task: {name} (ID: {task_id})")
            
            return 0
        
        elif args.schedule_command == 'remove':
            # Remove a scheduled task
            task_id = args.task_id
            
            remove_scheduled_task(task_id)
            
            print(f"Removed scheduled task with ID: {task_id}")
            
            return 0
        
        elif args.schedule_command == 'run':
            # Run a scheduled task
            task_id = args.task_id
            
            run_scheduled_task(task_id)
            
            print(f"Ran scheduled task with ID: {task_id}")
            
            return 0
        
        elif args.schedule_command == 'start':
            # Start the scheduler
            start_scheduler()
            
            print("Started the scheduler")
            
            return 0
        
        elif args.schedule_command == 'stop':
            # Stop the scheduler
            stop_scheduler()
            
            print("Stopped the scheduler")
            
            return 0
        
        else:
            print("Please specify a schedule command. Use --help for more information.")
            return 1
    
    except AutomationError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        return 1


def handle_workflow_command(args: argparse.Namespace) -> int:
    """
    Handle the 'workflow' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        if args.workflow_command == 'list':
            # List workflows
            workflows = list_workflows()
            
            if not workflows:
                print("No workflows found.")
                return 0
            
            print(f"\nWorkflows ({len(workflows)}):\n")
            
            for workflow in workflows:
                if args.details:
                    print(f"  ID: {workflow['id']}")
                    print(f"  Name: {workflow['name']}")
                    if workflow['description']:
                        print(f"  Description: {workflow['description']}")
                    print(f"  Status: {workflow['status']}")
                    print(f"  Steps: {workflow['step_count']}")
                    if workflow['created_at']:
                        created_at = datetime.datetime.fromtimestamp(workflow['created_at']).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  Created: {created_at}")
                    if workflow['updated_at']:
                        updated_at = datetime.datetime.fromtimestamp(workflow['updated_at']).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  Updated: {updated_at}")
                    print()
                else:
                    status = f" ({workflow['status']})" if workflow['status'] != 'pending' else ""
                    print(f"  {workflow['name']}{status} - {workflow['step_count']} steps")
            
            return 0
        
        elif args.workflow_command == 'create':
            # Create a workflow
            name = args.name
            description = args.description
            
            workflow_id = create_workflow(name, description)
            
            print(f"Created workflow: {name} (ID: {workflow_id})")
            print(f"You can now add steps to the workflow with: python -m url_analyzer automation workflow add-step {workflow_id} <step_name> --command <command>")
            
            return 0
        
        elif args.workflow_command == 'add-step':
            # Add a step to a workflow
            workflow_id = args.workflow_id
            name = args.name
            command = args.command.split()
            depends_on = args.depends_on
            condition = args.condition
            timeout = args.timeout
            retry = args.retry
            
            step_id = add_workflow_step(
                workflow_id=workflow_id,
                name=name,
                command=command,
                depends_on=depends_on,
                condition=condition,
                timeout=timeout,
                retry=retry
            )
            
            print(f"Added step: {name} (ID: {step_id}) to workflow {workflow_id}")
            
            return 0
        
        elif args.workflow_command == 'run':
            # Run a workflow
            workflow_id = args.workflow_id
            async_mode = args.async_mode
            
            # Parse variables
            variables = {}
            if args.variables:
                for var in args.variables:
                    if '=' in var:
                        key, value = var.split('=', 1)
                        variables[key] = value
                    else:
                        print(f"Warning: Ignoring invalid variable format: {var}")
            
            if async_mode:
                # Run asynchronously
                print(f"Running workflow {workflow_id} asynchronously")
                
                # Start the workflow in a separate thread
                import threading
                thread = threading.Thread(target=run_workflow, args=(workflow_id, variables))
                thread.daemon = True
                thread.start()
                
                print(f"Workflow {workflow_id} started. Use 'python -m url_analyzer automation workflow list --details' to check its status.")
            else:
                # Run synchronously
                print(f"Running workflow {workflow_id}")
                
                result = run_workflow(workflow_id, variables)
                
                print(f"Workflow completed with status: {result['status']}")
            
            return 0
        
        elif args.workflow_command == 'delete':
            # Delete a workflow
            workflow_id = args.workflow_id
            
            delete_workflow(workflow_id)
            
            print(f"Deleted workflow with ID: {workflow_id}")
            
            return 0
        
        else:
            print("Please specify a workflow command. Use --help for more information.")
            return 1
    
    except AutomationError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        return 1


def handle_batch_command(args: argparse.Namespace) -> int:
    """
    Handle the 'batch' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        if args.batch_command == 'list':
            # List batch jobs
            jobs = list_batch_jobs()
            
            if not jobs:
                print("No batch jobs found.")
                return 0
            
            print(f"\nBatch Jobs ({len(jobs)}):\n")
            
            for job in jobs:
                if args.details:
                    print(f"  ID: {job['id']}")
                    print(f"  Name: {job['name']}")
                    if job['description']:
                        print(f"  Description: {job['description']}")
                    print(f"  Status: {job['status']}")
                    if job['progress']:
                        print(f"  Progress: {job['progress']['processed']}/{job['progress']['total']} files processed, {job['progress']['failed']} failed")
                    if job['created_at']:
                        created_at = datetime.datetime.fromtimestamp(job['created_at']).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  Created: {created_at}")
                    if job['start_time']:
                        start_time = datetime.datetime.fromtimestamp(job['start_time']).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  Started: {start_time}")
                    if job['end_time']:
                        end_time = datetime.datetime.fromtimestamp(job['end_time']).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  Ended: {end_time}")
                    print()
                else:
                    status = f" ({job['status']})" if job['status'] != 'pending' else ""
                    progress = ""
                    if job['progress']:
                        progress = f" - {job['progress']['processed']}/{job['progress']['total']} files processed"
                    print(f"  {job['name']}{status}{progress}")
            
            return 0
        
        elif args.batch_command == 'create':
            # Create a batch job
            name = args.name
            input_dir = args.input_dir
            output_dir = args.output_dir
            pattern = args.pattern
            description = args.description
            
            # Find input files matching the pattern
            import glob
            input_files = glob.glob(os.path.join(input_dir, pattern))
            
            if not input_files:
                print(f"Warning: No files matching pattern '{pattern}' found in '{input_dir}'")
                return 1
            
            # Create options
            options = {
                'max_workers': args.max_workers,
                'skip_errors': args.skip_errors,
                'checkpoint_interval': args.checkpoint_interval
            }
            
            # Create the batch job
            job_id = create_batch_job(
                name=name,
                input_files=input_files,
                output_dir=output_dir,
                options=options,
                description=description
            )
            
            print(f"Created batch job: {name} (ID: {job_id})")
            print(f"Found {len(input_files)} files to process")
            print(f"You can run the job with: python -m url_analyzer automation batch run {job_id}")
            
            return 0
        
        elif args.batch_command == 'run':
            # Run a batch job
            job_id = args.job_id
            async_mode = args.async_mode
            
            if async_mode:
                # Run asynchronously
                print(f"Running batch job {job_id} asynchronously")
                
                process_batch_job(job_id, async_mode=True)
                
                print(f"Batch job {job_id} started. Use 'python -m url_analyzer automation batch list --details' to check its status.")
            else:
                # Run synchronously
                print(f"Running batch job {job_id}")
                
                result = process_batch_job(job_id, async_mode=False)
                
                print(f"Batch job completed with status: {result['status']}")
            
            return 0
        
        elif args.batch_command == 'cancel':
            # Cancel a batch job
            job_id = args.job_id
            
            cancel_batch_job(job_id)
            
            print(f"Cancelled batch job with ID: {job_id}")
            
            return 0
        
        elif args.batch_command == 'delete':
            # Delete a batch job
            job_id = args.job_id
            
            delete_batch_job(job_id)
            
            print(f"Deleted batch job with ID: {job_id}")
            
            return 0
        
        else:
            print("Please specify a batch command. Use --help for more information.")
            return 1
    
    except AutomationError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        return 1