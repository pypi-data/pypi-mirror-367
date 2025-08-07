"""
Workflow Module

This module provides workflow automation capabilities for the URL Analyzer,
allowing users to define and execute sequences of operations as workflows.
It supports conditional execution, parallel processing, and error handling.
"""

import os
import json
import time
import uuid
import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import WorkflowError, AutomationError

# Create logger
logger = get_logger(__name__)

# Default path for storing workflows
DEFAULT_WORKFLOWS_DIR = os.path.join(os.path.expanduser("~"), ".url_analyzer", "workflows")


class StepStatus(Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """Status of a workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """
    Represents a step in a workflow.
    
    Attributes:
        id: Unique identifier for the step
        name: Human-readable name for the step
        command: Command to execute (as a list of arguments)
        depends_on: List of step IDs that this step depends on
        condition: Optional condition for executing the step
        timeout: Optional timeout in seconds
        retry: Optional number of retry attempts
        status: Current status of the step
        output: Output from the step execution
        error: Error message if the step failed
        start_time: Timestamp when the step started
        end_time: Timestamp when the step completed
    """
    id: str
    name: str
    command: List[str]
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    timeout: Optional[int] = None
    retry: int = 0
    status: StepStatus = field(default=StepStatus.PENDING)
    output: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the step to a dictionary for serialization."""
        data = asdict(self)
        # Convert enum to string
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        """Create a step from a dictionary."""
        # Convert string to enum
        if "status" in data:
            data["status"] = StepStatus(data["status"])
        return cls(**data)
    
    def can_run(self, completed_steps: List[str]) -> bool:
        """
        Check if the step can run based on its dependencies.
        
        Args:
            completed_steps: List of IDs of completed steps
            
        Returns:
            True if the step can run, False otherwise
        """
        # Check if all dependencies are completed
        for dep in self.depends_on:
            if dep not in completed_steps:
                return False
        return True
    
    def evaluate_condition(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate the condition for executing the step.
        
        Args:
            context: Workflow context with variables
            
        Returns:
            True if the condition is met or there is no condition, False otherwise
        """
        if not self.condition:
            return True
        
        try:
            # Simple condition evaluation using eval (with limited context)
            # For security, we only allow access to the context variables
            result = eval(self.condition, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            logger.error(f"Error evaluating condition '{self.condition}': {e}")
            return False


@dataclass
class Workflow:
    """
    Represents a workflow with multiple steps.
    
    Attributes:
        id: Unique identifier for the workflow
        name: Human-readable name for the workflow
        description: Optional description of the workflow
        steps: List of workflow steps
        variables: Variables for the workflow
        status: Current status of the workflow
        created_at: Timestamp when the workflow was created
        updated_at: Timestamp when the workflow was last updated
        start_time: Timestamp when the workflow started
        end_time: Timestamp when the workflow completed
    """
    id: str
    name: str
    steps: List[WorkflowStep]
    description: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = field(default=WorkflowStatus.PENDING)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow to a dictionary for serialization."""
        data = asdict(self)
        # Convert enum to string
        data["status"] = self.status.value
        # Convert steps to dictionaries
        data["steps"] = [step.to_dict() for step in self.steps]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """Create a workflow from a dictionary."""
        # Convert string to enum
        if "status" in data:
            data["status"] = WorkflowStatus(data["status"])
        # Convert dictionaries to steps
        if "steps" in data:
            data["steps"] = [WorkflowStep.from_dict(step) for step in data["steps"]]
        return cls(**data)
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """
        Get a step by ID.
        
        Args:
            step_id: ID of the step to get
            
        Returns:
            The step, or None if not found
        """
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def get_next_steps(self) -> List[WorkflowStep]:
        """
        Get the next steps that can be executed.
        
        Returns:
            List of steps that can be executed next
        """
        # Get IDs of completed steps
        completed_steps = [step.id for step in self.steps 
                          if step.status == StepStatus.COMPLETED]
        
        # Find steps that can run
        next_steps = []
        for step in self.steps:
            if step.status == StepStatus.PENDING and step.can_run(completed_steps):
                next_steps.append(step)
        
        return next_steps
    
    def is_complete(self) -> bool:
        """
        Check if the workflow is complete.
        
        Returns:
            True if all steps are completed, failed, or skipped, False otherwise
        """
        for step in self.steps:
            if step.status not in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED):
                return False
        return True
    
    def has_failed(self) -> bool:
        """
        Check if the workflow has failed.
        
        Returns:
            True if any step has failed, False otherwise
        """
        for step in self.steps:
            if step.status == StepStatus.FAILED:
                return True
        return False


class WorkflowEngine:
    """
    Executes workflows and manages workflow state.
    """
    
    def __init__(self, workflows_dir: str = DEFAULT_WORKFLOWS_DIR):
        """
        Initialize the workflow engine.
        
        Args:
            workflows_dir: Directory for storing workflows
        """
        self.workflows_dir = workflows_dir
        self._ensure_workflows_dir()
    
    def _ensure_workflows_dir(self) -> None:
        """Ensure the workflows directory exists."""
        os.makedirs(self.workflows_dir, exist_ok=True)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all available workflows.
        
        Returns:
            List of workflow metadata
        """
        workflows = []
        
        # Ensure the workflows directory exists
        self._ensure_workflows_dir()
        
        # Find all JSON files in the workflows directory
        for filename in os.listdir(self.workflows_dir):
            if filename.endswith(".json"):
                workflow_path = os.path.join(self.workflows_dir, filename)
                try:
                    with open(workflow_path, "r") as f:
                        workflow_data = json.load(f)
                    
                    # Extract metadata
                    metadata = {
                        "id": workflow_data.get("id"),
                        "name": workflow_data.get("name"),
                        "description": workflow_data.get("description"),
                        "status": workflow_data.get("status"),
                        "created_at": workflow_data.get("created_at"),
                        "updated_at": workflow_data.get("updated_at"),
                        "step_count": len(workflow_data.get("steps", []))
                    }
                    
                    workflows.append(metadata)
                except Exception as e:
                    logger.warning(f"Error loading workflow {workflow_path}: {e}")
        
        return workflows
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: ID of the workflow to get
            
        Returns:
            The workflow, or None if not found
        """
        workflow_path = os.path.join(self.workflows_dir, f"{workflow_id}.json")
        if not os.path.exists(workflow_path):
            return None
        
        try:
            with open(workflow_path, "r") as f:
                workflow_data = json.load(f)
            
            return Workflow.from_dict(workflow_data)
        except Exception as e:
            logger.warning(f"Error loading workflow {workflow_path}: {e}")
            return None
    
    def save_workflow(self, workflow: Workflow) -> None:
        """
        Save a workflow.
        
        Args:
            workflow: The workflow to save
        """
        # Ensure the workflows directory exists
        self._ensure_workflows_dir()
        
        # Update the updated_at timestamp
        workflow.updated_at = time.time()
        
        # Save the workflow
        workflow_path = os.path.join(self.workflows_dir, f"{workflow.id}.json")
        try:
            with open(workflow_path, "w") as f:
                json.dump(workflow.to_dict(), f, indent=2)
            
            logger.info(f"Saved workflow: {workflow.name} (ID: {workflow.id})")
        except Exception as e:
            logger.error(f"Error saving workflow {workflow.name} (ID: {workflow.id}): {e}")
            raise WorkflowError(f"Error saving workflow: {e}")
    
    def create_workflow(self, name: str, description: Optional[str] = None) -> Workflow:
        """
        Create a new workflow.
        
        Args:
            name: Name of the workflow
            description: Optional description of the workflow
            
        Returns:
            The created workflow
        """
        # Generate a unique ID
        workflow_id = str(uuid.uuid4())
        
        # Create the workflow
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            steps=[]
        )
        
        # Save the workflow
        self.save_workflow(workflow)
        
        return workflow
    
    def delete_workflow(self, workflow_id: str) -> None:
        """
        Delete a workflow.
        
        Args:
            workflow_id: ID of the workflow to delete
        """
        workflow_path = os.path.join(self.workflows_dir, f"{workflow_id}.json")
        if not os.path.exists(workflow_path):
            raise WorkflowError(f"Workflow with ID {workflow_id} does not exist")
        
        try:
            os.remove(workflow_path)
            logger.info(f"Deleted workflow with ID: {workflow_id}")
        except Exception as e:
            logger.error(f"Error deleting workflow with ID {workflow_id}: {e}")
            raise WorkflowError(f"Error deleting workflow: {e}")
    
    def add_step(self, workflow_id: str, name: str, command: List[str],
                depends_on: Optional[List[str]] = None,
                condition: Optional[str] = None,
                timeout: Optional[int] = None,
                retry: int = 0) -> str:
        """
        Add a step to a workflow.
        
        Args:
            workflow_id: ID of the workflow
            name: Name of the step
            command: Command to execute
            depends_on: Optional list of step IDs that this step depends on
            condition: Optional condition for executing the step
            timeout: Optional timeout in seconds
            retry: Optional number of retry attempts
            
        Returns:
            ID of the created step
        """
        # Get the workflow
        workflow = self.get_workflow(workflow_id)
        if workflow is None:
            raise WorkflowError(f"Workflow with ID {workflow_id} does not exist")
        
        # Generate a unique ID for the step
        step_id = str(uuid.uuid4())
        
        # Create the step
        step = WorkflowStep(
            id=step_id,
            name=name,
            command=command,
            depends_on=depends_on or [],
            condition=condition,
            timeout=timeout,
            retry=retry
        )
        
        # Add the step to the workflow
        workflow.steps.append(step)
        
        # Save the workflow
        self.save_workflow(workflow)
        
        return step_id
    
    def remove_step(self, workflow_id: str, step_id: str) -> None:
        """
        Remove a step from a workflow.
        
        Args:
            workflow_id: ID of the workflow
            step_id: ID of the step to remove
        """
        # Get the workflow
        workflow = self.get_workflow(workflow_id)
        if workflow is None:
            raise WorkflowError(f"Workflow with ID {workflow_id} does not exist")
        
        # Find the step
        step_index = None
        for i, step in enumerate(workflow.steps):
            if step.id == step_id:
                step_index = i
                break
        
        if step_index is None:
            raise WorkflowError(f"Step with ID {step_id} does not exist in workflow {workflow_id}")
        
        # Remove the step
        workflow.steps.pop(step_index)
        
        # Update dependencies
        for step in workflow.steps:
            if step_id in step.depends_on:
                step.depends_on.remove(step_id)
        
        # Save the workflow
        self.save_workflow(workflow)
    
    def run_workflow(self, workflow_id: str, variables: Optional[Dict[str, Any]] = None) -> Workflow:
        """
        Run a workflow.
        
        Args:
            workflow_id: ID of the workflow to run
            variables: Optional variables for the workflow
            
        Returns:
            The updated workflow
        """
        # Get the workflow
        workflow = self.get_workflow(workflow_id)
        if workflow is None:
            raise WorkflowError(f"Workflow with ID {workflow_id} does not exist")
        
        # Update workflow status and start time
        workflow.status = WorkflowStatus.RUNNING
        workflow.start_time = time.time()
        
        # Update variables
        if variables:
            workflow.variables.update(variables)
        
        # Save the workflow
        self.save_workflow(workflow)
        
        try:
            # Run the workflow
            logger.info(f"Running workflow: {workflow.name} (ID: {workflow.id})")
            
            # Process steps until the workflow is complete
            while not workflow.is_complete():
                # Get the next steps to run
                next_steps = workflow.get_next_steps()
                
                if not next_steps:
                    # No steps can run, but the workflow is not complete
                    # This could happen if there are circular dependencies
                    raise WorkflowError(f"Workflow {workflow.name} (ID: {workflow.id}) has no runnable steps but is not complete")
                
                # Run each step
                for step in next_steps:
                    self._run_step(workflow, step)
                    
                    # Save the workflow after each step
                    self.save_workflow(workflow)
            
            # Update workflow status and end time
            if workflow.has_failed():
                workflow.status = WorkflowStatus.FAILED
            else:
                workflow.status = WorkflowStatus.COMPLETED
            
            workflow.end_time = time.time()
            
            # Save the workflow
            self.save_workflow(workflow)
            
            logger.info(f"Workflow completed: {workflow.name} (ID: {workflow.id}), Status: {workflow.status.value}")
            
            return workflow
        except Exception as e:
            # Update workflow status and end time
            workflow.status = WorkflowStatus.FAILED
            workflow.end_time = time.time()
            
            # Save the workflow
            self.save_workflow(workflow)
            
            logger.error(f"Error running workflow {workflow.name} (ID: {workflow.id}): {e}")
            raise WorkflowError(f"Error running workflow: {e}")
    
    def _run_step(self, workflow: Workflow, step: WorkflowStep) -> None:
        """
        Run a workflow step.
        
        Args:
            workflow: The workflow
            step: The step to run
        """
        # Check if the step should be skipped based on its condition
        if not step.evaluate_condition(workflow.variables):
            logger.info(f"Skipping step {step.name} (ID: {step.id}) due to condition")
            step.status = StepStatus.SKIPPED
            return
        
        # Update step status and start time
        step.status = StepStatus.RUNNING
        step.start_time = time.time()
        
        logger.info(f"Running step: {step.name} (ID: {step.id})")
        
        # Run the step
        retry_count = 0
        max_retries = step.retry
        
        while retry_count <= max_retries:
            try:
                # Import here to avoid circular imports
                from url_analyzer.cli.commands import main as cli_main
                
                # Run the command
                import sys
                import io
                from contextlib import redirect_stdout, redirect_stderr
                
                # Capture stdout and stderr
                output = io.StringIO()
                error = io.StringIO()
                
                # Save original argv
                original_argv = sys.argv
                
                try:
                    # Set argv to the command
                    sys.argv = step.command
                    
                    # Run the command with captured output
                    with redirect_stdout(output), redirect_stderr(error):
                        exit_code = cli_main()
                    
                    # Check exit code
                    if exit_code != 0:
                        raise WorkflowError(f"Command exited with non-zero code: {exit_code}")
                    
                    # Update step status and output
                    step.status = StepStatus.COMPLETED
                    step.output = output.getvalue()
                    
                    # Update workflow variables with step output
                    workflow.variables[f"step_{step.id}_output"] = step.output
                    workflow.variables[f"step_{step.id}_exit_code"] = exit_code
                    
                    logger.info(f"Step completed: {step.name} (ID: {step.id})")
                    break  # Success, exit the retry loop
                finally:
                    # Restore original argv
                    sys.argv = original_argv
            except Exception as e:
                # Log the error
                logger.error(f"Error running step {step.name} (ID: {step.id}): {e}")
                
                # Update retry count
                retry_count += 1
                
                if retry_count <= max_retries:
                    # Retry the step
                    logger.info(f"Retrying step {step.name} (ID: {step.id}), attempt {retry_count} of {max_retries}")
                    time.sleep(1)  # Wait before retrying
                else:
                    # Max retries reached, mark as failed
                    step.status = StepStatus.FAILED
                    step.error = str(e)
                    
                    # Update workflow variables with step error
                    workflow.variables[f"step_{step.id}_error"] = step.error
                    
                    logger.error(f"Step failed after {max_retries} retries: {step.name} (ID: {step.id})")
        
        # Update step end time
        step.end_time = time.time()


