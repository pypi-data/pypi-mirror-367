"""Read-only S3 client wrapper for safety."""

import boto3

from arq_alight.core.exceptions import StorageError


class ReadOnlyS3Client:
    """S3 client wrapper that only allows read operations."""

    # Whitelist of allowed read-only S3 operations
    ALLOWED_OPERATIONS = {
        "head_bucket",
        "head_object",
        "get_object",
        "get_object_acl",
        "get_object_attributes",
        "get_object_legal_hold",
        "get_object_lock_configuration",
        "get_object_retention",
        "get_object_tagging",
        "get_object_torrent",
        "list_buckets",
        "list_objects",
        "list_objects_v2",
        "list_object_versions",
        "get_bucket_location",
        "get_bucket_versioning",
        "get_bucket_tagging",
        "get_bucket_policy",
        "get_bucket_acl",
        "get_bucket_cors",
        "get_bucket_encryption",
        "get_bucket_lifecycle",
        "get_bucket_lifecycle_configuration",
        "get_bucket_logging",
        "get_bucket_notification",
        "get_bucket_notification_configuration",
        "get_bucket_replication",
        "get_bucket_request_payment",
        "get_bucket_website",
    }

    def __init__(self, s3_client):
        """Initialize with a boto3 S3 client.

        Args:
            s3_client: boto3 S3 client instance
        """
        self._client = s3_client
        self._wrap_client()

    def _wrap_client(self):
        """Wrap the S3 client to intercept and block write operations."""
        # Get all attributes from the original client
        for attr_name in dir(self._client):
            if attr_name.startswith("_"):
                continue

            attr = getattr(self._client, attr_name)

            # If it's a method and not in our whitelist, replace with error
            if callable(attr) and attr_name not in self.ALLOWED_OPERATIONS:
                setattr(self, attr_name, self._create_blocked_method(attr_name))
            else:
                # For allowed operations and non-callable attributes, pass through
                setattr(self, attr_name, attr)

    def _create_blocked_method(self, method_name: str):
        """Create a method that raises an error for blocked operations."""

        def blocked_method(*args, **kwargs):
            raise StorageError(
                f"Operation '{method_name}' is not allowed. "
                "Arq Alight is a read-only tool and cannot perform write operations."
            )

        return blocked_method

    def __getattr__(self, name):
        """Fallback for any attributes not explicitly set."""
        # First check if the underlying client has this attribute
        if not hasattr(self._client, name):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        attr = getattr(self._client, name)
        if callable(attr) and name not in self.ALLOWED_OPERATIONS:
            return self._create_blocked_method(name)
        return attr


def create_read_only_s3_client(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: str | None = None,
    region_name: str = "us-east-1",
    **kwargs,
) -> ReadOnlyS3Client:
    """Create a read-only S3 client.

    Args:
        aws_access_key_id: AWS access key
        aws_secret_access_key: AWS secret key
        aws_session_token: Optional session token
        region_name: AWS region
        **kwargs: Additional arguments for boto3.client

    Returns:
        ReadOnlyS3Client instance
    """
    # Create standard boto3 S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region_name,
        **kwargs,
    )

    # Wrap it in our read-only wrapper
    return ReadOnlyS3Client(s3_client)
