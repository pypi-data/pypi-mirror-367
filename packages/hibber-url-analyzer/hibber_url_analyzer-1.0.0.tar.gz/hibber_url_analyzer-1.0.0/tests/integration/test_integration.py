"""
Test file for URL Analyzer integration capabilities.

This file contains tests for the URL Analyzer integration capabilities,
including webhooks, data import/export, message queue, and batch processing.
"""

import os
import tempfile
import unittest
from typing import Dict, List, Any

# Import test fixtures
from tests import (
    create_test_urls, create_temp_config_file, create_temp_cache_file
)

from url_analyzer.integration.webhooks import (
    WebhookManager, Webhook, WebhookEvent, WebhookPayload
)
from url_analyzer.integration.exporters import (
    export_data, JSONExporter, CSVExporter
)
from url_analyzer.integration.importers import (
    import_data, import_urls_from_file
)
from url_analyzer.integration.queue import (
    Message, MessagePriority, InMemoryMessageQueue, send_message, subscribe
)
from url_analyzer.integration.batch import (
    BatchJob, BatchProcessor, BatchStatus, submit_batch_job, get_batch_job
)


class TestWebhooks(unittest.TestCase):
    """Test cases for webhooks."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.webhook_manager = WebhookManager()
        self.received_events = []
        
        # Create a test webhook
        self.webhook = Webhook(
            url="https://example.com/webhook",
            events=[WebhookEvent.URL_ANALYZED, WebhookEvent.BATCH_COMPLETED],
            name="Test Webhook"
        )
    
    def test_should_register_and_unregister_webhook_successfully(self):
        """Test that webhooks can be registered and unregistered successfully."""
        # Register the webhook
        webhook_id = self.webhook_manager.register_webhook(self.webhook)
        
        # Check that the webhook was registered
        self.assertIn(webhook_id, [w.id for w in self.webhook_manager.get_webhooks()])
        
        # Unregister the webhook
        result = self.webhook_manager.unregister_webhook(webhook_id)
        
        # Check that the webhook was unregistered
        self.assertTrue(result)
        self.assertNotIn(webhook_id, [w.id for w in self.webhook_manager.get_webhooks()])
    
    def test_should_handle_webhook_events_correctly(self):
        """Test that webhook events are handled and processed correctly."""
        # Define an event handler
        def event_handler(event, data):
            self.received_events.append((event, data))
        
        # Register the event handler
        self.webhook_manager.register_event_handler(WebhookEvent.URL_ANALYZED, event_handler)
        
        # Trigger an event
        test_data = {"url": "https://example.com", "category": "Example"}
        self.webhook_manager.trigger_event(WebhookEvent.URL_ANALYZED, test_data)
        
        # Start the webhook manager to process events
        self.webhook_manager.start()
        
        # Wait for events to be processed
        import time
        time.sleep(0.1)
        
        # Stop the webhook manager
        self.webhook_manager.stop()
        
        # Check that the event was handled
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0][0], WebhookEvent.URL_ANALYZED)
        self.assertEqual(self.received_events[0][1], test_data)


class TestDataExport(unittest.TestCase):
    """Test cases for data export."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = [
            {"url": "https://example.com", "category": "Example", "is_sensitive": False},
            {"url": "https://example.org", "category": "Example", "is_sensitive": True},
            {"url": "https://example.net", "category": "Example", "is_sensitive": False}
        ]
        
        # Create temporary files for export
        self.temp_json = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_csv = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        
        self.temp_json.close()
        self.temp_csv.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        for temp_file in [self.temp_json, self.temp_csv]:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_should_export_and_import_data_in_json_format(self):
        """Test that data can be exported to JSON format and imported back correctly."""
        # Export data to JSON
        export_data(self.test_data, self.temp_json.name)
        
        # Import data from JSON
        imported_data = import_data(self.temp_json.name)
        
        # Check that the imported data matches the original data
        self.assertEqual(imported_data, self.test_data)
    
    def test_should_export_and_import_data_in_csv_format(self):
        """Test that data can be exported to CSV format and imported back correctly."""
        # Export data to CSV
        export_data(self.test_data, self.temp_csv.name)
        
        # Import data from CSV
        imported_data = import_data(self.temp_csv.name, as_dict_list=True)
        
        # Check that the imported data has the same length as the original data
        self.assertEqual(len(imported_data), len(self.test_data))
        
        # Check that all the original URLs are in the imported data
        original_urls = [item["url"] for item in self.test_data]
        imported_urls = [item["url"] for item in imported_data]
        for url in original_urls:
            self.assertIn(url, imported_urls)


