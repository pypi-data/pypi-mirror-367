"""
Message queue module for URL Analyzer.

This module provides message queue integration for URL Analyzer,
allowing it to send and receive messages asynchronously.
"""

import json
import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from queue import Queue, Empty
from typing import Dict, List, Optional, Any, Callable, Union, TypeVar, Generic

# Configure logger
logger = logging.getLogger(__name__)

# Type variable for message payload
T = TypeVar('T')


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3
    
    def __str__(self) -> str:
        """Return string representation of the priority level."""
        return self.name


@dataclass
class Message(Generic[T]):
    """
    Message for queue processing.
    
    This class represents a message for asynchronous processing.
    
    Args:
        payload: The message payload
        message_type: The type of message
        priority: The message priority
        id: Unique identifier for the message
        timestamp: The message timestamp
        headers: Optional message headers
    """
    payload: T
    message_type: str
    priority: MessagePriority = MessagePriority.NORMAL
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return {
            "id": self.id,
            "message_type": self.message_type,
            "priority": str(self.priority),
            "timestamp": self.timestamp.isoformat(),
            "headers": self.headers,
            "payload": self.payload
        }
    
    def to_json(self) -> str:
        """Convert the message to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create a message from a dictionary.
        
        Args:
            data: The dictionary containing message data
            
        Returns:
            A new Message instance
        """
        priority = MessagePriority[data["priority"]] if isinstance(data["priority"], str) else data["priority"]
        timestamp = datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"]
        
        return cls(
            id=data["id"],
            message_type=data["message_type"],
            priority=priority,
            timestamp=timestamp,
            headers=data.get("headers", {}),
            payload=data["payload"]
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """
        Create a message from a JSON string.
        
        Args:
            json_str: The JSON string containing message data
            
        Returns:
            A new Message instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class MessageQueue(ABC, Generic[T]):
    """
    Abstract base class for message queues.
    
    This class defines the interface for message queues.
    """
    
    @abstractmethod
    def send(self, message: Message[T]) -> None:
        """
        Send a message to the queue.
        
        Args:
            message: The message to send
        """
        pass
    
    @abstractmethod
    def receive(self, timeout: Optional[float] = None) -> Optional[Message[T]]:
        """
        Receive a message from the queue.
        
        Args:
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            The received message, or None if no message is available
        """
        pass
    
    @abstractmethod
    def subscribe(self, message_type: str, callback: Callable[[Message[T]], None]) -> None:
        """
        Subscribe to messages of a specific type.
        
        Args:
            message_type: The message type to subscribe to
            callback: The callback function to call when a message is received
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, message_type: str, callback: Callable[[Message[T]], None]) -> bool:
        """
        Unsubscribe from messages of a specific type.
        
        Args:
            message_type: The message type to unsubscribe from
            callback: The callback function to unsubscribe
            
        Returns:
            True if the callback was unsubscribed, False otherwise
        """
        pass
    
    @abstractmethod
    def start(self) -> None:
        """Start the message queue."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the message queue."""
        pass


class InMemoryMessageQueue(MessageQueue[T]):
    """
    In-memory message queue.
    
    This class implements a message queue using an in-memory queue.
    """
    
    def __init__(self):
        """Initialize the in-memory message queue."""
        self.queue: Queue[Message[T]] = Queue()
        self.subscribers: Dict[str, List[Callable[[Message[T]], None]]] = {}
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        
        logger.debug("Initialized InMemoryMessageQueue")
    
    def send(self, message: Message[T]) -> None:
        """
        Send a message to the queue.
        
        Args:
            message: The message to send
        """
        self.queue.put(message)
        logger.debug(f"Sent message {message.id} of type {message.message_type} to queue")
    
    def receive(self, timeout: Optional[float] = None) -> Optional[Message[T]]:
        """
        Receive a message from the queue.
        
        Args:
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            The received message, or None if no message is available
        """
        try:
            message = self.queue.get(block=True, timeout=timeout)
            logger.debug(f"Received message {message.id} of type {message.message_type} from queue")
            return message
        except Empty:
            return None
    
    def subscribe(self, message_type: str, callback: Callable[[Message[T]], None]) -> None:
        """
        Subscribe to messages of a specific type.
        
        Args:
            message_type: The message type to subscribe to
            callback: The callback function to call when a message is received
        """
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        
        self.subscribers[message_type].append(callback)
        logger.debug(f"Subscribed to message type {message_type}")
    
    def unsubscribe(self, message_type: str, callback: Callable[[Message[T]], None]) -> bool:
        """
        Unsubscribe from messages of a specific type.
        
        Args:
            message_type: The message type to unsubscribe from
            callback: The callback function to unsubscribe
            
        Returns:
            True if the callback was unsubscribed, False otherwise
        """
        if message_type in self.subscribers and callback in self.subscribers[message_type]:
            self.subscribers[message_type].remove(callback)
            logger.debug(f"Unsubscribed from message type {message_type}")
            return True
        return False
    
    def start(self) -> None:
        """Start the message queue."""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(
                target=self._worker,
                daemon=True
            )
            self.worker_thread.start()
            logger.info("Started InMemoryMessageQueue")
    
    def stop(self) -> None:
        """Stop the message queue."""
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
        logger.info("Stopped InMemoryMessageQueue")
    
    def _worker(self) -> None:
        """Worker thread for processing messages."""
        while self.running:
            message = self.receive(timeout=0.1)
            
            if message is None:
                continue
            
            message_type = message.message_type
            
            # Call subscribers for this message type
            for callback in self.subscribers.get(message_type, []):
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in subscriber callback for message {message.id}: {e}")
            
            # Call subscribers for all message types
            for callback in self.subscribers.get("*", []):
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in wildcard subscriber callback for message {message.id}: {e}")