# Global workflow engine instance
_workflow_engine = None


def get_workflow_engine() -> WorkflowEngine:
    """
    Get the global workflow engine instance.
    
    Returns:
        The global workflow engine instance
    """
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine


def create_workflow(name: str, description: Optional[str] = None) -> str:
    """
    Create a new workflow.
    
    Args:
        name: Name of the workflow
        description: Optional description of the workflow
        
    Returns:
        ID of the created workflow
    """
    engine = get_workflow_engine()
    workflow = engine.create_workflow(name, description)
    return workflow.id


def add_workflow_step(
    workflow_id: str,
    name: str,
    command: List[str],
    depends_on: Optional[List[str]] = None,
    condition: Optional[str] = None,
    timeout: Optional[int] = None,
    retry: int = 0
) -> str:
    """
    Add a step to a workflow.
    
    Args:
        workflow_id: ID of the workflow
        name: Name of the step
        command: Command to execute
        depends_on: Optional list of step IDs that this step depends on
        condition: Optional condition for executing the step
        timeout: Optional timeout in seconds
        retry: Optional number of retry attempts
        
    Returns:
        ID of the created step
    """
    engine = get_workflow_engine()
    return engine.add_step(
        workflow_id, name, command, depends_on, condition, timeout, retry
    )


def run_workflow(workflow_id: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run a workflow.
    
    Args:
        workflow_id: ID of the workflow to run
        variables: Optional variables for the workflow
        
    Returns:
        Dictionary with workflow execution results
    """
    engine = get_workflow_engine()
    workflow = engine.run_workflow(workflow_id, variables)
    return workflow.to_dict()


def list_workflows() -> List[Dict[str, Any]]:
    """
    List all available workflows.
    
    Returns:
        List of workflow metadata
    """
    engine = get_workflow_engine()
    return engine.list_workflows()


def get_workflow(workflow_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a workflow by ID.
    
    Args:
        workflow_id: ID of the workflow to get
        
    Returns:
        Dictionary with workflow data, or None if not found
    """
    engine = get_workflow_engine()
    workflow = engine.get_workflow(workflow_id)
    if workflow is None:
        return None
    return workflow.to_dict()


def delete_workflow(workflow_id: str) -> None:
    """
    Delete a workflow.
    
    Args:
        workflow_id: ID of the workflow to delete
    """
    engine = get_workflow_engine()
    engine.delete_workflow(workflow_id)


def save_workflow(workflow_data: Dict[str, Any]) -> None:
    """
    Save a workflow from a dictionary.
    
    Args:
        workflow_data: Dictionary with workflow data
    """
    engine = get_workflow_engine()
    workflow = Workflow.from_dict(workflow_data)
    engine.save_workflow(workflow)


def load_workflow(workflow_id: str) -> Dict[str, Any]:
    """
    Load a workflow by ID.
    
    Args:
        workflow_id: ID of the workflow to load
        
    Returns:
        Dictionary with workflow data
        
    Raises:
        WorkflowError: If the workflow does not exist
    """
    workflow_data = get_workflow(workflow_id)
    if workflow_data is None:
        raise WorkflowError(f"Workflow with ID {workflow_id} does not exist")
    return workflow_data