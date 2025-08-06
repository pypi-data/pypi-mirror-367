"""Command-line interface for raxodus."""

import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __codename__, __tagline__, __version__, get_avatar_url
from .client import RackspaceClient
from .exceptions import AuthenticationError, RaxodusError
from .formatters import format_csv, format_json, format_table
from .shell_completions import COMPLETION_SCRIPTS, detect_shell, install_completion

console = Console()


def version_callback(ctx, param, value):
    """Show detailed version information."""
    if not value or ctx.resilient_parsing:
        return

    console.print(Panel.fit(
        f"[bold cyan]raxodus[/bold cyan] v{__version__}\n"
        f"[yellow]Codename:[/yellow] {__codename__}\n"
        f"[dim]{__tagline__}[/dim]\n\n"
        f"[link={get_avatar_url()}]View Avatar[/link]",
        title="🗡️ Raxodus Release Info 🗡️",
        border_style="blue"
    ))
    ctx.exit()


@click.group()
@click.option(
    "--version",
    is_flag=True,
    callback=version_callback,
    expose_value=False,
    is_eager=True,
    help="Show version and release information"
)
@click.pass_context
def cli(ctx):
    """raxodus - Escape from Rackspace ticket hell.

    Set credentials via environment variables:

        export RACKSPACE_USERNAME="your-username"
        export RACKSPACE_API_KEY="your-api-key"
        export RACKSPACE_ACCOUNT="123456"
    """
    ctx.ensure_object(dict)


@cli.group()
def auth():
    """Authentication commands."""
    pass


@auth.command()
def test():
    """Test authentication credentials."""
    try:
        with RackspaceClient() as client:
            token = client.authenticate()
            console.print("[green]✓[/green] Authentication successful!")
            console.print(f"  User ID: {token.user_id}")
            console.print(f"  Token expires: {token.expires_at}")
            if token.accounts:
                console.print(f"  Accounts: {', '.join(token.accounts)}")
    except AuthenticationError as e:
        console.print(f"[red]✗[/red] Authentication failed: {e}")
        sys.exit(1)
    except RaxodusError as e:
        console.print(f"[red]✗[/red] Error: {e}")
        sys.exit(1)


@cli.group()
def tickets():
    """Ticket management commands."""
    pass


@tickets.command("list")
@click.option("--account", help="Rackspace account number")
@click.option("--status", help="Filter by status (open, closed, pending)")
@click.option("--days", type=int, help="Show tickets from last N days")
@click.option("--page", type=int, default=1, help="Page number")
@click.option("--per-page", type=int, default=100, help="Results per page")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table", "csv"]),
    default="json",
    help="Output format",
)
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Include timing metadata in JSON output",
)
def list_tickets(account, status, days, page, per_page, output_format, debug):
    """List support tickets."""
    try:
        with RackspaceClient() as client:
            result = client.list_tickets(
                account=account,
                status=status,
                days=days,
                page=page,
                per_page=per_page,
            )

            if output_format == "json":
                click.echo(format_json(result.to_summary(include_metadata=debug)))
            elif output_format == "table":
                if debug and result.elapsed_seconds:
                    console.print(
                        f"[dim]API Response: {result.elapsed_seconds}s | "
                        f"From Cache: {result.from_cache}[/dim]"
                    )
                click.echo(format_table(result))
            elif output_format == "csv":
                click.echo(format_csv(result))

    except RaxodusError as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)


@tickets.command("get")
@click.argument("ticket_id")
@click.option("--account", help="Rackspace account number")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table"]),
    default="json",
    help="Output format",
)
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Include timing metadata in output",
)
def get_ticket(ticket_id, account, output_format, debug):
    """Get a specific ticket."""
    try:
        with RackspaceClient() as client:
            ticket = client.get_ticket(ticket_id, account=account)

            if output_format == "json":
                click.echo(format_json(ticket.to_dict_with_metadata(include_metadata=debug)))
            elif output_format == "table":
                # Create detailed table
                table = Table(title=f"Ticket {ticket.id}")
                table.add_column("Field", style="cyan")
                table.add_column("Value")

                table.add_row("ID", ticket.id)
                table.add_row("Subject", ticket.subject)
                table.add_row("Status", ticket.status)
                table.add_row("Severity", ticket.severity or "N/A")
                table.add_row("Created", ticket.created_at.isoformat())
                table.add_row("Updated", ticket.updated_at.isoformat())
                table.add_row("Requester", ticket.requester or "N/A")
                table.add_row("Assigned To", ticket.assigned_to or "N/A")

                console.print(table)

    except RaxodusError as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)


@cli.group()
def completion():
    """Manage shell completions for raxodus."""
    pass


@completion.command()
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish", "auto"]),
    default="auto",
    help="Shell to install completion for"
)
def install(shell):
    """Install shell completion for raxodus."""

    if shell == "auto":
        shell = detect_shell()
        console.print(f"Detected shell: [cyan]{shell}[/cyan]")

    try:
        success, message = install_completion(shell)

        if success:
            console.print(f"[green]✅ {message}[/green]")
            console.print("[yellow]Please restart your shell or run:[/yellow]")

            if shell == "bash":
                console.print("  source ~/.bashrc")
            elif shell == "zsh":
                console.print("  source ~/.zshrc")
            elif shell == "fish":
                console.print("  source ~/.config/fish/config.fish")
        else:
            console.print(f"[yellow]{message}[/yellow]")

    except Exception as e:
        console.print(f"[red]Error installing completion:[/red] {e}", file=sys.stderr)
        sys.exit(1)


@completion.command()
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish"]),
    required=True,
    help="Shell to generate completion for"
)
def show(shell):
    """Show shell completion script for raxodus."""

    try:
        if shell in COMPLETION_SCRIPTS:
            console.print(COMPLETION_SCRIPTS[shell])
        else:
            console.print(f"[red]Error:[/red] Shell '{shell}' not supported", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
