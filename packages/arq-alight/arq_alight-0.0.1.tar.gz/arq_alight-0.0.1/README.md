# Arq Alight

A lightweight command-line tool for browsing and restoring backups created by [Arq Backup](https://www.arqbackup.com/) on macOS.

## Overview

Arq Alight provides a fast, efficient way to:

- Browse your Arq backups stored in Amazon S3 (and presumably compatible S3-compatible clones)
- Search for specific files across all your backups
- Restore individual files or specific directories
- Cache backup metadata locally for offline browsing

**Important**: Arq Alight is a read-only tool. It will never modify, write to, or delete your backups. Creating new backups or modifying existing backups is strictly out of scope for this project.

**Safety Feature**: The tool enforces read-only access at the client level by wrapping the AWS S3 client to block all write operations, providing an additional layer of protection against accidental modifications.

## Status

🚧 **This project is currently under active development and is not ready for public use.**

The tool is in early alpha stage with core functionality still being implemented.

## Disclaimer

**NO WARRANTY**: This software is provided "as is" without warranty of any kind, either expressed or implied. Use at your own risk. While the developer has taken precautions to ensure this tool operates in read-only mode and cannot harm existing data, no guarantees are made.

**RECOMMENDED FOR SOFTWARE PROFESSIONALS ONLY**: This tool is intended for use by software professionals who understand the risks involved in data recovery operations and can verify the integrity of restored data.

## Features (Planned)

- Browse backups without the full Arq application
- Fast local caching of backup metadata
- Search files by name or pattern
- Selective file and directory restoration
- Support for Arq's encryption and compression
- Friendly computer name mapping for easier identification

## Requirements

- macOS (Apple Silicon or Intel)
- Python 3.11 or later
- AWS credentials for S3 access
- Backups created with Arq 7

## License

MIT License - see LICENSE file for details.
