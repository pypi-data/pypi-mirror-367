"""Command-line interface for Arq Alight."""

import argparse
import os
import sys
from urllib.parse import urlparse

from rich.console import Console
from rich.table import Table

from . import __version__
from .config.manager import ConfigManager
from .core.exceptions import ArqAlightError
from .utils.security import obfuscate_key, validate_destination_path

console = Console()


def parse_s3_url(url: str) -> tuple[str, str]:
    """Parse S3 URL into bucket and prefix.

    Args:
        url: S3 URL like s3://bucket/path/to/backup

    Returns:
        Tuple of (bucket, prefix)

    Raises:
        ValueError: If URL is not a valid S3 URL
    """
    if not url.startswith("s3://"):
        raise ValueError(f"Invalid S3 URL: {url}. Must start with s3://")

    parsed = urlparse(url)
    bucket = parsed.netloc
    prefix = parsed.path.lstrip("/")

    if not bucket:
        raise ValueError(f"Invalid S3 URL: {url}. No bucket specified")

    return bucket, prefix


def cmd_configure(args: argparse.Namespace) -> int:
    """Handle configure command."""
    console.print("[yellow]Command 'configure' not yet implemented[/yellow]")
    if args.keychain:
        console.print("  Would store credentials in macOS keychain")
    return 0


def cmd_list_backups(args: argparse.Namespace) -> int:
    """Handle list-backups command."""
    try:
        bucket, prefix = parse_s3_url(args.backup_path)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1

    console.print(f"[cyan]Listing backups in:[/cyan] s3://{bucket}/{prefix}")

    # Check for AWS credentials
    if args.aws_access_key_id:
        obfuscated = obfuscate_key(args.aws_access_key_id)
        console.print(f"[dim]Using AWS Access Key ID:[/dim] {obfuscated}")
    elif os.environ.get("AWS_ACCESS_KEY_ID"):
        console.print("[dim]Using AWS credentials from environment variables[/dim]")
    else:
        console.print("[dim]Using AWS credentials from default chain[/dim]")

    # TODO: Implement actual S3 listing
    console.print("\n[yellow]Actual S3 listing not yet implemented[/yellow]")
    console.print("\nExample output:")

    # Create example table
    table = Table(title="Computers with Backups")
    table.add_column("Computer", style="cyan")
    table.add_column("UUID", style="dim")
    table.add_column("Last Backup", style="green")
    table.add_column("Total Size")

    # Get computer names from config
    config = ConfigManager()
    computer_names = config.list_computer_names()

    # Example data
    table.add_row(
        computer_names.get("123e4567-e89b-12d3-a456-426614174000", "MacBook Pro"),
        "123e4567-e89b-12d3-a456-426614174000",
        "2025-08-05 10:30:00",
        "125.3 GB",
    )
    table.add_row(
        computer_names.get("987f6543-a21b-34c5-d678-123456789012", "iMac Office"),
        "987f6543-a21b-34c5-d678-123456789012",
        "2025-08-04 22:15:00",
        "89.7 GB",
    )

    console.print(table)
    return 0


def cmd_cache_metadata(args: argparse.Namespace) -> int:
    """Handle cache-metadata command."""
    if args.info:
        console.print("[yellow]Cache info not yet implemented[/yellow]")
        return 0

    try:
        bucket, prefix = parse_s3_url(args.backup_path)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1

    console.print("[yellow]Command 'cache-metadata' not yet implemented[/yellow]")
    console.print(f"  Would cache metadata from: s3://{bucket}/{prefix}")

    if args.update:
        console.print("  [cyan]Update mode:[/cyan] would only fetch changed trees")
    if args.backup_folder_id:
        console.print(f"  [cyan]Specific folder:[/cyan] {args.backup_folder_id}")

    return 0


def cmd_ls(args: argparse.Namespace) -> int:
    """Handle ls command."""
    try:
        bucket, prefix = parse_s3_url(args.backup_path)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1

    console.print("[yellow]Command 'ls' not yet implemented[/yellow]")
    console.print(f"  Would list files in backup {args.backup_id}")
    console.print(f"  Path: {args.path}")
    console.print(f"  From: s3://{bucket}/{prefix}")
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    """Handle find command."""
    try:
        bucket, prefix = parse_s3_url(args.backup_path)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1

    console.print("[yellow]Command 'find' not yet implemented[/yellow]")
    console.print(f"  Would search for: '{args.name}'")
    console.print(f"  In backup: {args.backup_id}")
    if args.type:
        console.print(f"  Type filter: {args.type}")
    console.print(f"  From: s3://{bucket}/{prefix}")
    return 0


