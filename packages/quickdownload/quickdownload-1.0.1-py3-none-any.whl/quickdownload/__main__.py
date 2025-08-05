"""
Summary:
    Downloads a file from a URL with optional output file name and parallel downloads.
    Supports both HTTP/HTTPS downloads and BitTorrent downloads via magnet links or .torrent files.

Keyword arguments:
    url -- The URL of the file to download, magnet link, or .torrent file
    output -- The output file name or directory (default: None)
    parallel -- Number of parallel downloads for HTTP (default: 4)
    seed_time -- Time to seed after torrent download in minutes (default: 0)

Return: None
Path: __main__.py
Author: Nikhil K Singh
Date: 2025-08-03

"""

import argparse


from quickdownload.utils import download_file
from quickdownload.torrent_utils import download_torrent, is_torrent_url


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="QuickDownload - High-performance parallel file downloader with torrent support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  HTTP/HTTPS Downloads:
    quickdownload https://example.com/file.zip
    quickdownload -o custom.zip https://example.com/file.zip
    quickdownload -p 8 https://example.com/largefile.zip
  
  Torrent Downloads:
    quickdownload "magnet:?xt=urn:btih:1234567890abcdef..."
    quickdownload -o /downloads file.torrent
    quickdownload --seed-time 60 https://example.com/file.torrent
        """,
    )

    # Add arguments to the parser
    parser.add_argument(
        "url", help="The URL of the file to download, magnet link, or .torrent file"
    )
    parser.add_argument("-o", "--output", help="The output file name or directory")
    parser.add_argument(
        "-p",
        "--parallel",
        type=int,
        default=4,
        help="Number of parallel downloads (HTTP only)",
    )
    parser.add_argument(
        "--seed-time",
        type=int,
        default=0,
        help="Time to seed after download (minutes, torrent only)",
    )
    args = parser.parse_args()

    # Check if this is a torrent download
    if is_torrent_url(args.url):
        download_torrent(args.url, args.output, args.seed_time)
    else:
        download_file(args.url, args.output, args.parallel)


if __name__ == "__main__":
    main()
