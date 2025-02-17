"""
py-stream-zip

A stream-based ZIP file extractor in Python, inspired by node-stream-zip.

Credits:
    This package is inspired by node-stream-zip.
"""

from .stream_zip import StreamZip
from .zip_entry import ZipEntry
from .central_directory import (
    CentralDirectoryHeader,
    CentralDirectoryLoc64Header,
    CentralDirectoryZip64Header,
)
from .utils import read_uint32_le, read_uint64_le, parse_zip_time

__all__ = [
    "StreamZip",
    "ZipEntry",
    "CentralDirectoryHeader",
    "CentralDirectoryLoc64Header",
    "CentralDirectoryZip64Header",
]
