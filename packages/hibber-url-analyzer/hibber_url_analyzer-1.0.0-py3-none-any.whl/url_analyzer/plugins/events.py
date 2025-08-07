"""
Events Module for URL Analyzer

This module provides an event system for URL Analyzer, allowing components
to publish events and subscribe to events from other components. This enables
loose coupling between components and extensibility through event-driven architecture.
"""

from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
from enum import Enum, auto
import logging
import inspect
import time
import uuid
from dataclasses import dataclass, field

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Event:
    """
    Base class for all events in the system.
    
    Events are immutable data objects that carry information about something
    that has happened in the system.
    """
    event_type: str
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the event after initialization."""
        if not self.event_type:
            raise ValueError("Event type cannot be empty")


class EventPriority(Enum):
    """Enum defining the priority levels for event handlers."""
    HIGHEST = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    LOWEST = 0


class EventBus:
    """
    Central event bus for publishing and subscribing to events.
    
    The event bus maintains a registry of subscribers and dispatches events
    to the appropriate handlers.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        # Map of event types to list of (handler, priority, subscriber_id)
        self._subscribers: Dict[str, List[Tuple[Callable, EventPriority, str]]] = {}
        # Map of wildcard patterns to list of (handler, priority, subscriber_id)
        self._wildcard_subscribers: Dict[str, List[Tuple[Callable, EventPriority, str]]] = {}
        # Map of subscriber_id to list of event types
        self._subscriber_registry: Dict[str, List[str]] = {}
        logger.debug("EventBus initialized")
    
    def subscribe(self, 
                 event_type: str, 
                 handler: Callable[[Event], None], 
                 priority: EventPriority = EventPriority.NORMAL,
                 subscriber_id: Optional[str] = None) -> str:
        """
        Subscribe to an event type.
        
        Args:
            event_type: The type of event to subscribe to (can include wildcards with *)
            handler: The function to call when the event occurs
            priority: Priority level for execution order
            subscriber_id: Optional ID for the subscriber (generated if not provided)
            
        Returns:
            Subscriber ID that can be used to unsubscribe
        """
        if subscriber_id is None:
            subscriber_id = str(uuid.uuid4())
        
        if '*' in event_type:
            # This is a wildcard subscription
            if event_type not in self._wildcard_subscribers:
                self._wildcard_subscribers[event_type] = []
            
            self._wildcard_subscribers[event_type].append((handler, priority, subscriber_id))
            self._wildcard_subscribers[event_type].sort(key=lambda x: x[1].value, reverse=True)
            logger.debug(f"Registered wildcard subscriber '{subscriber_id}' for '{event_type}' with priority {priority.name}")
        else:
            # This is a direct subscription
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            self._subscribers[event_type].append((handler, priority, subscriber_id))
            self._subscribers[event_type].sort(key=lambda x: x[1].value, reverse=True)
            logger.debug(f"Registered subscriber '{subscriber_id}' for '{event_type}' with priority {priority.name}")
        
        # Update the subscriber registry
        if subscriber_id not in self._subscriber_registry:
            self._subscriber_registry[subscriber_id] = []
        
        self._subscriber_registry[subscriber_id].append(event_type)
        
        return subscriber_id
    
    def unsubscribe(self, subscriber_id: str) -> bool:
        """
        Unsubscribe from all events.
        
        Args:
            subscriber_id: The ID of the subscriber to remove
            
        Returns:
            Boolean indicating whether unsubscription was successful
        """
        if subscriber_id not in self._subscriber_registry:
            logger.warning(f"Subscriber '{subscriber_id}' not found")
            return False
        
        # Get all event types this subscriber is subscribed to
        event_types = self._subscriber_registry[subscriber_id]
        
        # Remove the subscriber from all event types
        for event_type in event_types:
            if '*' in event_type:
                # This is a wildcard subscription
                if event_type in self._wildcard_subscribers:
                    self._wildcard_subscribers[event_type] = [
                        (h, p, s) for h, p, s in self._wildcard_subscribers[event_type]
                        if s != subscriber_id
                    ]
                    
                    if not self._wildcard_subscribers[event_type]:
                        del self._wildcard_subscribers[event_type]
            else:
                # This is a direct subscription
                if event_type in self._subscribers:
                    self._subscribers[event_type] = [
                        (h, p, s) for h, p, s in self._subscribers[event_type]
                        if s != subscriber_id
                    ]
                    
                    if not self._subscribers[event_type]:
                        del self._subscribers[event_type]
        
        # Remove the subscriber from the registry
        del self._subscriber_registry[subscriber_id]
        
        logger.debug(f"Unsubscribed '{subscriber_id}' from all events")
        return True
    
    def unsubscribe_from_event(self, subscriber_id: str, event_type: str) -> bool:
        """
        Unsubscribe from a specific event type.
        
        Args:
            subscriber_id: The ID of the subscriber to remove
            event_type: The type of event to unsubscribe from
            
        Returns:
            Boolean indicating whether unsubscription was successful
        """
        if subscriber_id not in self._subscriber_registry:
            logger.warning(f"Subscriber '{subscriber_id}' not found")
            return False
        
        # Check if the subscriber is subscribed to this event type
        if event_type not in self._subscriber_registry[subscriber_id]:
            logger.warning(f"Subscriber '{subscriber_id}' not subscribed to '{event_type}'")
            return False
        
        # Remove the subscriber from the event type
        if '*' in event_type:
            # This is a wildcard subscription
            if event_type in self._wildcard_subscribers:
                self._wildcard_subscribers[event_type] = [
                    (h, p, s) for h, p, s in self._wildcard_subscribers[event_type]
                    if s != subscriber_id
                ]
                
                if not self._wildcard_subscribers[event_type]:
                    del self._wildcard_subscribers[event_type]
        else:
            # This is a direct subscription
            if event_type in self._subscribers:
                self._subscribers[event_type] = [
                    (h, p, s) for h, p, s in self._subscribers[event_type]
                    if s != subscriber_id
                ]
                
                if not self._subscribers[event_type]:
                    del self._subscribers[event_type]
        
        # Remove the event type from the subscriber's registry
        self._subscriber_registry[subscriber_id].remove(event_type)
        
        # If the subscriber has no more subscriptions, remove it from the registry
        if not self._subscriber_registry[subscriber_id]:
            del self._subscriber_registry[subscriber_id]
        
        logger.debug(f"Unsubscribed '{subscriber_id}' from '{event_type}'")
        return True
    
    def publish(self, event: Event) -> bool:
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event to publish
            
        Returns:
            Boolean indicating whether publication was successful
        """
        event_type = event.event_type
        logger.debug(f"Publishing event '{event_type}' with ID '{event.event_id}'")
        
        # Collect all handlers that should receive this event
        handlers_to_call = []
        
        # Add direct subscribers
        if event_type in self._subscribers:
            handlers_to_call.extend(self._subscribers[event_type])
        
        # Add wildcard subscribers
        for pattern, subscribers in self._wildcard_subscribers.items():
            if self._matches_wildcard(event_type, pattern):
                handlers_to_call.extend(subscribers)
        
        # Sort by priority
        handlers_to_call.sort(key=lambda x: x[1].value, reverse=True)
        
        # Call all handlers
        success = True
        for handler, _, subscriber_id in handlers_to_call:
            try:
                handler(event)
                logger.debug(f"Successfully delivered event to subscriber '{subscriber_id}'")
            except Exception as e:
                logger.error(f"Error delivering event to subscriber '{subscriber_id}': {str(e)}")
                success = False
        
        return success
    
    def _matches_wildcard(self, event_type: str, pattern: str) -> bool:
        """
        Check if an event type matches a wildcard pattern.
        
        Args:
            event_type: The event type to check
            pattern: The wildcard pattern to match against
            
        Returns:
            Boolean indicating whether the event type matches the pattern
        """
        # Convert the pattern to a regex pattern
        import re
        regex_pattern = pattern.replace('.', '\\.').replace('*', '.*')
        return bool(re.match(f"^{regex_pattern}$", event_type))
    
    def get_subscribers(self, event_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get information about subscribers.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            Dictionary mapping subscriber IDs to lists of event types
        """
        if event_type is None:
            # Return all subscribers
            return {sid: events for sid, events in self._subscriber_registry.items()}
        else:
            # Return subscribers for a specific event type
            result = {}
            
            # Check direct subscribers
            if event_type in self._subscribers:
                for _, _, subscriber_id in self._subscribers[event_type]:
                    if subscriber_id not in result:
                        result[subscriber_id] = []
                    result[subscriber_id].append(event_type)
            
            # Check wildcard subscribers
            for pattern, subscribers in self._wildcard_subscribers.items():
                if self._matches_wildcard(event_type, pattern):
                    for _, _, subscriber_id in subscribers:
                        if subscriber_id not in result:
                            result[subscriber_id] = []
                        result[subscriber_id].append(pattern)
            
            return result


# Create a global event bus instance
event_bus = EventBus()


# Define some common event types
class CommonEventTypes:
    """Common event types used throughout the system."""
    # URL processing events
    URL_PROCESSING_STARTED = "url.processing.started"
    URL_PROCESSING_COMPLETED = "url.processing.completed"
    URL_PROCESSING_ERROR = "url.processing.error"
    
    # URL classification events
    URL_CLASSIFICATION_STARTED = "url.classification.started"
    URL_CLASSIFICATION_COMPLETED = "url.classification.completed"
    URL_CLASSIFICATION_ERROR = "url.classification.error"
    
    # Report generation events
    REPORT_GENERATION_STARTED = "report.generation.started"
    REPORT_GENERATION_COMPLETED = "report.generation.completed"
    REPORT_GENERATION_ERROR = "report.generation.error"
    
    # Data export events
    DATA_EXPORT_STARTED = "data.export.started"
    DATA_EXPORT_COMPLETED = "data.export.completed"
    DATA_EXPORT_ERROR = "data.export.error"
    
    # Plugin events
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_ERROR = "plugin.error"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    
    # Configuration events
    CONFIG_LOADED = "config.loaded"
    CONFIG_SAVED = "config.saved"
    CONFIG_ERROR = "config.error"