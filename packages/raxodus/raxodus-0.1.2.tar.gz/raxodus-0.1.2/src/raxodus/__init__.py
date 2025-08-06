"""raxodus - Escape from Rackspace ticket hell."""

from .client import RackspaceClient
from .models import Ticket, TicketList
from .version import __codename__, __tagline__, __version__, get_avatar_url, get_version_info

__author__ = "Brian Morin"

__all__ = [
    "RackspaceClient",
    "Ticket",
    "TicketList",
    "__version__",
    "__codename__",
    "__tagline__",
    "get_avatar_url",
    "get_version_info",
]
