"""
RabbitMQ message queue manager for user events
"""
import json
import logging
from typing import Any, Dict

import pika
from decouple import config

logger = logging.getLogger(__name__)


class MessageQueueManager:
    """
    Manager for publishing user events to RabbitMQ
    """

    def __init__(self):
        """Initialize RabbitMQ connection"""
        self.rabbitmq_url = config("RABBITMQ_URL", default=None)
        self.connection = None
        self.channel = None
        self._setup_connection()

    def _setup_connection(self):
        """Setup RabbitMQ connection and channel"""
        if not self.rabbitmq_url:
            logger.warning("RABBITMQ_URL not configured, message queue disabled")
            return

        try:
            params = pika.URLParameters(self.rabbitmq_url)
            params.socket_timeout = 5
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()

            # Declare exchanges
            self.channel.exchange_declare(
                exchange="user_events", exchange_type="topic", durable=True
            )

            # Declare queues
            self.channel.queue_declare(queue="user_registrations", durable=True)
            self.channel.queue_declare(queue="user_updates", durable=True)
            self.channel.queue_declare(queue="notification_preferences", durable=True)
            self.channel.queue_declare(queue="push_tokens", durable=True)

            # Bind queues to exchange
            self.channel.queue_bind(
                exchange="user_events",
                queue="user_registrations",
                routing_key="user.registered",
            )
            self.channel.queue_bind(
                exchange="user_events", queue="user_updates", routing_key="user.updated"
            )
            self.channel.queue_bind(
                exchange="user_events",
                queue="notification_preferences",
                routing_key="preferences.*",
            )
            self.channel.queue_bind(
                exchange="user_events", queue="push_tokens", routing_key="token.*"
            )

            logger.info("RabbitMQ connection established successfully")
        except Exception as e:
            logger.error(f"Failed to setup RabbitMQ connection: {e}")
            self.connection = None
            self.channel = None

    def _ensure_connection(self):
        """Ensure connection is alive, reconnect if needed"""
        if not self.rabbitmq_url:
            return False

        if not self.connection or self.connection.is_closed:
            self._setup_connection()

        return self.channel is not None and self.channel.is_open

    def publish_event(
        self, routing_key: str, event_data: Dict[str, Any], priority: int = 0
    ) -> bool:
        """
        Publish an event to RabbitMQ

        Args:
            routing_key: Routing key for the event (e.g., 'user.registered')
            event_data: Event data to publish
            priority: Message priority (0-9)

        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_connection():
            logger.warning("RabbitMQ not available, event not published")
            return False

        try:
            message = json.dumps(event_data)

            self.channel.basic_publish(
                exchange="user_events",
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type="application/json",
                    priority=priority,
                ),
            )

            logger.info(f"Published event: {routing_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish event {routing_key}: {e}")
            return False

    def publish_user_registered(self, user_id: str, email: str, username: str) -> bool:
        """
        Publish user registration event

        Args:
            user_id: User UUID
            email: User email
            username: Username

        Returns:
            True if successful
        """
        event_data = {
            "event_type": "user_registered",
            "user_id": str(user_id),
            "email": email,
            "username": username,
            "timestamp": None,  # Will be set by the consumer
        }
        return self.publish_event("user.registered", event_data, priority=5)

    def publish_user_updated(self, user_id: str, updated_fields: Dict[str, Any]) -> bool:
        """
        Publish user update event

        Args:
            user_id: User UUID
            updated_fields: Dictionary of updated fields

        Returns:
            True if successful
        """
        event_data = {
            "event_type": "user_updated",
            "user_id": str(user_id),
            "updated_fields": updated_fields,
            "timestamp": None,
        }
        return self.publish_event("user.updated", event_data)

    def publish_preferences_updated(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Publish notification preferences update event

        Args:
            user_id: User UUID
            preferences: Notification preferences

        Returns:
            True if successful
        """
        event_data = {
            "event_type": "preferences_updated",
            "user_id": str(user_id),
            "preferences": preferences,
            "timestamp": None,
        }
        return self.publish_event("preferences.updated", event_data)

    def publish_push_token_added(self, user_id: str, token: str, device_type: str) -> bool:
        """
        Publish push token added event

        Args:
            user_id: User UUID
            token: Push token
            device_type: Device type (ios, android, web)

        Returns:
            True if successful
        """
        event_data = {
            "event_type": "push_token_added",
            "user_id": str(user_id),
            "token": token,
            "device_type": device_type,
            "timestamp": None,
        }
        return self.publish_event("token.added", event_data, priority=3)

    def publish_push_token_removed(self, user_id: str, token: str) -> bool:
        """
        Publish push token removed event

        Args:
            user_id: User UUID
            token: Push token

        Returns:
            True if successful
        """
        event_data = {
            "event_type": "push_token_removed",
            "user_id": str(user_id),
            "token": token,
            "timestamp": None,
        }
        return self.publish_event("token.removed", event_data)

    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")


# Global message queue manager instance
mq_manager = MessageQueueManager()
