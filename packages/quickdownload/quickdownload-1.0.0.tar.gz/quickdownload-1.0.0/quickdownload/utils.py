import os
import sys
import time
import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor, as_completed


def _get_progress_file(output):
    """Get the progress tracking file path."""
    return f"{output}.progress"


def _save_progress(output, url, file_size, parallel, completed_chunks):
    """Save download progress to a file."""
    progress_data = {
        "url": url,
        "output": output,
        "file_size": file_size,
        "parallel": parallel,
        "completed_chunks": completed_chunks,
        "timestamp": time.time(),
    }
    progress_file = _get_progress_file(output)
    try:
        with open(progress_file, "w") as f:
            json.dump(progress_data, f)
    except Exception:
        pass  # Continue even if we can't save progress


def _load_progress(output):
    """Load download progress from a file."""
    progress_file = _get_progress_file(output)
    try:
        if os.path.exists(progress_file):
            with open(progress_file, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def _cleanup_progress(output):
    """Remove progress tracking file."""
    progress_file = _get_progress_file(output)
    try:
        if os.path.exists(progress_file):
            os.remove(progress_file)
    except OSError:
        pass


def _verify_chunk(temp_file, expected_size):
    """Verify if a chunk file is complete and valid."""
    try:
        if os.path.exists(temp_file):
            actual_size = os.path.getsize(temp_file)
            return actual_size == expected_size
    except OSError:
        pass
    return False


def download_file(url, output=None, parallel=4):
    """
    Downloads a file from the specified URL with optional output file name and parallel downloads.
    Supports resuming interrupted downloads.
    Args:
        url (str): The URL of the file to download.
        output (str, optional): The output file name. If None, the file will be saved with its original name.
        parallel (int, optional): Number of parallel downloads. Default is 4.
        Returns: None
    Raises:
        Exception: If the download fails or if there are issues with the URL.

    """
    try:
        print(f"Starting download from: {url}")
        print("Analyzing file... ", end="", flush=True)

        # Get file info and check if range requests are supported
        file_size, supports_ranges, filename = _get_file_info(url)
        print("✓")

        # Determine output filename
        if output is None:
            output = filename

        print(f"File size: {_format_size(file_size)}")
        print(f"Output file: {output}")
        print(f"Range requests supported: {supports_ranges}")

        # Check for existing progress
        existing_progress = _load_progress(output)
        resume_download = False

        if existing_progress:
            if (
                existing_progress.get("url") == url
                and existing_progress.get("file_size") == file_size
                and existing_progress.get("parallel") == parallel
            ):
                print("Found existing download progress - checking chunks...")
                resume_download = True
            else:
                print("Previous download had different parameters - starting fresh")
                _cleanup_progress(output)

        # Show a preview loading bar
        if file_size > 0:
            print(f"Preparing to download {_format_size(file_size)}...")
            _show_preview_bar()
        else:
            print("File size unknown, starting download...")

        if not supports_ranges or parallel == 1:
            print("\nUsing single-threaded download...")
            _download_single_threaded(url, output)
        else:
            print(f"\nUsing {parallel} parallel threads...")
            if resume_download:
                print(" Resuming previous download...")
            _download_parallel(url, output, file_size, parallel, existing_progress)

        # Clean up progress tracking on successful completion
        _cleanup_progress(output)
        print(f"\nDownload completed: {output}")

    except KeyboardInterrupt:
        print("\nDownload interrupted by user. Progress saved for resuming.")
        raise
    except Exception as e:
        print(f"\nDownload failed: {str(e)}")
        print("Progress saved - you can resume this download later.")
        raise


def _get_file_info(url):
    """Get file information including size and range support."""
    try:
        print(".", end="", flush=True)
        req = urllib.request.Request(url, method="HEAD")
        # Add timeout to prevent hanging
        with urllib.request.urlopen(req, timeout=30) as response:
            print(".", end="", flush=True)
            file_size = int(response.headers.get("Content-Length", 0))
            supports_ranges = response.headers.get("Accept-Ranges") == "bytes"

            # Extract filename from URL or Content-Disposition header
            filename = None
            content_disposition = response.headers.get("Content-Disposition", "")
            if "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')

            if not filename:
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path) or "downloaded_file"

            print(".", end="", flush=True)
            return file_size, supports_ranges, filename

    except HTTPError as e:
        if e.code == 405:  # Method Not Allowed, try GET request
            try:
                print(".", end="", flush=True)
                req = urllib.request.Request(url)
                req.add_header("Range", "bytes=0-0")
                # Add timeout to prevent hanging
                with urllib.request.urlopen(req, timeout=30) as response:
                    print(".", end="", flush=True)
                    content_range = response.headers.get("Content-Range", "")
                    if content_range:
                        file_size = int(content_range.split("/")[1])
                        supports_ranges = True
                    else:
                        file_size = 0
                        supports_ranges = False

                    parsed_url = urllib.parse.urlparse(url)
                    filename = os.path.basename(parsed_url.path) or "downloaded_file"

                    print(".", end="", flush=True)
                    return file_size, supports_ranges, filename
            except Exception as e:
                print(f" (fallback failed: {e})", end="", flush=True)
                pass
        raise Exception(f"Failed to get file info: HTTP {e.code}")
    except URLError as e:
        raise Exception(f"Failed to connect: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error getting file info: {str(e)}")


