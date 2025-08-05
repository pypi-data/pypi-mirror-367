import os
import sys
import time
import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Global progress tracking for multi-chunk downloads
chunk_progress = {}
progress_lock = threading.Lock()


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
                print("Resuming previous download...")
            _download_parallel(url, output, file_size, parallel, existing_progress)

        # Clean up progress tracking on successful completion
        _cleanup_progress(output)
        print(f"\nDownload completed: {output}")
        print(f"File successfully saved to: {os.path.abspath(output)}")

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
    """Download file using single thread with resume support."""
    max_retries = 5

    for attempt in range(max_retries):
        try:
            # Check if partial file exists
            start_byte = 0
            if os.path.exists(output):
                start_byte = os.path.getsize(output)
                print(f"Resuming download from byte {start_byte}")

            # Create request with range header if resuming
            req = urllib.request.Request(url)
            if start_byte > 0:
                req.add_header("Range", f"bytes={start_byte}-")

            # Add timeout to prevent hanging
            with urllib.request.urlopen(req, timeout=30) as response:
                # Get total size (accounting for partial downloads)
                if start_byte > 0:
                    content_range = response.headers.get("Content-Range", "")
                    if content_range:
                        total_size = int(content_range.split("/")[1])
                    else:
                        total_size = start_byte + int(
                            response.headers.get("Content-Length", 0)
                        )
                else:
                    total_size = int(response.headers.get("Content-Length", 0))

                # Open in append mode if resuming, write mode if starting fresh
                mode = "ab" if start_byte > 0 else "wb"
                with open(output, mode) as f:
                    downloaded = start_byte

                    while True:
                        try:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)

                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                _show_progress(progress, downloaded, total_size)
                        except (ConnectionError, TimeoutError) as e:
                            print(f"\nConnection error: {str(e)}")
                            raise  # Will retry with current progress

                print()  # New line after progress
                return  # Success

        except (HTTPError, URLError, ConnectionError, TimeoutError, OSError) as e:
            if attempt == max_retries - 1:
                raise Exception(
                    f"Single-threaded download failed after {max_retries} attempts: {str(e)}"
                )

            delay = (2**attempt) + (attempt * 0.5)
            print(
                f"\nDownload failed (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f}s..."
            )
            time.sleep(delay)

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

            # Initialize chunk progress tracking
            global chunk_progress
            chunk_progress = {}

            # Initialize progress for completed chunks
            for chunk_id in completed_chunks:
                if chunk_id < len(chunks):
                    start, end, _ = chunks[chunk_id]
                    chunk_size = end - start + 1
                    _update_chunk_progress(chunk_id, chunk_size, chunk_size)

            # Reserve space for progress display
            print("\n" * (parallel + 3))  # Space for chunk bars + overall bar

            # Start progress display thread
            display_active = True

            def progress_updater():
                while display_active:
                    _display_multi_chunk_progress(parallel, file_size)
                    time.sleep(0.5)  # Update twice per second

            progress_thread = threading.Thread(target=progress_updater, daemon=True)
            progress_thread.start()

            # Download remaining chunks in parallel with retry logic
            max_chunk_retries = 3
            failed_chunks = []

            for retry_round in range(max_chunk_retries):
                if retry_round > 0:
                    print(
                        f"\nRetrying {len(failed_chunks)} failed chunks (attempt {retry_round + 1}/{max_chunk_retries})..."
                    )
                    remaining_chunks = failed_chunks
                    failed_chunks = []

                if not remaining_chunks:
                    break

                with ThreadPoolExecutor(
                    max_workers=min(parallel, len(remaining_chunks))
                ) as executor:
                    future_to_chunk = {
                        executor.submit(
                            _download_chunk,
                            url,
                            start,
                            end,
                            temp_files[chunk_id],
                            chunk_id,
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

                        except Exception as e:
                            # Add failed chunk to retry list instead of failing immediately
                            print(f"\nChunk {chunk_id} failed: {str(e)}")
                            failed_chunks.append((start, end, chunk_id))

                            # Save progress even on failure
                            _save_progress(
                                output, url, file_size, parallel, list(completed_chunks)
                            )

            # If we still have failed chunks after all retries, raise an error
            if failed_chunks:
                failed_chunk_ids = [chunk_id for _, _, chunk_id in failed_chunks]
                raise Exception(
                    f"Failed to download chunks {failed_chunk_ids} after {max_chunk_retries} attempts"
                )

            # Stop progress display
            display_active = False
            time.sleep(0.6)  # Wait for final update

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


def _download_chunk(url, start, end, temp_file, chunk_id=None):
    """Download a specific chunk of the file with progress reporting and resume capability."""
    max_retries = 5  # Increased retries for network issues
    chunk_size = end - start + 1

    # Check if partial chunk already exists
    downloaded_offset = 0
    if os.path.exists(temp_file):
        downloaded_offset = os.path.getsize(temp_file)
        # Don't resume if file is corrupted or larger than expected
        if downloaded_offset > chunk_size:
            downloaded_offset = 0
            try:
                os.remove(temp_file)
            except OSError:
                pass

    for attempt in range(max_retries):
        try:
            # Calculate actual range to download (resume from partial)
            actual_start = start + downloaded_offset

            # If chunk is already complete, return immediately
            if downloaded_offset >= chunk_size:
                return chunk_size

            req = urllib.request.Request(url)
            req.add_header("Range", f"bytes={actual_start}-{end}")

            # Add timeout to prevent hanging
            with urllib.request.urlopen(req, timeout=30) as response:
                # Open in append mode if resuming, write mode if starting fresh
                mode = "ab" if downloaded_offset > 0 else "wb"
                with open(temp_file, mode) as f:
                    downloaded_this_session = 0
                    while True:
                        try:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded_this_session += len(chunk)
                            total_downloaded = (
                                downloaded_offset + downloaded_this_session
                            )

                            # Update chunk progress if tracking is enabled
                            if chunk_id is not None:
                                _update_chunk_progress(
                                    chunk_id, total_downloaded, chunk_size
                                )

                        except (ConnectionError, TimeoutError) as e:
                            # Network error during chunk read - partial progress is saved
                            print(f"\nNetwork error in chunk {chunk_id}: {str(e)}")
                            downloaded_offset += downloaded_this_session
                            raise  # Will retry from new offset

                    return downloaded_offset + downloaded_this_session

        except (HTTPError, URLError, ConnectionError, TimeoutError, OSError) as e:
            if attempt == max_retries - 1:
                raise Exception(
                    f"Chunk {chunk_id} download failed after {max_retries} attempts: {str(e)}"
                )

            # Update offset for next retry attempt if we have a partial file
            if os.path.exists(temp_file):
                downloaded_offset = os.path.getsize(temp_file)

            # Exponential backoff with jitter for network errors
            delay = (2**attempt) + (attempt * 0.5)  # 1, 2.5, 5, 9.5, 16 seconds
            print(
                f"\nChunk {chunk_id} failed (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f}s..."
            )
            time.sleep(delay)

        except Exception as e:
            # Non-network errors - don't preserve partial downloads
            if attempt == max_retries - 1:
                raise Exception(
                    f"Chunk {chunk_id} download failed after {max_retries} attempts: {str(e)}"
                )
            time.sleep(1 * (attempt + 1))  # Basic backoff for other errors


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

    print("Initializing download...")
    bar_chars = ["░", "█"]
    for i in range(20):
        bar = "".join(bar_chars[1] if j <= i else bar_chars[0] for j in range(20))
        percentage = ((i + 1) / 20) * 100
        sys.stdout.write(f"\rPreparing: [{bar}] {percentage:.0f}%")
        sys.stdout.flush()
        time.sleep(0.05)
    print()  # New line after preview


def _show_progress(progress, downloaded, total):
    """Display download progress with speed and ETA."""
    bar_length = 50
    filled_length = int(bar_length * progress / 100)

    # Create a more visible progress bar with different characters
    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    downloaded_str = _format_size(downloaded)
    total_str = _format_size(total)

    # Initialize timing data if not present
    if not hasattr(_show_progress, "start_time"):
        _show_progress.start_time = time.time()
        _show_progress.last_time = time.time()
        _show_progress.last_downloaded = 0

    current_time = time.time()

    # Calculate speed and ETA
    speed_str = ""
    eta_str = ""

    # Calculate overall average speed
    total_time = current_time - _show_progress.start_time
    if total_time > 0:
        avg_speed = downloaded / total_time
        if avg_speed > 0:
            speed_str = f" | {_format_size(avg_speed)}/s"

            # Calculate ETA
            remaining_bytes = total - downloaded
            eta_seconds = remaining_bytes / avg_speed
            if eta_seconds < 60:
                eta_str = f" | ETA: {eta_seconds:.0f}s"
            elif eta_seconds < 3600:
                eta_str = f" | ETA: {eta_seconds/60:.0f}m {eta_seconds%60:.0f}s"
            else:
                hours = eta_seconds // 3600
                minutes = (eta_seconds % 3600) // 60
                eta_str = f" | ETA: {hours:.0f}h {minutes:.0f}m"

    # Enhanced progress display with speed and ETA
    progress_text = f"\r[{bar}] {progress:.1f}% ({downloaded_str}/{total_str}){speed_str}{eta_str}   "

    sys.stdout.write(progress_text)
    sys.stdout.flush()


def _format_size(bytes_size):
    """Format bytes into human readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def _update_chunk_progress(chunk_id, downloaded, total):
    """Update progress for a specific chunk."""
    with progress_lock:
        chunk_progress[chunk_id] = {
            "downloaded": downloaded,
            "total": total,
            "progress": (downloaded / total * 100) if total > 0 else 0,
        }


def _display_multi_chunk_progress(total_chunks, file_size):
    """Display progress bars for all chunks."""
    with progress_lock:
        # Clear the screen area for chunk progress
        sys.stdout.write(f"\r\033[{total_chunks + 2}A")  # Move cursor up

        # Calculate overall progress
        total_downloaded = 0
        overall_progress = 0

        for chunk_id in range(total_chunks):
            if chunk_id in chunk_progress:
                chunk_data = chunk_progress[chunk_id]
                downloaded = chunk_data["downloaded"]
                total = chunk_data["total"]
                progress = chunk_data["progress"]
                total_downloaded += downloaded

                # Create mini progress bar for this chunk
                bar_length = 20
                filled_length = int(bar_length * progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                status = "DONE" if progress >= 100 else "DOWN"
                print(
                    f"Chunk {chunk_id:2d}: {status} [{bar}] {progress:5.1f}% {_format_size(downloaded):>8}/{_format_size(total):<8}"
                )
            else:
                # Chunk not started yet
                bar = "░" * 20
                print(f"Chunk {chunk_id:2d}: WAIT [{bar}]   0.0%     0 B/    0 B    ")

        # Overall progress
        if file_size > 0:
            overall_progress = (total_downloaded / file_size) * 100

        print("─" * 70)
        overall_bar_length = 50
        overall_filled = int(overall_bar_length * overall_progress / 100)
        overall_bar = "█" * overall_filled + "░" * (overall_bar_length - overall_filled)

        print(
            f"Overall: [{overall_bar}] {overall_progress:.1f}% ({_format_size(total_downloaded)}/{_format_size(file_size)})"
        )

        sys.stdout.flush()
