"""Rackspace API client."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .exceptions import AuthenticationError, RateLimitError, RaxodusError
from .models import AuthToken, Ticket, TicketList


class RackspaceClient:
    """Client for interacting with Rackspace API."""

    # Default URLs - can be overridden via environment or init
    DEFAULT_AUTH_URL = "https://identity.api.rackspacecloud.com"
    DEFAULT_TICKET_API_URL = "https://demo.ticketing.api.rackspace.com"

    def __init__(
        self,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
        account: Optional[str] = None,
        auth_url: Optional[str] = None,
        ticket_api_url: Optional[str] = None,
        region: str = "us",
        cache_dir: Optional[Path] = None,
        cache_ttl: int = 300,
        timeout: float = 30.0,
    ):
        """Initialize Rackspace client.

        Args:
            username: Rackspace username (or from RACKSPACE_USERNAME env)
            api_key: API key (or from RACKSPACE_API_KEY env)
            account: Default account number (or from RACKSPACE_ACCOUNT env)
            auth_url: Authentication URL (or from RACKSPACE_AUTH_URL env)
            ticket_api_url: Ticket API URL (or from RACKSPACE_TICKET_API_URL env)
            region: API region (default: us)
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds
            timeout: HTTP timeout in seconds
        """
        self.username = username or os.getenv("RACKSPACE_USERNAME")
        self.api_key = api_key or os.getenv("RACKSPACE_API_KEY")
        self.account = account or os.getenv("RACKSPACE_ACCOUNT")
        self.auth_url = auth_url or os.getenv("RACKSPACE_AUTH_URL", self.DEFAULT_AUTH_URL)
        self.ticket_api_url = ticket_api_url or os.getenv("RACKSPACE_TICKET_API_URL", self.DEFAULT_TICKET_API_URL)
        self.region = region
        self.timeout = timeout

        if not self.username or not self.api_key:
            raise RaxodusError(
                "Missing credentials. Set RACKSPACE_USERNAME and RACKSPACE_API_KEY"
            )

        # Setup caching
        self.cache_dir = cache_dir or Path.home() / ".cache" / "raxodus"
        self.cache_ttl = cache_ttl
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # HTTP client
        self.client = httpx.Client(
            timeout=self.timeout,
            headers={"User-Agent": "raxodus/0.1.0"},
        )

        # Auth state
        self._token: Optional[AuthToken] = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close HTTP client."""
        self.client.close()

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
    )
    def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method
            url: URL to request
            **kwargs: Additional arguments for httpx

        Returns:
            HTTP response

        Raises:
            RateLimitError: If rate limited
            RaxodusError: For other errors
        """
        try:
            response = self.client.request(method, url, **kwargs)

            if response.status_code == 429:
                raise RateLimitError("Rate limited by Rackspace API")

            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid credentials or expired token") from e
            elif e.response.status_code == 403:
                raise AuthenticationError("Access denied") from e
            else:
                raise RaxodusError(f"API error: {e}") from e
        except httpx.RequestError as e:
            raise RaxodusError(f"Request failed: {e}") from e

    def authenticate(self) -> AuthToken:
        """Authenticate with Rackspace API.

        Returns:
            Authentication token

        Raises:
            AuthenticationError: If authentication fails
        """
        # Check cached token
        if self._token and not self._token.is_expired:
            return self._token

        # Request new token
        auth_data = {
            "auth": {
                "RAX-KSKEY:apiKeyCredentials": {
                    "username": self.username,
                    "apiKey": self.api_key,
                }
            }
        }

        response = self._request(
            "POST",
            f"{self.auth_url}/v2.0/tokens",
            json=auth_data,
        )

        data = response.json()

        # Parse token
        token_data = data["access"]["token"]
        self._token = AuthToken(
            token=token_data["id"],
            expires_at=datetime.fromisoformat(
                token_data["expires"].replace("Z", "+00:00")
            ),
            user_id=data["access"]["user"]["id"],
            accounts=[
                svc["name"]
                for svc in data["access"].get("serviceCatalog", [])
                if svc["type"] == "account"
            ],
        )

        return self._token

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token.

        Returns:
            Headers dict
        """
        token = self.authenticate()
        return {
            "X-Auth-Token": token.token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def list_tickets(
        self,
        account: Optional[str] = None,
        status: Optional[str] = None,
        days: Optional[int] = None,
        page: int = 1,
        per_page: int = 100,
    ) -> TicketList:
        """List support tickets.

        Args:
            account: Account number (uses default if not provided)
            status: Filter by status
            days: Show tickets from last N days
            page: Page number
            per_page: Results per page

        Returns:
            List of tickets
        """
        import time

        account = account or self.account
        if not account:
            raise RaxodusError("Account number required")

        # Build query parameters
        params = {
            "page": page,
            "per_page": per_page,
        }

        if status:
            params["status"] = status

        if days:
            since = datetime.utcnow() - timedelta(days=days)
            params["since"] = since.isoformat()

        # Check cache
        cache_key = f"tickets_{account}_{status}_{days}_{page}_{per_page}"
        cached = self._get_cached(cache_key)
        if cached:
            result = TicketList(**cached)
            result.from_cache = True
            result.elapsed_seconds = 0.0
            return result

        # Make request with timing
        start_time = time.time()
        response = self._request(
            "GET",
            f"{self.ticket_api_url}/tickets",
            headers=self._get_headers(),
            params=params,
        )
        elapsed = time.time() - start_time

        data = response.json()

        # Parse tickets
        tickets = [Ticket(**t) for t in data.get("tickets", [])]
        result = TicketList(
            tickets=tickets,
            total=data.get("total", len(tickets)),
            page=page,
            per_page=per_page,
            elapsed_seconds=round(elapsed, 3),
            from_cache=False,
        )

        # Cache result
        self._set_cached(cache_key, result.model_dump(mode="json"))

        return result

    def get_ticket(
        self,
        ticket_id: str,
        account: Optional[str] = None,
    ) -> Ticket:
        """Get a specific ticket.

        Args:
            ticket_id: Ticket ID
            account: Account number (uses default if not provided)

        Returns:
            Ticket details
        """
        import time

        account = account or self.account
        if not account:
            raise RaxodusError("Account number required")

        # Check cache
        cache_key = f"ticket_{account}_{ticket_id}"
        cached = self._get_cached(cache_key)
        if cached:
            ticket = Ticket(**cached)
            # Add timing metadata
            ticket._elapsed_seconds = 0.0
            ticket._from_cache = True
            return ticket

        # Make request with timing
        start_time = time.time()
        response = self._request(
            "GET",
            f"{self.ticket_api_url}/tickets/{ticket_id}",
            headers=self._get_headers(),
        )
        elapsed = time.time() - start_time

        data = response.json()
        ticket = Ticket(**data)

        # Add timing metadata (using private attrs)
        ticket._elapsed_seconds = round(elapsed, 3)
        ticket._from_cache = False

        # Cache result
        self._set_cached(cache_key, ticket.model_dump(mode="json"))

        return ticket


    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if available and not expired.

        Args:
            key: Cache key

        Returns:
            Cached data or None
        """
        if not self.cache_dir:
            return None

        cache_file = self.cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None

        # Check age
        age = datetime.now().timestamp() - cache_file.stat().st_mtime
        if age > self.cache_ttl:
            return None

        try:
            return json.loads(cache_file.read_text())
        except (json.JSONDecodeError, IOError):
            return None

    def _set_cached(self, key: str, data: Dict[str, Any]) -> None:
        """Cache data.

        Args:
            key: Cache key
            data: Data to cache
        """
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / f"{key}.json"
        try:
            cache_file.write_text(json.dumps(data, default=str))
        except IOError:
            pass  # Ignore cache write failures
