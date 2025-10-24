# YouTube Downloader (ytdlp)

Simple Python scripts for downloading YouTube videos and audio using yt-dlp.

## 📁 What's Included

### 🎵 **ytdlp_service.py** - Simple MP3 & Video Download Service (NEW)
A clean Python class for downloading YouTube videos as MP3 files or high-quality videos.

**Features:**
- ✅ Simple Python class - no Flask, no Docker, no complexity
- ✅ Download MP3 audio with quality selection
- ✅ Download videos in MP4/MKV format with best quality
- ✅ Download single or multiple videos
- ✅ Get video information before downloading
- ✅ Quality selection (best/1080p/720p/480p)
- ✅ Embedded metadata and thumbnails
- ✅ Easy to integrate into your own projects

**Usage:**
```python
from ytdlp_service import YouTubeMP3Downloader

# Create downloader
downloader = YouTubeMP3Downloader(download_dir="downloads")

# Download MP3
mp3_result = downloader.download_mp3(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    quality="best"
)

# Download video in MP4 format (best quality)
video_result = downloader.download_video(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    format_preference="mp4",  # or "mkv" or "any"
    quality="best"            # or "1080p", "720p", "480p"
)

# Download video in MKV format
mkv_result = downloader.download_video(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    format_preference="mkv",
    quality="1080p"
)

# Get video info first
info = downloader.get_video_info(url)
print(f"Title: {info['title']}")
print(f"Duration: {info['duration']}s")

# Download multiple videos
urls = ["url1", "url2", "url3"]
mp3_results = downloader.download_multiple(urls, quality="best")
video_results = downloader.download_multiple_videos(urls, format_preference="mp4", quality="1080p")
```

---

### 📜 Legacy Scripts (Batch Processing)
Original Python scripts for batch downloading from `links.txt`:

- **`mp3.py`** - Download audio as MP3
- **`video.py`** - Download videos up to 1080p
- **`best_video.py`** - Download best quality video with metadata
- **`videobest.py`** - Download best quality video (simple version)

**Usage:**
1. Add YouTube URLs to `links.txt` (one per line)
2. Run the desired script: `python mp3.py`
3. Check `downloads/` folder for files
4. Review `download_log.txt` for results

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- FFmpeg (required for audio conversion)
- yt-dlp

### Setup

1. **Install yt-dlp:**
```bash
pip install yt-dlp
```

2. **Install FFmpeg:**
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `sudo apt-get install ffmpeg`

---

## 📖 Quick Start

### Using the New Service (Recommended)

```bash
# Run the example
python ytdlp_service.py
```

Or use it in your own code:

```python
from ytdlp_service import YouTubeMP3Downloader

downloader = YouTubeMP3Downloader()

# Single download
result = downloader.download_mp3("https://www.youtube.com/watch?v=VIDEO_ID")

if result['status'] == 'success':
    print(f"Downloaded: {result['file_path']}")
else:
    print(f"Error: {result['error']}")
```

### Using Legacy Scripts

```bash
# Add URLs to links.txt
echo "https://www.youtube.com/watch?v=VIDEO_ID" > links.txt

# Run the script
python mp3.py
```

---

## 📂 Project Structure

```
ytdlp/
├── ytdlp_service.py        # NEW: Simple MP3 download service
├── mp3.py                  # Legacy: MP3 batch downloader
├── video.py                # Legacy: Video downloader
├── best_video.py           # Legacy: Best quality video
├── videobest.py            # Legacy: Simple best video
├── links.txt               # Input URLs for legacy scripts
├── download_log.txt        # Download logs
├── instructions.txt        # yt-dlp command examples
└── downloads/              # Downloaded files
    └── mp3/                # MP3 downloads
```

---

## 📝 License

This project is provided as-is for educational and personal use.

---

## ⚠️ Disclaimer

This tool is for downloading content you have the right to download. Please respect copyright laws and YouTube's Terms of Service.
