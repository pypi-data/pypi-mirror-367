"""Data models for Arq backup entities."""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class NodeType(Enum):
    """Types of nodes in the backup tree."""

    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"


class CompressionType(Enum):
    """Compression types supported by Arq."""

    NONE = 0
    LZ4 = 1


class EncryptionVersion(Enum):
    """Encryption versions supported by Arq."""

    NONE = 0
    V1 = 1
    V2 = 2
    V3 = 3  # Current version using AES/CBC


@dataclass
class BackupConfig:
    """Backup configuration from backupconfig.json."""

    backup_set_uuid: str
    computer_uuid: str
    encryption_version: EncryptionVersion
    created_time: datetime
    s3_bucket: str | None = None
    s3_path: str | None = None
    aws_region: str = "us-east-1"


@dataclass
class BackupFolder:
    """Represents a backup folder configuration."""

    uuid: str
    local_path: Path
    exclude_paths: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    created_time: datetime = field(default_factory=datetime.now)
    modified_time: datetime = field(default_factory=datetime.now)


@dataclass
class Node:
    """Represents a file or directory in the backup."""

    type: NodeType
    name: str
    mode: int  # Unix file permissions
    uid: int  # User ID
    gid: int  # Group ID
    mtime: datetime  # Modification time
    size: int | None = None  # File size (None for directories)
    data_sha256: str | None = None  # SHA256 of file data
    data_blob_keys: list[str] | None = None  # For multi-part files
    tree_sha256: str | None = None  # For directories
    target_path: str | None = None  # For symlinks
    xattrs: dict[str, bytes] | None = None  # Extended attributes

    @property
    def is_file(self) -> bool:
        """Check if node is a file."""
        return self.type == NodeType.FILE

    @property
    def is_directory(self) -> bool:
        """Check if node is a directory."""
        return self.type == NodeType.DIRECTORY

    @property
    def is_symlink(self) -> bool:
        """Check if node is a symlink."""
        return self.type == NodeType.SYMLINK


@dataclass
class Tree:
    """Container for nodes with metadata."""

    version: int  # Tree format version (e.g., 22)
    sha256: str  # SHA256 of this tree
    nodes: list[Node]
    compressed: bool = True
    compression_type: CompressionType = CompressionType.LZ4
    encrypted: bool = False
    encryption_key_sha256: str | None = None

    def find_node(self, name: str) -> Node | None:
        """Find a node by name in this tree."""
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def get_directories(self) -> list[Node]:
        """Get all directory nodes."""
        return [n for n in self.nodes if n.is_directory]

    def get_files(self) -> list[Node]:
        """Get all file nodes."""
        return [n for n in self.nodes if n.is_file]


@dataclass
class Blob:
    """Represents a chunk of file data."""

    sha256: str
    size: int
    compressed: bool = True
    compression_type: CompressionType = CompressionType.LZ4
    encrypted: bool = False
    encryption_key_sha256: str | None = None
    data: bytes | None = None  # Actual data when loaded

    @property
    def key(self) -> str:
        """Get the storage key for this blob."""
        return self.sha256


@dataclass
class BlobPack:
    """Container for multiple blobs stored together."""

    sha256: str
    blobs: list[Blob]
    index: dict[str, int]  # Maps blob SHA256 to offset in pack


@dataclass
class TreePack:
    """Container for multiple trees stored together."""

    sha256: str
    trees: list[Tree]
    index: dict[str, int]  # Maps tree SHA256 to offset in pack


@dataclass
class BackupRecord:
    """Represents a single backup snapshot."""

    uuid: str
    backup_folder_uuid: str
    computer_uuid: str
    created_time: datetime
    completed_time: datetime | None
    root_tree_sha256: str
    total_size: int
    total_files: int
    total_directories: int
    is_complete: bool = True
    error_message: str | None = None


@dataclass
class CacheManifest:
    """Metadata about cached backup data."""

    backup_set_path: str
    cached_at: datetime
    last_updated: datetime
    backup_config: BackupConfig
    cached_backup_folders: list[str]  # UUIDs
    tree_count: int
    total_nodes: int
    cache_size_bytes: int
    version: int = 1
    computer_names: dict[str, str] = field(default_factory=dict)  # UUID -> friendly name


@dataclass
class RestoreOptions:
    """Options for restore operations."""

    preserve_permissions: bool = True
    preserve_timestamps: bool = True
    preserve_ownership: bool = False  # Requires root
    preserve_xattrs: bool = True
    overwrite_existing: bool = False
    verify_checksums: bool = True
    progress_callback: Callable[[int, int], None] | None = None
