"""
QuickDownload - High-performance parallel file downloader with torrent support

A command-line tool and Python library for downloading files with parallel connections
and resume capabilities. Supports both HTTP/HTTPS downloads and BitTorrent downloads.
"""

__version__ = "1.0.0"
__author__ = "Nikhil K Singh"
__email__ = "nsr.nikhilsingh@gmail.com"

from .utils import download_file
from .torrent_utils import download_torrent, is_torrent_url

__all__ = ["download_file", "download_torrent", "is_torrent_url"]
