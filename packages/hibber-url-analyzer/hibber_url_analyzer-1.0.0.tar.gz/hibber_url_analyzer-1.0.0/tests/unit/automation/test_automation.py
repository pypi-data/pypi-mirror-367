#!/usr/bin/env python
"""
Test script for URL Analyzer automation features.

This script tests the automation features of URL Analyzer, including
scripting interfaces, scheduled tasks, workflow automation, and batch processing.
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import time
from typing import Dict, List, Any, Optional

from url_analyzer.utils.errors import AutomationError
from url_analyzer.automation.scripting import (
    list_available_scripts, create_script_template, run_script
)
from url_analyzer.automation.scheduler import (
    list_scheduled_tasks, schedule_task, remove_scheduled_task,
    run_scheduled_task
)
from url_analyzer.automation.workflow import (
    list_workflows, create_workflow, add_workflow_step,
    run_workflow, delete_workflow, get_workflow
)
from url_analyzer.automation.batch import (
    list_batch_jobs, create_batch_job, process_batch_job,
    cancel_batch_job, delete_batch_job, get_batch_job
)


class TestAutomation(unittest.TestCase):
    """Test case for URL Analyzer automation features."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.temp_dir, "input")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create test files
        self.test_file = os.path.join(self.input_dir, "test_urls.csv")
        with open(self.test_file, "w") as f:
            f.write("Domain_name,URL\n")
            f.write("example.com,https://example.com\n")
            f.write("google.com,https://google.com\n")
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_scripting(self):
        """Test scripting interface."""
        print("\nTesting scripting interface...")
        
        # Create a test script
        script_name = "test_script"
        script_path = create_script_template(script_name, "basic")
        
        # Check that the script was created
        self.assertTrue(os.path.exists(script_path))
        print(f"Created script: {script_path}")
        
        # List available scripts
        scripts = list_available_scripts()
        
        # Check that the test script is in the list
        script_names = [script["name"] for script in scripts]
        self.assertIn(script_name, script_names)
        print(f"Available scripts: {script_names}")
        
        # Run the script
        try:
            result = run_script(script_name, ["https://example.com"])
            print(f"Script result: {result}")
        except Exception as e:
            print(f"Error running script: {e}")
    
    def test_scheduler(self):
        """Test scheduler interface."""
        print("\nTesting scheduler interface...")
        
        # Schedule a task
        task_id = schedule_task(
            name="Test Task",
            command=["analyze", "--path", self.test_file],
            schedule_type="once",
            schedule_params={"timestamp": time.time() + 3600},  # 1 hour from now
            description="Test task for automation testing",
            tags=["test", "automation"]
        )
        
        # Check that the task was scheduled
        self.assertIsNotNone(task_id)
        print(f"Scheduled task: {task_id}")
        
        # List scheduled tasks
        tasks = list_scheduled_tasks()
        
        # Check that the test task is in the list
        task_ids = [task["id"] for task in tasks]
        self.assertIn(task_id, task_ids)
        print(f"Scheduled tasks: {task_ids}")
        
        # Remove the task
        remove_scheduled_task(task_id)
        
        # Check that the task was removed
        tasks = list_scheduled_tasks()
        task_ids = [task["id"] for task in tasks]
        self.assertNotIn(task_id, task_ids)
        print("Task removed successfully")
    
    def test_workflow(self):
        """Test workflow interface."""
        print("\nTesting workflow interface...")
        
        # Create a workflow
        workflow_id = create_workflow(
            name="Test Workflow",
            description="Test workflow for automation testing"
        )
        
        # Check that the workflow was created
        self.assertIsNotNone(workflow_id)
        print(f"Created workflow: {workflow_id}")
        
        # Add a step to the workflow
        step_id = add_workflow_step(
            workflow_id=workflow_id,
            name="Test Step",
            command=["analyze", "--path", self.test_file],
            retry=1
        )
        
        # Check that the step was added
        self.assertIsNotNone(step_id)
        print(f"Added step: {step_id}")
        
        # Get the workflow
        workflow = get_workflow(workflow_id)
        
        # Check that the workflow has the step
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow["name"], "Test Workflow")
        self.assertEqual(len(workflow["steps"]), 1)
        print(f"Workflow steps: {len(workflow['steps'])}")
        
        # Delete the workflow
        delete_workflow(workflow_id)
        
        # Check that the workflow was deleted
        workflow = get_workflow(workflow_id)
        self.assertIsNone(workflow)
        print("Workflow deleted successfully")
    
    def test_batch(self):
        """Test batch processing interface."""
        print("\nTesting batch processing interface...")
        
        # Create a batch job
        job_id = create_batch_job(
            name="Test Batch Job",
            input_files=[self.test_file],
            output_dir=self.output_dir,
            options={
                "max_workers": 2,
                "skip_errors": True,
                "checkpoint_interval": 1
            },
            description="Test batch job for automation testing"
        )
        
        # Check that the job was created
        self.assertIsNotNone(job_id)
        print(f"Created batch job: {job_id}")
        
        # Get the job
        job = get_batch_job(job_id)
        
        # Check that the job has the correct properties
        self.assertIsNotNone(job)
        self.assertEqual(job["name"], "Test Batch Job")
        self.assertEqual(job["status"], "pending")
        print(f"Job status: {job['status']}")
        
        # Delete the job
        delete_batch_job(job_id)
        
        # Check that the job was deleted
        job = get_batch_job(job_id)
        self.assertIsNone(job)
        print("Batch job deleted successfully")


if __name__ == "__main__":
    unittest.main()