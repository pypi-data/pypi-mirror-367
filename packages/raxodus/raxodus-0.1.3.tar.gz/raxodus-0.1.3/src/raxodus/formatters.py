"""Output formatters for different formats."""

import csv
import io
import json
from typing import Any, Dict

from rich.console import Console
from rich.table import Table

from .models import TicketList


def format_json(data: Dict[str, Any]) -> str:
    """Format data as JSON.

    Args:
        data: Data to format

    Returns:
        JSON string
    """
    return json.dumps(data, indent=2, default=str)


def format_table(ticket_list: TicketList) -> str:
    """Format tickets as a rich table.

    Args:
        ticket_list: List of tickets

    Returns:
        Formatted table string
    """
    console = Console()

    table = Table(title=f"Tickets ({ticket_list.total} total)")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Subject", style="white")
    table.add_column("Status", style="yellow")
    table.add_column("Severity", style="red")
    table.add_column("Created", style="green")

    for ticket in ticket_list.tickets:
        table.add_row(
            ticket.id,
            ticket.subject[:50] + ("..." if len(ticket.subject) > 50 else ""),
            ticket.status,
            ticket.severity or "N/A",
            ticket.created_at.strftime("%Y-%m-%d %H:%M"),
        )

    # Capture table output
    with console.capture() as capture:
        console.print(table)

    return capture.get()


def format_csv(ticket_list: TicketList) -> str:
    """Format tickets as CSV.

    Args:
        ticket_list: List of tickets

    Returns:
        CSV string
    """
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id",
            "subject",
            "status",
            "severity",
            "category",
            "created_at",
            "updated_at",
            "requester",
            "assigned_to",
        ],
    )

    writer.writeheader()

    for ticket in ticket_list.tickets:
        writer.writerow({
            "id": ticket.id,
            "subject": ticket.subject,
            "status": ticket.status,
            "severity": ticket.severity or "",
            "category": ticket.category or "",
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
            "requester": ticket.requester or "",
            "assigned_to": ticket.assigned_to or "",
        })

    return output.getvalue()
