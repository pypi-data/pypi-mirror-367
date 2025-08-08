"""YouTrack REST Client - A limited client library for accessing YouTrack REST API."""

from .connection import Connection
from .issue import Issue
from .project import Project

__version__ = "0.1.0"
__all__ = ["Connection", "Issue", "Project"]