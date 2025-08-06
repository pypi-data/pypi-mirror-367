"""AWS credential management with read-only enforcement."""

import os
from dataclasses import dataclass
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from arq_alight.core.exceptions import AWSCredentialsError, AuthenticationError


@dataclass
class AWSCredentials:
    """AWS credentials for S3 access."""
    
    access_key_id: str
    secret_access_key: str
    session_token: Optional[str] = None
    region: str = "us-east-1"


class CredentialProvider:
    """Manages AWS credentials from multiple sources with read-only enforcement."""

    REQUIRED_PERMISSIONS = [
        "s3:ListBucket",
        "s3:GetObject", 
        "s3:GetObjectVersion",
        "s3:GetBucketLocation",
    ]
    
    FORBIDDEN_PERMISSIONS = [
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:PutBucketPolicy",
        "s3:DeleteBucket",
    ]

    def __init__(self):
        """Initialize credential provider."""
        pass

    def get_credentials(
        self,
        cli_access_key: Optional[str] = None,
        cli_secret_key: Optional[str] = None,
        cli_session_token: Optional[str] = None,
        cli_region: Optional[str] = None,
    ) -> AWSCredentials:
        """Get AWS credentials from various sources.
        
        Priority order:
        1. CLI arguments
        2. Environment variables
        3. AWS credentials file (~/.aws/credentials)
        
        Args:
            cli_access_key: Access key from CLI
            cli_secret_key: Secret key from CLI
            cli_session_token: Session token from CLI
            cli_region: AWS region from CLI
            
        Returns:
            AWSCredentials object
            
        Raises:
            AWSCredentialsError: If no valid credentials found
        """
        # Try CLI arguments first
        if cli_access_key and cli_secret_key:
            return AWSCredentials(
                access_key_id=cli_access_key,
                secret_access_key=cli_secret_key,
                session_token=cli_session_token,
                region=cli_region or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            )
        
        # Try environment variables
        if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
            return AWSCredentials(
                access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                session_token=os.environ.get("AWS_SESSION_TOKEN"),
                region=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            )
        
        # Try boto3 default credential chain
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials:
                return AWSCredentials(
                    access_key_id=credentials.access_key,
                    secret_access_key=credentials.secret_key,
                    session_token=credentials.token,
                    region=session.region_name or "us-east-1"
                )
        except Exception:
            pass
        
        raise AWSCredentialsError(
            "No AWS credentials found. Please provide credentials via:\n"
            "  - Command line arguments (--aws-access-key-id, --aws-secret-access-key)\n"
            "  - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)\n"
            "  - AWS credentials file (~/.aws/credentials)"
        )

    def verify_read_only_access(self, credentials: AWSCredentials, bucket: str) -> None:
        """Verify credentials have only read access to the bucket.
        
        Args:
            credentials: AWS credentials to verify
            bucket: S3 bucket name
            
        Raises:
            AuthenticationError: If verification fails or write access detected
        """
        s3 = boto3.client(
            's3',
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=credentials.region
        )
        
        # First, verify we have basic read access
        try:
            s3.head_bucket(Bucket=bucket)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '403':
                raise AuthenticationError(f"Access denied to bucket '{bucket}'")
            elif error_code == '404':
                raise AuthenticationError(f"Bucket '{bucket}' not found")
            else:
                raise AuthenticationError(f"Failed to access bucket '{bucket}': {e}")
        
        # Check if we can list objects (basic read permission)
        try:
            s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                raise AuthenticationError(
                    f"No read access to bucket '{bucket}'. "
                    "Please ensure your credentials have s3:ListBucket permission."
                )
            raise

    def create_read_only_session(self, credentials: AWSCredentials) -> boto3.Session:
        """Create a boto3 session with the provided credentials.
        
        Args:
            credentials: AWS credentials
            
        Returns:
            Configured boto3 Session
        """
        return boto3.Session(
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
            region_name=credentials.region
        )