"""Security utilities for Arq Alight."""

from pathlib import Path


def obfuscate_key(key: str, visible_chars: int = 3) -> str:
    """Obfuscate a secret key showing only first and last few characters.

    Args:
        key: The key to obfuscate
        visible_chars: Number of characters to show at start and end

    Returns:
        Obfuscated string like "ABC*****XYZ"
    """
    if not key:
        return ""

    if len(key) <= (visible_chars * 2):
        # Key too short to meaningfully obfuscate
        return "*" * len(key)

    return f"{key[:visible_chars]}{'*' * (len(key) - visible_chars * 2)}{key[-visible_chars:]}"


def validate_destination_path(dest: Path | str) -> Path:
    """Validate that a destination path is safe for writing.

    Args:
        dest: Destination path to validate

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path is unsafe or invalid
    """
    # Convert to Path and resolve
    path = Path(dest).expanduser().resolve()

    # Define system directories that should never be written to
    forbidden_paths = [
        Path("/"),
        Path("/bin"),
        Path("/boot"),
        Path("/dev"),
        Path("/etc"),
        Path("/lib"),
        Path("/lib64"),
        Path("/proc"),
        Path("/root"),
        Path("/run"),
        Path("/sbin"),
        Path("/sys"),
        Path("/usr"),
        Path("/var"),
        # macOS specific
        Path("/System"),
        Path("/Library"),
        Path("/Applications"),
        Path("/private"),
    ]

    # Check if path is under any forbidden directory
    for forbidden in forbidden_paths:
        # Special case for root - only allow if path has more than one part
        if forbidden == Path("/"):
            # Root is forbidden only if we're trying to write directly to /
            if path == Path("/") or path.parent == Path("/"):
                raise ValueError(f"Cannot write to system directory: {path}\nPath is at root level")
            continue

        # Check if our path is inside the forbidden directory
        if path.is_relative_to(forbidden):
            raise ValueError(
                f"Cannot write to system directory: {path}\n"
                f"Path is under protected directory: {forbidden}"
            )

    # Ensure parent directory exists or can be created
    if not path.parent.exists():
        try:
            # Check if we can create parent directories
            path.parent.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise ValueError(f"Cannot create parent directory {path.parent}: {e}") from e

    # Check if path exists and is a directory when we expect a file
    if path.exists() and path.is_dir():
        raise ValueError(f"Destination exists and is a directory: {path}")

    return path
