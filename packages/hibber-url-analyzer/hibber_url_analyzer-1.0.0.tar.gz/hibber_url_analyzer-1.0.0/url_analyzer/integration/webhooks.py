"""
Webhooks module for URL Analyzer.

This module provides webhook functionality for URL Analyzer,
allowing it to send event notifications to external systems.
"""

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Union
import requests

# Configure logger
logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    """Webhook event types."""
    URL_ANALYZED = auto()
    BATCH_COMPLETED = auto()
    REPORT_GENERATED = auto()
    CLASSIFICATION_UPDATED = auto()
    SYSTEM_ERROR = auto()
    CACHE_CLEARED = auto()
    
    def __str__(self) -> str:
        """Return string representation of the event type."""
        return self.name


@dataclass
class Webhook:
    """
    Webhook configuration.
    
    This class represents a webhook configuration for sending event notifications.
    
    Args:
        url: The URL to send webhook notifications to
        events: List of event types to send notifications for
        name: Optional name for the webhook
        headers: Optional HTTP headers to include in webhook requests
        secret: Optional secret for signing webhook payloads
        enabled: Whether the webhook is enabled
        id: Unique identifier for the webhook
    """
    url: str
    events: List[WebhookEvent]
    name: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    secret: Optional[str] = None
    enabled: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Validate the webhook configuration."""
        if not self.url:
            raise ValueError("Webhook URL is required")
        
        if not self.events:
            raise ValueError("At least one event type is required")
        
        # Add default headers if not present
        if "Content-Type" not in self.headers:
            self.headers["Content-Type"] = "application/json"
        
        # Add a name if not provided
        if not self.name:
            self.name = f"webhook-{self.id[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the webhook to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "events": [str(event) for event in self.events],
            "headers": self.headers,
            "enabled": self.enabled,
            "has_secret": self.secret is not None
        }


@dataclass
class WebhookPayload:
    """
    Webhook payload.
    
    This class represents a webhook payload for sending event notifications.
    
    Args:
        event: The event type
        data: The event data
        timestamp: The event timestamp
        webhook_id: The ID of the webhook
    """
    event: WebhookEvent
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    webhook_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the payload to a dictionary."""
        return {
            "event": str(self.event),
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "webhook_id": self.webhook_id
        }
    
    def to_json(self) -> str:
        """Convert the payload to a JSON string."""
        return json.dumps(self.to_dict())


