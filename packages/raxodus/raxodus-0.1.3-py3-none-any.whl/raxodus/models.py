"""Pydantic models for Rackspace API responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TicketAttachment(BaseModel):
    """Attachment on a ticket."""

    id: str
    filename: str
    size: int
    created_at: datetime
    url: Optional[str] = None


class TicketComment(BaseModel):
    """Comment on a ticket."""

    id: str
    author: str
    created_at: datetime
    body: str
    is_public: bool = True
    attachments: List[TicketAttachment] = Field(default_factory=list)


class Ticket(BaseModel):
    """Rackspace support ticket."""

    # Core fields that always exist in list responses
    ticketId: str
    subject: str
    status: str
    modified: datetime

    # Optional fields
    severity: Optional[str] = ""
    accountId: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    created: Optional[datetime] = None  # Not in list response
    createdAt: Optional[datetime] = None  # Sometimes this field
    favorite: Optional[bool] = False
    resources: List[str] = Field(default_factory=list)
    createdBy: Optional[Dict[str, Any]] = None
    modifiedBy: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    resolution: Optional[str] = None
    comments: List[TicketComment] = Field(default_factory=list)
    recipients: Optional[Any] = None  # Can be null

    # Convenience properties
    @property
    def id(self) -> str:
        """Alias for ticketId."""
        return self.ticketId

    @property
    def created_at(self) -> Optional[datetime]:
        """Get created timestamp."""
        return self.created or self.createdAt

    @property
    def updated_at(self) -> datetime:
        """Alias for modified."""
        return self.modified

    class Config:
        extra = "ignore"  # Future-proof against API changes

    @field_validator("status")
    @classmethod
    def normalize_status(cls, v: str) -> str:
        """Normalize status values."""
        return v.lower().replace(" ", "_")

    def to_summary(self) -> Dict[str, Any]:
        """Return a summary dict for list views."""
        return {
            "id": self.id,
            "subject": self.subject,
            "status": self.status,
            "severity": self.severity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat(),
        }

    def to_dict_with_metadata(self, include_metadata: bool = False) -> Dict[str, Any]:
        """Return dict with optional metadata.

        Args:
            include_metadata: Include timing and cache metadata
        """
        result = self.model_dump(mode="json")

        if include_metadata and hasattr(self, "_elapsed_seconds"):
            result["_metadata"] = {
                "elapsed_seconds": getattr(self, "_elapsed_seconds", None),
                "from_cache": getattr(self, "_from_cache", False),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        return result


class TicketList(BaseModel):
    """List of tickets response."""

    tickets: List[Ticket]
    total: int
    page: int = 1
    per_page: int = 100
    elapsed_seconds: Optional[float] = None  # API response time
    from_cache: bool = False  # Whether this was from cache

    def to_summary(self, include_metadata: bool = False) -> Dict[str, Any]:
        """Return summary for JSON output.

        Args:
            include_metadata: Include timing and cache metadata
        """
        result = {
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "tickets": [t.to_summary() for t in self.tickets],
        }

        if include_metadata:
            result["_metadata"] = {
                "elapsed_seconds": self.elapsed_seconds,
                "from_cache": self.from_cache,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        return result


class AuthToken(BaseModel):
    """Authentication token response."""

    token: str
    expires_at: datetime
    user_id: str
    accounts: List[str] = Field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at


class RackspaceAccount(BaseModel):
    """Rackspace account information."""

    id: str
    name: str
    type: str = "managed"
    status: str = "active"

    class Config:
        extra = "ignore"