def cmd_restore_file(args: argparse.Namespace) -> int:
    """Handle restore-file command."""
    try:
        bucket, prefix = parse_s3_url(args.backup_path)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1

    try:
        dest_path = validate_destination_path(args.dest)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1

    console.print("[yellow]Command 'restore-file' not yet implemented[/yellow]")
    console.print(f"  Would restore: {args.file}")
    console.print(f"  To: {dest_path}")
    console.print(f"  From backup: {args.backup_id}")
    console.print(f"  In: s3://{bucket}/{prefix}")
    return 0


def cmd_restore_dir(args: argparse.Namespace) -> int:
    """Handle restore-dir command."""
    try:
        bucket, prefix = parse_s3_url(args.backup_path)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1

    try:
        dest_path = validate_destination_path(args.dest)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1

    console.print("[yellow]Command 'restore-dir' not yet implemented[/yellow]")
    console.print(f"  Would restore: {args.dir}")
    console.print(f"  To: {dest_path}")
    console.print(f"  From backup: {args.backup_id}")
    console.print(f"  Recursive: {args.recursive}")
    console.print(f"  In: s3://{bucket}/{prefix}")
    return 0


def cmd_set_computer_name(args: argparse.Namespace) -> int:
    """Handle set-computer-name command."""
    config = ConfigManager()
    config.set_computer_name(args.uuid, args.name)
    console.print(f"[green]✓[/green] Set computer name: {args.uuid} → '{args.name}'")
    return 0


def cmd_list_computer_names(args: argparse.Namespace) -> int:
    """Handle list-computer-names command."""
    config = ConfigManager()
    names = config.list_computer_names()

    if not names:
        console.print("[dim]No computer names configured[/dim]")
        return 0

    table = Table(title="Computer Name Mappings")
    table.add_column("UUID", style="cyan")
    table.add_column("Friendly Name", style="green")

    for uuid, name in sorted(names.items()):
        table.add_row(uuid, name)

    console.print(table)
    return 0