def _download_single_threaded(url, output):
    """Download file using single thread."""
    try:
        # Add timeout to prevent hanging
        with urllib.request.urlopen(url, timeout=30) as response:
            with open(output, "wb") as f:
                downloaded = 0
                total_size = int(response.headers.get("Content-Length", 0))

                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        _show_progress(progress, downloaded, total_size)

                print()  # New line after progress

    except Exception as e:
        raise Exception(f"Single-threaded download failed: {str(e)}")


def _download_parallel(url, output, file_size, parallel, existing_progress=None):
    """Download file using multiple parallel threads with resume support."""
    chunk_size = file_size // parallel
    chunks = []
    completed_chunks = set()

    # Create chunk ranges
    for i in range(parallel):
        start = i * chunk_size
        end = start + chunk_size - 1
        if i == parallel - 1:  # Last chunk gets remainder
            end = file_size - 1
        chunks.append((start, end, i))

    # Create temporary files for chunks
    temp_files = []
    for i in range(parallel):
        temp_file = f"{output}.part{i}"
        temp_files.append(temp_file)

    # Check existing progress and verify chunks
    if existing_progress:
        completed_chunks = set(existing_progress.get("completed_chunks", []))
        print(f"Verifying {len(completed_chunks)} completed chunks...")

        # Verify each supposedly completed chunk
        chunks_to_verify = list(completed_chunks)
        for chunk_id in chunks_to_verify:
            if chunk_id < len(chunks):
                start, end, _ = chunks[chunk_id]
                expected_size = end - start + 1
                temp_file = temp_files[chunk_id]

                if not _verify_chunk(temp_file, expected_size):
                    print(f"Chunk {chunk_id} corrupted, will re-download")
                    completed_chunks.discard(chunk_id)
                    try:
                        os.remove(temp_file)
                    except OSError:
                        pass

        if completed_chunks:
            print(f"{len(completed_chunks)} chunks verified and ready to resume")

    try:
        # Filter out completed chunks
        remaining_chunks = [
            (start, end, chunk_id)
            for start, end, chunk_id in chunks
            if chunk_id not in completed_chunks
        ]

        if not remaining_chunks:
            print("All chunks already completed!")
        else:
            print(f"Downloading {len(remaining_chunks)} remaining chunks...")

            # Download remaining chunks in parallel
            with ThreadPoolExecutor(
                max_workers=min(parallel, len(remaining_chunks))
            ) as executor:
                future_to_chunk = {
                    executor.submit(
                        _download_chunk, url, start, end, temp_files[chunk_id]
                    ): (start, end, chunk_id)
                    for start, end, chunk_id in remaining_chunks
                }

                total_downloaded = sum(
                    os.path.getsize(temp_files[i])
                    for i in completed_chunks
                    if os.path.exists(temp_files[i])
                )

                for future in as_completed(future_to_chunk):
                    start, end, chunk_id = future_to_chunk[future]
                    try:
                        bytes_downloaded = future.result()
                        completed_chunks.add(chunk_id)
                        total_downloaded += bytes_downloaded

                        # Save progress after each completed chunk
                        _save_progress(
                            output, url, file_size, parallel, list(completed_chunks)
                        )

                        progress = (total_downloaded / file_size) * 100
                        _show_progress(progress, total_downloaded, file_size)

                    except Exception as e:
                        # Save progress even on failure
                        _save_progress(
                            output, url, file_size, parallel, list(completed_chunks)
                        )
                        raise Exception(f"Chunk {chunk_id} failed: {str(e)}")

        print()  # New line after progress

        # Combine chunks into final file
        print("Combining chunks...")
        _combine_chunks(temp_files, output)

        # Clean up temporary files (but keep progress file until final cleanup)
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass

    except Exception:
        # Save progress on failure but keep temp files for resume
        _save_progress(output, url, file_size, parallel, list(completed_chunks))
        raise


def _download_chunk(url, start, end, temp_file):
    """Download a specific chunk of the file."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("Range", f"bytes={start}-{end}")

            # Add timeout to prevent hanging
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(temp_file, "wb") as f:
                    downloaded = 0
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                    return downloaded

        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(
                    f"Chunk download failed after {max_retries} attempts: {str(e)}"
                )
            time.sleep(1 * (attempt + 1))  # Exponential backoff


def _combine_chunks(temp_files, output):
    """Combine downloaded chunks into final file."""
    with open(output, "wb") as outfile:
        for temp_file in temp_files:
            with open(temp_file, "rb") as infile:
                while True:
                    chunk = infile.read(8192)
                    if not chunk:
                        break
                    outfile.write(chunk)


def _show_preview_bar():
    """Show a preview loading bar animation."""
    import time

    bar_chars = ["▱", "▰"]
    for i in range(10):
        bar = "".join(bar_chars[j % 2] if j <= i else bar_chars[0] for j in range(10))
        sys.stdout.write(f"\rPreparing: [{bar}]")
        sys.stdout.flush()
        time.sleep(0.1)
    print()  # New line after preview


def _show_progress(progress, downloaded, total):
    """Display download progress."""
    bar_length = 40
    filled_length = int(bar_length * progress / 100)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)

    downloaded_str = _format_size(downloaded)
    total_str = _format_size(total)

    sys.stdout.write(f"\r[{bar}] {progress:.1f}% ({downloaded_str}/{total_str})")
    sys.stdout.flush()


def _format_size(bytes_size):
    """Format bytes into human readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"