class MessageQueueManager:
    """
    Message queue manager.
    
    This class manages message queues and provides a unified interface for sending and receiving messages.
    """
    
    def __init__(self):
        """Initialize the message queue manager."""
        self.queues: Dict[str, MessageQueue] = {}
        self.default_queue: Optional[str] = None
        
        logger.debug("Initialized MessageQueueManager")
    
    def register_queue(self, name: str, queue: MessageQueue, default: bool = False) -> None:
        """
        Register a message queue.
        
        Args:
            name: The name of the queue
            queue: The message queue
            default: Whether this is the default queue
        """
        self.queues[name] = queue
        
        if default or self.default_queue is None:
            self.default_queue = name
        
        logger.info(f"Registered message queue {name}")
    
    def unregister_queue(self, name: str) -> bool:
        """
        Unregister a message queue.
        
        Args:
            name: The name of the queue
            
        Returns:
            True if the queue was unregistered, False otherwise
        """
        if name in self.queues:
            queue = self.queues.pop(name)
            queue.stop()
            
            if self.default_queue == name:
                self.default_queue = next(iter(self.queues)) if self.queues else None
            
            logger.info(f"Unregistered message queue {name}")
            return True
        return False
    
    def get_queue(self, name: Optional[str] = None) -> MessageQueue:
        """
        Get a message queue.
        
        Args:
            name: The name of the queue (default: default queue)
            
        Returns:
            The message queue
            
        Raises:
            ValueError: If the queue does not exist
        """
        queue_name = name or self.default_queue
        
        if queue_name is None or queue_name not in self.queues:
            raise ValueError(f"Queue {queue_name} does not exist")
        
        return self.queues[queue_name]
    
    def send(self, message: Message, queue_name: Optional[str] = None) -> None:
        """
        Send a message to a queue.
        
        Args:
            message: The message to send
            queue_name: The name of the queue (default: default queue)
        """
        queue = self.get_queue(queue_name)
        queue.send(message)
    
    def receive(self, queue_name: Optional[str] = None, timeout: Optional[float] = None) -> Optional[Message]:
        """
        Receive a message from a queue.
        
        Args:
            queue_name: The name of the queue (default: default queue)
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            The received message, or None if no message is available
        """
        queue = self.get_queue(queue_name)
        return queue.receive(timeout)
    
    def subscribe(self, message_type: str, callback: Callable[[Message], None], queue_name: Optional[str] = None) -> None:
        """
        Subscribe to messages of a specific type.
        
        Args:
            message_type: The message type to subscribe to
            callback: The callback function to call when a message is received
            queue_name: The name of the queue (default: default queue)
        """
        queue = self.get_queue(queue_name)
        queue.subscribe(message_type, callback)
    
    def unsubscribe(self, message_type: str, callback: Callable[[Message], None], queue_name: Optional[str] = None) -> bool:
        """
        Unsubscribe from messages of a specific type.
        
        Args:
            message_type: The message type to unsubscribe from
            callback: The callback function to unsubscribe
            queue_name: The name of the queue (default: default queue)
            
        Returns:
            True if the callback was unsubscribed, False otherwise
        """
        queue = self.get_queue(queue_name)
        return queue.unsubscribe(message_type, callback)
    
    def start_all(self) -> None:
        """Start all message queues."""
        for name, queue in self.queues.items():
            queue.start()
            logger.info(f"Started message queue {name}")
    
    def stop_all(self) -> None:
        """Stop all message queues."""
        for name, queue in self.queues.items():
            queue.stop()
            logger.info(f"Stopped message queue {name}")


# Create a default message queue manager
default_manager = MessageQueueManager()

# Register an in-memory queue as the default
default_manager.register_queue("memory", InMemoryMessageQueue(), default=True)

# Start the default queue
default_manager.get_queue("memory").start()


def send_message(message_type: str, payload: Any, priority: MessagePriority = MessagePriority.NORMAL, headers: Optional[Dict[str, str]] = None) -> str:
    """
    Send a message to the default queue.
    
    This is a convenience function for sending messages.
    
    Args:
        message_type: The type of message
        payload: The message payload
        priority: The message priority
        headers: Optional message headers
        
    Returns:
        The ID of the sent message
    """
    message = Message(
        message_type=message_type,
        payload=payload,
        priority=priority,
        headers=headers or {}
    )
    
    default_manager.send(message)
    return message.id


def subscribe(message_type: str, callback: Callable[[Message], None]) -> None:
    """
    Subscribe to messages of a specific type.
    
    This is a convenience function for subscribing to messages.
    
    Args:
        message_type: The message type to subscribe to
        callback: The callback function to call when a message is received
    """
    default_manager.subscribe(message_type, callback)


def unsubscribe(message_type: str, callback: Callable[[Message], None]) -> bool:
    """
    Unsubscribe from messages of a specific type.
    
    This is a convenience function for unsubscribing from messages.
    
    Args:
        message_type: The message type to unsubscribe from
        callback: The callback function to unsubscribe
        
    Returns:
        True if the callback was unsubscribed, False otherwise
    """
    return default_manager.unsubscribe(message_type, callback)