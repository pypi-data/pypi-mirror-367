# QuickDownload

A high-performance parallel file downloader that supports both HTTP/HTTPS downloads and BitTorrent downloads, with full support for resuming interrupted downloads.

## Features

- **Parallel Downloads**: Split HTTP files into multiple chunks and download them simultaneously
- **BitTorrent Support**: Download from magnet links, .torrent files, and .torrent URLs
- **Resume Support**: Automatically resume interrupted downloads from where they left off
- **Progress Tracking**: Persistent progress tracking survives network failures and interruptions
- **Configurable Parallelism**: Control the number of parallel download threads (HTTP only)
- **Custom Output**: Specify custom output file names and locations
- **Command Line Interface**: Simple and intuitive CLI for both HTTP and torrent downloads
- **High Performance**: Significantly faster downloads for large files
- **Automatic Retry**: Failed chunks are automatically retried with exponential backoff
- **Seeding Support**: Optional seeding for torrent downloads to contribute back to the network

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/QuickDownload.git
cd QuickDownload

# Install the package (includes libtorrent for torrent support)
pip install -e .
```

Note: For torrent support, libtorrent is required. If installation fails, try:
```bash
# On macOS with Homebrew
brew install libtorrent-rasterbar

# On Ubuntu/Debian
sudo apt-get install python3-libtorrent

# Then install QuickDownload
pip install -e .
```

## Usage

### HTTP/HTTPS Downloads

Basic usage:
```bash
quickdownload https://example.com/largefile.zip
```

With custom output filename:
```bash
quickdownload -o myfile.zip https://example.com/largefile.zip
```

With custom parallelism:
```bash
quickdownload -p 8 https://example.com/largefile.zip
```

### Torrent Downloads

Download from magnet link:
```bash
quickdownload "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
```

Download from .torrent file:
```bash
quickdownload ~/Downloads/ubuntu.torrent
```

Download from .torrent URL:
```bash
quickdownload https://example.com/ubuntu.torrent
```

Download to specific directory:
```bash
quickdownload -o ~/Downloads "magnet:?xt=urn:btih:..."
```

Download with seeding:
```bash
quickdownload --seed-time 60 "magnet:?xt=urn:btih:..."
```

### Command Line Options

| Option | Short | Description | Default | Applies To |
|--------|-------|-------------|---------|------------|
| `--output` | `-o` | Custom output filename/directory | Current directory | Both |
| `--parallel` | `-p` | Number of parallel download threads | 4 | HTTP only |
| `--seed-time` | `` | Time to seed after torrent download (minutes) | 0 | Torrent only |
| `--help` | `-h` | Show help message | - | Both |

### HTTP Download Examples

Download a large file with maximum parallelism:
```bash
quickdownload -p 16 https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso
```

Download to a specific directory:
```bash
quickdownload -o ~/Downloads/ubuntu.iso https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso
```

### Torrent Download Examples

Download Linux distribution:
```bash
# Using magnet link
quickdownload "magnet:?xt=urn:btih:a26f24611b7db8c524c6e96b7e25000b9e2ad705"

# Using .torrent file
quickdownload ~/Downloads/ubuntu-22.04.3-desktop-amd64.iso.torrent

# Using .torrent URL
quickdownload https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso.torrent
```

Download to specific directory with seeding:
```bash
quickdownload -o ~/Downloads --seed-time 30 "magnet:?xt=urn:btih:..."
```

### Resume Examples

If a download is interrupted, simply run the same command to resume:

```bash
# Start download
quickdownload -p 8 -o large_file.zip https://example.com/large_file.zip
# ... download gets interrupted (Ctrl+C, network failure, etc.) ...

# Resume download - same command!
quickdownload -p 8 -o large_file.zip https://example.com/large_file.zip
# Output: "📁 Found existing download progress - checking chunks..."
# Output: "🔄 Resuming previous download..."
```

### Real-World Usage Scenarios

**Scenario 1: Large Software Download**
```bash
# Download a large ISO file with 8 parallel connections
quickdownload -p 8 -o ubuntu-22.04.iso \
  https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso

# If interrupted, resume with the same command
# Only missing chunks will be downloaded
```

**Scenario 2: Unreliable Network**
```bash
# Start download on unreliable connection
quickdownload -p 4 -o dataset.zip https://data.example.com/large-dataset.zip

# Network fails halfway through - no problem!
# Later, run the same command to continue:
quickdownload -p 4 -o dataset.zip https://data.example.com/large-dataset.zip
# Progress is automatically resumed from where it left off
```

**Scenario 3: Batch Processing**
```bash
#!/bin/bash
# Download multiple files with resume support
files=(
  "file1.zip"
  "file2.tar.gz" 
  "file3.iso"
)

for file in "${files[@]}"; do
  echo "Downloading $file..."
  quickdownload -p 6 -o "$file" "https://downloads.example.com/$file"
  # Each file will resume if previously interrupted