class TestDataImport(unittest.TestCase):
    """Test cases for data import."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use fixture utility function for test URLs
        self.test_urls = create_test_urls()[:3]  # Use first 3 URLs
        
        # Create a temporary file with URLs
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w")
        for url in self.test_urls:
            self.temp_file.write(f"{url}\n")
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_should_import_urls_from_file_successfully(self):
        """Test that URLs can be imported from a text file successfully."""
        # Import URLs from the file
        imported_urls = []
        with open(self.temp_file.name, "r") as f:
            for line in f:
                imported_urls.append(line.strip())
        
        # Check that the imported URLs match the original URLs
        self.assertEqual(imported_urls, self.test_urls)


class TestMessageQueue(unittest.TestCase):
    """Test cases for message queue."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.queue = InMemoryMessageQueue()
        self.received_messages = []
        
        # Start the queue
        self.queue.start()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Stop the queue
        self.queue.stop()
    
    def test_should_send_and_receive_messages_successfully(self):
        """Test that messages can be sent to and received from the queue successfully."""
        # Create a message
        message = Message(
            message_type="test",
            payload={"key": "value"}
        )
        
        # Send the message
        self.queue.send(message)
        
        # Receive the message
        received = self.queue.receive(timeout=0.1)
        
        # Check that the received message matches the sent message
        self.assertIsNotNone(received)
        self.assertEqual(received.message_type, message.message_type)
        self.assertEqual(received.payload, message.payload)
    
    def test_should_subscribe_to_messages_and_receive_notifications(self):
        """Test that message handlers can subscribe to specific message types and receive notifications."""
        # Define a message handler
        def message_handler(message):
            self.received_messages.append(message)
        
        # Subscribe to messages
        self.queue.subscribe("test", message_handler)
        
        # Send a message
        message = Message(
            message_type="test",
            payload={"key": "value"}
        )
        self.queue.send(message)
        
        # Wait for the message to be processed
        import time
        time.sleep(0.1)
        
        # Check that the message was received
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0].message_type, message.message_type)
        self.assertEqual(self.received_messages[0].payload, message.payload)


class TestBatchProcessing(unittest.TestCase):
    """Test cases for batch processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_urls = [
            "https://example.com",
            "https://example.org",
            "https://example.net"
        ]
        
        # Create a temporary output file
        self.temp_output = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_output.close()
        
        # Create a batch processor
        self.processor = BatchProcessor()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_output.name):
            os.unlink(self.temp_output.name)
    
    def test_should_create_batch_job_with_correct_properties(self):
        """Test that batch jobs can be created with the correct properties and initial status."""
        # Create a batch job
        job = BatchJob(
            name="Test Job",
            urls=self.test_urls,
            output_path=self.temp_output.name
        )
        
        # Check job properties
        self.assertEqual(job.name, "Test Job")
        self.assertEqual(job.urls, self.test_urls)
        self.assertEqual(job.output_path, self.temp_output.name)
        self.assertEqual(job.status, BatchStatus.PENDING)
    
    def test_should_submit_and_retrieve_batch_job_successfully(self):
        """Test that batch jobs can be submitted and retrieved successfully with correct properties."""
        # Submit a batch job
        job_id = submit_batch_job(
            name="Test Job",
            urls=self.test_urls,
            output_path=self.temp_output.name
        )
        
        # Check that the job was submitted
        self.assertIsNotNone(job_id)
        
        # Get the job
        job = get_batch_job(job_id)
        
        # Check that the job exists
        self.assertIsNotNone(job)
        self.assertEqual(job.name, "Test Job")


if __name__ == "__main__":
    unittest.main()