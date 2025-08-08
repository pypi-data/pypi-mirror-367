"""
Mentors Event Hub - Centralized event logging with Repository Pattern
"""

__version__ = "0.1.0"

from .event_hub_client import EventHubClient
from .event_hub import setup_global_hub, send_event, send_error, capture_errors
from .repository.event_repository import EventRepository

__all__ = [
    "EventHubClient",
    "EventRepository",
    "setup_global_hub", 
    "send_event",
    "send_error",
    "capture_errors"
]