def cmd_remove_computer_name(args: argparse.Namespace) -> int:
    """Handle remove-computer-name command."""
    config = ConfigManager()
    config.remove_computer_name(args.uuid)
    console.print(f"[green]✓[/green] Removed computer name for: {args.uuid}")
    return 0


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="arq-alight",
        description="Lightweight Arq backup browser and restore tool for macOS",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Configure command
    config_parser = subparsers.add_parser(
        "configure",
        help="Configure AWS credentials",
    )
    config_parser.add_argument(
        "--keychain",
        action="store_true",
        help="Store credentials in macOS keychain",
    )

    # List backups command
    list_parser = subparsers.add_parser(
        "list-backups",
        help="List available backups",
    )
    list_parser.add_argument(
        "backup_path",
        type=str,
        help="S3 path to backup (e.g., s3://bucket/path)",
    )

    # Cache metadata command
    cache_parser = subparsers.add_parser(
        "cache-metadata",
        help="Cache backup metadata locally for fast searches",
    )
    cache_parser.add_argument(
        "backup_path",
        type=str,
        help="S3 path to backup (e.g., s3://bucket/path)",
    )
    cache_parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing cache (only fetch changed trees)",
    )
    cache_parser.add_argument(
        "--backup-folder-id",
        type=str,
        help="Cache specific backup folder by UUID",
    )
    cache_parser.add_argument(
        "--info",
        action="store_true",
        help="Show cache information",
    )

    # List files command
    ls_parser = subparsers.add_parser(
        "ls",
        help="List files in a backup",
    )
    ls_parser.add_argument(
        "backup_path",
        type=str,
        help="S3 path to backup (e.g., s3://bucket/path)",
    )
    ls_parser.add_argument(
        "--backup-id",
        type=str,
        required=True,
        help="Backup ID to list files from",
    )
    ls_parser.add_argument(
        "--path",
        type=str,
        default="/",
        help="Path within backup to list (default: /)",
    )

    # Find command
    find_parser = subparsers.add_parser(
        "find",
        help="Find files by name pattern",
    )
    find_parser.add_argument(
        "backup_path",
        type=str,
        help="S3 path to backup (e.g., s3://bucket/path)",
    )
    find_parser.add_argument(
        "--backup-id",
        type=str,
        required=True,
        help="Backup ID to search in",
    )
    find_parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name pattern to search for (supports wildcards)",
    )
    find_parser.add_argument(
        "--type",
        choices=["file", "directory"],
        help="Filter by node type",
    )

    # Restore file command
    restore_file_parser = subparsers.add_parser(
        "restore-file",
        help="Restore a single file",
    )
    restore_file_parser.add_argument(
        "backup_path",
        type=str,
        help="S3 path to backup (e.g., s3://bucket/path)",
    )
    restore_file_parser.add_argument(
        "--backup-id",
        type=str,
        required=True,
        help="Backup ID to restore from",
    )
    restore_file_parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="File path to restore",
    )
    restore_file_parser.add_argument(
        "--dest",
        type=str,
        required=True,
        help="Destination directory",
    )

    # Restore directory command
    restore_dir_parser = subparsers.add_parser(
        "restore-dir",
        help="Restore a directory",
    )
    restore_dir_parser.add_argument(
        "backup_path",
        type=str,
        help="S3 path to backup (e.g., s3://bucket/path)",
    )
    restore_dir_parser.add_argument(
        "--backup-id",
        type=str,
        required=True,
        help="Backup ID to restore from",
    )
    restore_dir_parser.add_argument(
        "--dir",
        type=str,
        required=True,
        help="Directory path to restore",
    )
    restore_dir_parser.add_argument(
        "--dest",
        type=str,
        required=True,
        help="Destination directory",
    )
    restore_dir_parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Restore recursively (default: True)",
    )

    # Set computer name command
    set_name_parser = subparsers.add_parser(
        "set-computer-name",
        help="Set a friendly name for a computer UUID",
    )
    set_name_parser.add_argument(
        "uuid",
        type=str,
        help="Computer UUID",
    )
    set_name_parser.add_argument(
        "name",
        type=str,
        help="Friendly name to assign",
    )

    # List computer names command
    subparsers.add_parser(
        "list-computer-names",
        help="List all computer name mappings",
    )

    # Remove computer name command
    remove_name_parser = subparsers.add_parser(
        "remove-computer-name",
        help="Remove a computer name mapping",
    )
    remove_name_parser.add_argument(
        "uuid",
        type=str,
        help="Computer UUID",
    )

    # Add AWS credential options to parser
    parser.add_argument(
        "--aws-access-key-id",
        type=str,
        help="AWS Access Key ID",
    )
    parser.add_argument(
        "--aws-secret-access-key",
        type=str,
        help="AWS Secret Access Key",
    )
    parser.add_argument(
        "--aws-session-token",
        type=str,
        help="AWS Session Token (for temporary credentials)",
    )

    # Add global options
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )

    args = parser.parse_args()

    # Handle no-color option
    if args.no_color:
        console._force_terminal = False

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Command dispatch
    commands = {
        "configure": cmd_configure,
        "list-backups": cmd_list_backups,
        "cache-metadata": cmd_cache_metadata,
        "ls": cmd_ls,
        "find": cmd_find,
        "restore-file": cmd_restore_file,
        "restore-dir": cmd_restore_dir,
        "set-computer-name": cmd_set_computer_name,
        "list-computer-names": cmd_list_computer_names,
        "remove-computer-name": cmd_remove_computer_name,
    }

    try:
        handler = commands.get(args.command)
        if handler:
            exit_code = handler(args)
            sys.exit(exit_code)
        else:
            console.print(f"[red]Unknown command:[/red] {args.command}")
            sys.exit(1)
    except ArqAlightError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        sys.exit(130)
    except Exception as e:
        if args.verbose:
            console.print_exception()
        else:
            console.print(f"[red]Unexpected error:[/red] {e}")
            console.print("[dim]Run with -v for full traceback[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