class WebhookManager:
    """
    Webhook manager.
    
    This class manages webhooks and sends event notifications.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the webhook manager.
        
        Args:
            config_path: Optional path to a webhook configuration file
        """
        self.webhooks: Dict[str, Webhook] = {}
        self.event_handlers: Dict[WebhookEvent, List[Callable]] = {
            event: [] for event in WebhookEvent
        }
        self.delivery_queue: List[Dict[str, Any]] = []
        self.delivery_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Load webhooks from configuration if provided
        if config_path:
            self.load_webhooks(config_path)
        
        logger.debug("Initialized WebhookManager")
    
    def register_webhook(self, webhook: Webhook) -> str:
        """
        Register a webhook.
        
        Args:
            webhook: The webhook to register
            
        Returns:
            The ID of the registered webhook
        """
        self.webhooks[webhook.id] = webhook
        logger.info(f"Registered webhook {webhook.name} ({webhook.id}) for events: {', '.join(str(e) for e in webhook.events)}")
        return webhook.id
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """
        Unregister a webhook.
        
        Args:
            webhook_id: The ID of the webhook to unregister
            
        Returns:
            True if the webhook was unregistered, False otherwise
        """
        if webhook_id in self.webhooks:
            webhook = self.webhooks.pop(webhook_id)
            logger.info(f"Unregistered webhook {webhook.name} ({webhook_id})")
            return True
        return False
    
    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """
        Get a webhook by ID.
        
        Args:
            webhook_id: The ID of the webhook to get
            
        Returns:
            The webhook if found, None otherwise
        """
        return self.webhooks.get(webhook_id)
    
    def get_webhooks(self) -> List[Webhook]:
        """
        Get all registered webhooks.
        
        Returns:
            List of all registered webhooks
        """
        return list(self.webhooks.values())
    
    def trigger_event(self, event: WebhookEvent, data: Dict[str, Any]) -> None:
        """
        Trigger an event.
        
        This method triggers an event and sends notifications to all registered webhooks
        that are subscribed to the event.
        
        Args:
            event: The event to trigger
            data: The event data
        """
        logger.debug(f"Triggering event {event}")
        
        # Call event handlers
        for handler in self.event_handlers.get(event, []):
            try:
                handler(event, data)
            except Exception as e:
                logger.error(f"Error in event handler for {event}: {e}")
        
        # Queue webhook deliveries
        for webhook_id, webhook in self.webhooks.items():
            if webhook.enabled and event in webhook.events:
                payload = WebhookPayload(
                    event=event,
                    data=data,
                    webhook_id=webhook_id
                )
                
                delivery = {
                    "webhook": webhook,
                    "payload": payload,
                    "attempts": 0,
                    "max_attempts": 3,
                    "next_attempt": time.time()
                }
                
                self.delivery_queue.append(delivery)
                logger.debug(f"Queued webhook delivery for {webhook.name} ({webhook_id})")
        
        # Start delivery thread if not already running
        self._ensure_delivery_thread()
    
    def register_event_handler(self, event: WebhookEvent, handler: Callable) -> None:
        """
        Register an event handler.
        
        Args:
            event: The event to handle
            handler: The handler function
        """
        self.event_handlers[event].append(handler)
        logger.debug(f"Registered event handler for {event}")
    
    def unregister_event_handler(self, event: WebhookEvent, handler: Callable) -> bool:
        """
        Unregister an event handler.
        
        Args:
            event: The event to handle
            handler: The handler function
            
        Returns:
            True if the handler was unregistered, False otherwise
        """
        if event in self.event_handlers and handler in self.event_handlers[event]:
            self.event_handlers[event].remove(handler)
            logger.debug(f"Unregistered event handler for {event}")
            return True
        return False
    
    def load_webhooks(self, config_path: str) -> None:
        """
        Load webhooks from a configuration file.
        
        Args:
            config_path: Path to the webhook configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            for webhook_config in config.get("webhooks", []):
                try:
                    events = [WebhookEvent[e] for e in webhook_config.get("events", [])]
                    webhook = Webhook(
                        url=webhook_config["url"],
                        events=events,
                        name=webhook_config.get("name"),
                        headers=webhook_config.get("headers", {}),
                        secret=webhook_config.get("secret"),
                        enabled=webhook_config.get("enabled", True),
                        id=webhook_config.get("id", str(uuid.uuid4()))
                    )
                    self.register_webhook(webhook)
                except (KeyError, ValueError) as e:
                    logger.error(f"Error loading webhook: {e}")
            
            logger.info(f"Loaded {len(self.webhooks)} webhooks from {config_path}")
        except Exception as e:
            logger.error(f"Error loading webhooks from {config_path}: {e}")
    
    def save_webhooks(self, config_path: str) -> None:
        """
        Save webhooks to a configuration file.
        
        Args:
            config_path: Path to the webhook configuration file
        """
        try:
            config = {
                "webhooks": [
                    {
                        "id": webhook.id,
                        "name": webhook.name,
                        "url": webhook.url,
                        "events": [str(event) for event in webhook.events],
                        "headers": webhook.headers,
                        "secret": webhook.secret,
                        "enabled": webhook.enabled
                    }
                    for webhook in self.webhooks.values()
                ]
            }
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved {len(self.webhooks)} webhooks to {config_path}")
        except Exception as e:
            logger.error(f"Error saving webhooks to {config_path}: {e}")
    
    def _ensure_delivery_thread(self) -> None:
        """Ensure the delivery thread is running."""
        if self.delivery_thread is None or not self.delivery_thread.is_alive():
            self.running = True
            self.delivery_thread = threading.Thread(
                target=self._delivery_worker,
                daemon=True
            )
            self.delivery_thread.start()
            logger.debug("Started webhook delivery thread")
    
    def _delivery_worker(self) -> None:
        """Worker thread for delivering webhooks."""
        while self.running and self.delivery_queue:
            current_time = time.time()
            
            # Find the next delivery to attempt
            next_delivery = None
            next_index = -1
            
            for i, delivery in enumerate(self.delivery_queue):
                if delivery["next_attempt"] <= current_time:
                    next_delivery = delivery
                    next_index = i
                    break
            
            if next_delivery is None:
                # No deliveries ready yet, sleep for a bit
                time.sleep(0.1)
                continue
            
            # Remove the delivery from the queue
            self.delivery_queue.pop(next_index)
            
            # Attempt to deliver the webhook
            webhook = next_delivery["webhook"]
            payload = next_delivery["payload"]
            
            try:
                response = requests.post(
                    webhook.url,
                    headers=webhook.headers,
                    data=payload.to_json(),
                    timeout=5
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(f"Webhook delivery successful: {webhook.name} ({webhook.id})")
                else:
                    logger.warning(f"Webhook delivery failed: {webhook.name} ({webhook.id}) - Status code: {response.status_code}")
                    
                    # Requeue for retry if not too many attempts
                    if next_delivery["attempts"] < next_delivery["max_attempts"]:
                        next_delivery["attempts"] += 1
                        next_delivery["next_attempt"] = current_time + (2 ** next_delivery["attempts"])
                        self.delivery_queue.append(next_delivery)
                        logger.debug(f"Requeued webhook delivery for {webhook.name} ({webhook.id}) - Attempt {next_delivery['attempts']}")
            except Exception as e:
                logger.error(f"Error delivering webhook: {webhook.name} ({webhook.id}) - {e}")
                
                # Requeue for retry if not too many attempts
                if next_delivery["attempts"] < next_delivery["max_attempts"]:
                    next_delivery["attempts"] += 1
                    next_delivery["next_attempt"] = current_time + (2 ** next_delivery["attempts"])
                    self.delivery_queue.append(next_delivery)
                    logger.debug(f"Requeued webhook delivery for {webhook.name} ({webhook.id}) - Attempt {next_delivery['attempts']}")
        
        # No more deliveries, stop the thread
        self.running = False
        logger.debug("Webhook delivery thread stopped")
    
    def stop(self) -> None:
        """Stop the webhook manager."""
        self.running = False
        if self.delivery_thread and self.delivery_thread.is_alive():
            self.delivery_thread.join(timeout=1.0)
        logger.info("Webhook manager stopped")