done
```

## How It Works

1. **File Analysis**: QuickDownload first analyzes the target file to determine its size and whether the server supports range requests
2. **Resume Detection**: Checks for existing partial downloads and verifies chunk integrity
3. **Chunk Creation**: The file is divided into equal chunks based on the specified parallelism level
4. **Parallel Download**: Each chunk is downloaded simultaneously using separate threads
5. **Progress Tracking**: Download progress is continuously saved to enable resuming
6. **Assembly**: Downloaded chunks are assembled into the final file
7. **Cleanup**: Temporary files and progress data are removed upon successful completion

## Performance Benefits

- **Speed**: Downloads are typically 2-5x faster than single-threaded downloads
- **Reliability**: Failed chunks are automatically retried without affecting other chunks
- **Efficiency**: Network bandwidth is utilized more effectively
- **Resumability**: Large downloads can be resumed exactly where they left off
- **Fault Tolerance**: Individual chunk failures don't stop the entire download
- **Smart Recovery**: Corrupted chunks are automatically detected and re-downloaded
- **Zero Data Loss**: Progress tracking ensures no completed work is lost on interruption

### Performance Examples

```bash
# Traditional wget (single-threaded)
wget https://example.com/1GB-file.zip
# Time: ~10 minutes on 100Mbps connection

# QuickDownload (8 parallel threads)
quickdownload -p 8 https://example.com/1GB-file.zip  
# Time: ~3-4 minutes on same connection (2.5x faster)

# If interrupted at 60% completion:
# wget: starts over from 0%
# QuickDownload: resumes from 60% - saves 6+ minutes!
```

### Resume Implementation Details

QuickDownload implements resume functionality through:

1. **Progress Files**: Creates `.progress` files containing:
   - Original URL and parameters
   - File size and chunk information
   - List of completed chunk IDs
   - Timestamp for validation

2. **Chunk Verification**: On resume, verifies each "completed" chunk:
   - Checks file size matches expected chunk size
   - Re-downloads corrupted or missing chunks
   - Only downloads what's actually needed

3. **State Management**: 
   - Temporary `.part{N}` files for each chunk
   - Progress saved after each completed chunk
   - Automatic cleanup on successful completion

### Current Implementation Status

✅ **Fully Implemented:**
- Parallel downloading with configurable threads
- Complete resume functionality after interruptions
- Progress tracking that survives crashes
- Chunk integrity verification
- Automatic retry with exponential backoff
- Smart fallback for servers without range support
- Comprehensive error handling
- Progress visualization with real-time updates

✅ **Tested Scenarios:**
- Network interruptions (Ctrl+C)
- Computer crashes/restarts
- Corrupted chunk detection
- Invalid URLs and server errors
- Single-threaded fallback
- Multiple resume attempts

⚠️ **Current Limitations:**
- Resume only works when using same parameters (URL, output file, parallel count)
- Servers without HTTP range support fall back to single-threaded (no resume)
- Progress files are stored in the same directory as output file

### Supported Protocols

- HTTP/HTTPS
- Servers that support range requests (HTTP 206 Partial Content)
- Automatic fallback to single-threaded download for servers that don't support ranges

### Requirements

- Python 3.7+
- Network connection
- Sufficient disk space for the target file

## Error Handling

QuickDownload includes robust error handling for:
- Network timeouts and connection errors
- Disk space issues
- Invalid URLs
- Server errors (404, 500, etc.)
- Chunk download failures with automatic retry
- Corrupted chunk detection and recovery
- Interrupted downloads with full resume capability

## FAQ

**Q: How many parallel downloads should I use?**
A: The optimal number depends on your network connection and the server. Start with 4-8 parallel downloads. Too many can actually slow things down due to overhead.

**Q: Does this work with all websites?**
A: QuickDownload works with any server that supports HTTP range requests. If range requests aren't supported, it falls back to a single-threaded download.

**Q: Can I resume a download that was interrupted?**
A: Yes! QuickDownload automatically saves progress and can resume downloads exactly where they left off. Simply run the same command again, and it will detect and resume the previous download.

**Q: What happens if my computer crashes during a download?**
A: No problem! QuickDownload saves progress continuously. When you restart the download, it will verify existing chunks and only download what's missing or corrupted.

**Q: How does chunk verification work?**
A: Each chunk is verified for size and integrity before being considered complete. Corrupted chunks are automatically re-downloaded.

**Q: What files does QuickDownload create during download?**
A: During download, you'll see:
- `filename.part0`, `filename.part1`, etc. (temporary chunk files)
- `filename.progress` (progress tracking file)
These are automatically cleaned up on successful completion.

**Q: Can I change the number of parallel downloads for a resumed download?**
A: No, you must use the same parameters (URL, output filename, parallel count) to resume a download. If you change parameters, it will start fresh.

**Q: Does resume work with all servers?**
A: Resume only works with servers that support HTTP range requests. If a server doesn't support ranges, QuickDownload will fall back to single-threaded download (which can't be resumed).

**Q: How much faster is parallel downloading?**
A: Typically 2-5x faster than single-threaded downloads, depending on your network connection and the server's capabilities. The optimal number of threads varies by situation.

**Q: Is this safe to use?**
A: Yes, QuickDownload only downloads files and doesn't execute any code. However, always be cautious about what files you download from the internet.


### Troubleshooting

**Download stuck at "Analyzing file..."**: Server may be slow to respond. Check your internet connection.

**"Range requests supported: False"**: Server doesn't support parallel downloads. Will use single-threaded mode (still works, just slower).

**Resume not working**: Ensure you're using the exact same command (URL, output file, parallel count) as the original download.

**Chunks failing repeatedly**: May indicate server issues or network instability. Try reducing parallel count with `-p 2`.

---

Made with ❤️ for faster, more reliable downloads
