"""
Simple YouTube to MP3 Download Service
Core logic for downloading MP3 files from YouTube URLs
"""

import subprocess
import os
import shutil
from datetime import datetime
import zipfile
import tempfile
from urllib.parse import urlparse, parse_qs


class YouTubeMP3Downloader:
    """
    Simple service to download YouTube videos as MP3 files or videos in various formats.
    
    Features:
    - Download MP3 audio with quality selection
    - Download videos in MP4/MKV/any format
    - Quality selection (best, 1080p, 720p, 480p)
    - Batch downloads
    - Video information retrieval
    - Embedded metadata and thumbnails
    """
    
    def __init__(self, download_dir="downloads/mp3"):
        """
        Initialize the downloader.
        
        Args:
            download_dir (str): Directory where MP3 files will be saved
        """
        self.download_dir = download_dir
        self._ensure_download_dir()
    
    def _ensure_download_dir(self):
        """Create download directory if it doesn't exist."""
        os.makedirs(self.download_dir, exist_ok=True)
    
    def download_mp3(self, url, quality="best", output_filename=None):
        """
        Download a YouTube video as MP3.
        
        Args:
            url (str): YouTube video URL
            quality (str): Audio quality - "best" (0), "good" (5), or "worst" (9)
            output_filename (str): Optional custom filename (without extension)
        
        Returns:
            dict: Result with status, file_path, and error (if any)
        """
        try:
            # Map quality to yt-dlp audio quality values
            quality_map = {
                "best": "0",
                "good": "5", 
                "worst": "9"
            }
            audio_quality = quality_map.get(quality, "0")
            
            # Build output template
            if output_filename:
                output_template = os.path.join(self.download_dir, f"{output_filename}.%(ext)s")
            else:
                output_template = os.path.join(self.download_dir, "%(title)s.%(ext)s")
            
            # Build yt-dlp command
            command = [
                'yt-dlp',
                '-x',                           # Extract audio
                '--audio-format', 'mp3',        # Convert to MP3
                '--audio-quality', audio_quality,
                '--embed-thumbnail',            # Embed thumbnail as cover art
                '--add-metadata',               # Add metadata (title, artist, etc.)
                '--no-playlist',                # Download single video only
                '-o', output_template,          # Output template
                url
            ]
            
            print(f"🎵 Starting download from: {url}")
            print(f"📁 Saving to: {self.download_dir}")
            print(f"🎚️  Quality: {quality}")
            
            # Execute download
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                # Find the downloaded file
                files = [f for f in os.listdir(self.download_dir) 
                        if f.endswith('.mp3')]
                
                if files:
                    # Get the most recently created file
                    latest_file = max(
                        [os.path.join(self.download_dir, f) for f in files],
                        key=os.path.getctime
                    )
                    file_size = os.path.getsize(latest_file)
                    
                    print(f"✅ Download completed!")
                    print(f"📄 File: {os.path.basename(latest_file)}")
                    print(f"💾 Size: {file_size / 1024 / 1024:.2f} MB")
                    
                    return {
                        'status': 'success',
                        'file_path': latest_file,
                        'file_name': os.path.basename(latest_file),
                        'file_size': file_size,
                        'error': None
                    }
                else:
                    raise Exception("Downloaded file not found")
            else:
                raise Exception(f"yt-dlp error: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            error_msg = "Download timeout (exceeded 10 minutes)"
            print(f"❌ {error_msg}")
            return {
                'status': 'failed',
                'file_path': None,
                'error': error_msg
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Download failed: {error_msg}")
            return {
                'status': 'failed',
                'file_path': None,
                'error': error_msg
            }
    
    def get_video_info(self, url):
        """
        Get video information without downloading.
        
        Args:
            url (str): YouTube video URL
        
        Returns:
            dict: Video information or None if failed
        """
        try:
            command = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
                url
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                video_info = {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'thumbnail': info.get('thumbnail', ''),
                    'video_id': info.get('id', ''),
                    'description': info.get('description', '')
                }
                
                print(f"📋 Video Info:")
                print(f"   Title: {video_info['title']}")
                print(f"   Uploader: {video_info['uploader']}")
                print(f"   Duration: {video_info['duration']}s")
                
                return video_info
            else:
                print(f"❌ Failed to get video info: {result.stderr}")
                return None
        
        except Exception as e:
            print(f"❌ Error getting video info: {str(e)}")
            return None
    
    def download_multiple(self, urls, quality="best"):
        """
        Download multiple YouTube videos as MP3.
        
        Args:
            urls (list): List of YouTube video URLs
            quality (str): Audio quality for all downloads
        
        Returns:
            list: List of results for each download
        """
        results = []
        total = len(urls)
        
        print(f"\n{'='*60}")
        print(f"Starting batch download of {total} videos")
        print(f"{'='*60}\n")
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{total}] Processing: {url}")
            result = self.download_mp3(url, quality)
            results.append({
                'url': url,
                'result': result
            })
        
        # Summary
        successful = sum(1 for r in results if r['result']['status'] == 'success')
        failed = total - successful
        
        print(f"\n{'='*60}")
        print(f"Batch Download Complete!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"{'='*60}\n")
        
        return results

    def download_video(self, url, format_preference="mp4", quality="best", output_filename=None):
        """
        Download a YouTube video in best quality.
        
        Args:
            url (str): YouTube video URL
            format_preference (str): Preferred format - "mp4", "mkv", or "any"
            quality (str): Quality preference - "best", "1080p", "720p", "480p"
            output_filename (str): Optional custom filename (without extension)
        
        Returns:
            dict: Result with status, file_path, and error (if any)
        """
        try:
            # Build output template
            if output_filename:
                output_template = os.path.join(self.download_dir, f"{output_filename}.%(ext)s")
            else:
                output_template = os.path.join(self.download_dir, "%(title)s.%(ext)s")
            
            # Build format selector based on preferences
            if format_preference == "mp4":
                if quality == "best":
                    format_selector = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b"
                else:
                    height = quality.replace('p', '') if quality != "best" else "9999"
                    format_selector = f"bv*[ext=mp4][height<={height}]+ba[ext=m4a]/b[ext=mp4][height<={height}]/bv*[height<={height}]+ba/b[height<={height}]"
            elif format_preference == "mkv":
                if quality == "best":
                    format_selector = "bv*+ba/b"  # Best video + best audio (usually results in mkv)
                else:
                    height = quality.replace('p', '') if quality != "best" else "9999"
                    format_selector = f"bv*[height<={height}]+ba/b[height<={height}]"
            else:  # any format
                if quality == "best":
                    format_selector = "bv*+ba/b"
                else:
                    height = quality.replace('p', '') if quality != "best" else "9999"
                    format_selector = f"bv*[height<={height}]+ba/b[height<={height}]"
            
            # Build yt-dlp command
            command = [
                'yt-dlp',
                '-f', format_selector,          # Format selection
                '--merge-output-format', format_preference if format_preference != "any" else "mp4",
                '--embed-subs',                 # Embed subtitles if available
                '--write-auto-subs',            # Download auto-generated subs
                '--embed-thumbnail',            # Embed thumbnail
                '--add-metadata',               # Add metadata
                '--no-playlist',                # Download single video only
                '--ignore-errors',              # Continue on download errors
                '-o', output_template,          # Output template
                url
            ]
            
            # Add FFmpeg location if available
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path:
                command.extend(['--ffmpeg-location', os.path.dirname(ffmpeg_path)])
            
            print(f"🎬 Starting video download from: {url}")
            print(f"📁 Saving to: {self.download_dir}")
            print(f"🎚️  Quality: {quality}")
            print(f"📦 Format preference: {format_preference}")
            
            # Execute download
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=1200  # 20 minutes timeout for videos
            )
            
            if result.returncode == 0:
                # Find the downloaded file (look for video extensions)
                video_extensions = ['.mp4', '.mkv', '.webm', '.avi', '.mov']
                files = [f for f in os.listdir(self.download_dir) 
                        if any(f.lower().endswith(ext) for ext in video_extensions)]
                
                if files:
                    # Get the most recently created file
                    latest_file = max(
                        [os.path.join(self.download_dir, f) for f in files],
                        key=os.path.getctime
                    )
                    file_size = os.path.getsize(latest_file)
                    
                    print(f"✅ Video download completed!")
                    print(f"📄 File: {os.path.basename(latest_file)}")
                    print(f"💾 Size: {file_size / 1024 / 1024:.2f} MB")
                    
                    return {
                        'status': 'success',
                        'file_path': latest_file,
                        'file_name': os.path.basename(latest_file),
                        'file_size': file_size,
                        'error': None
                    }
                else:
                    raise Exception("Downloaded video file not found")
            else:
                # Better error handling
                error_output = result.stderr.strip()
                if "ffmpeg not found" in error_output.lower():
                    raise Exception("FFmpeg not found. Please install FFmpeg for video processing.")
                elif "signature extraction failed" in error_output.lower():
                    raise Exception("YouTube signature extraction failed. Try updating yt-dlp: pip install --upgrade yt-dlp")
                else:
                    raise Exception(f"yt-dlp error: {error_output}")
        
        except subprocess.TimeoutExpired:
            error_msg = "Video download timeout (exceeded 20 minutes)"
            print(f"❌ {error_msg}")
            return {
                'status': 'failed',
                'file_path': None,
                'error': error_msg
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Video download failed: {error_msg}")
            
            # Provide helpful suggestions
            if "ffmpeg" in error_msg.lower():
                print("\n💡 Solution: Install FFmpeg")
                print("   Windows: Download from https://ffmpeg.org/download.html")
                print("   macOS: brew install ffmpeg")
                print("   Linux: sudo apt-get install ffmpeg")
            elif "signature extraction" in error_msg.lower():
                print("\n💡 Solution: Update yt-dlp")
                print("   Run: pip install --upgrade yt-dlp")
            
            return {
                'status': 'failed',
                'file_path': None,
                'error': error_msg
            }

    def download_multiple_videos(self, urls, format_preference="mp4", quality="best"):
        """
        Download multiple YouTube videos.
        
        Args:
            urls (list): List of YouTube video URLs
            format_preference (str): Preferred format - "mp4", "mkv", or "any"
            quality (str): Quality preference for all downloads
        
        Returns:
            list: List of results for each download
        """
        results = []
        total = len(urls)
        
        print(f"\n{'='*60}")
        print(f"Starting batch video download of {total} videos")
        print(f"Format: {format_preference} | Quality: {quality}")
        print(f"{'='*60}\n")
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{total}] Processing: {url}")
            result = self.download_video(url, format_preference, quality)
            results.append({
                'url': url,
                'result': result
            })
        
        # Summary
        successful = sum(1 for r in results if r['result']['status'] == 'success')
        failed = total - successful
        
        print(f"\n{'='*60}")
        print(f"Batch Video Download Complete!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"{'='*60}\n")
        
        return results

    def is_playlist_url(self, url):
        """Check if URL is a playlist"""
        return 'playlist' in url or 'list=' in url

    def get_playlist_info(self, url):
        """Get playlist information"""
        try:
            command = [
                'yt-dlp',
                '--dump-json',
                '--flat-playlist',
                url
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                import json
                lines = result.stdout.strip().split('\n')
                videos = []
                
                for line in lines:
                    if line:
                        video_info = json.loads(line)
                        videos.append({
                            'title': video_info.get('title', 'Unknown'),
                            'id': video_info.get('id', ''),
                            'url': f"https://www.youtube.com/watch?v={video_info.get('id', '')}"
                        })
                
                return {
                    'status': 'success',
                    'videos': videos,
                    'count': len(videos)
                }
            else:
                return {'status': 'failed', 'error': result.stderr}
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def download_playlist(self, url, download_type="mp3", quality="best", format_pref="mp4"):
        """Download entire playlist and create zip file"""
        try:
            # Get playlist info
            playlist_info = self.get_playlist_info(url)
            if playlist_info['status'] == 'failed':
                return {'status': 'failed', 'error': playlist_info['error']}
            
            videos = playlist_info['videos']
            if not videos:
                return {'status': 'failed', 'error': 'No videos found in playlist'}
            
            # Create temporary directory for this playlist
            temp_dir = tempfile.mkdtemp(prefix="playlist_")
            
            # Download all videos
            results = []
            successful_files = []
            
            for i, video in enumerate(videos):
                print(f"[{i+1}/{len(videos)}] Downloading: {video['title']}")
                
                if download_type == "mp3":
                    # Temporarily change download dir
                    original_dir = self.download_dir
                    self.download_dir = temp_dir
                    result = self.download_mp3(video['url'], quality)
                    self.download_dir = original_dir
                else:
                    original_dir = self.download_dir
                    self.download_dir = temp_dir
                    result = self.download_video(video['url'], format_pref, quality)
                    self.download_dir = original_dir
                
                results.append(result)
                if result['status'] == 'success':
                    successful_files.append(result['file_path'])
            
            # Create zip file if we have successful downloads
            if successful_files:
                zip_filename = f"playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                zip_path = os.path.join(self.download_dir, zip_filename)
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in successful_files:
                        if os.path.exists(file_path):
                            zipf.write(file_path, os.path.basename(file_path))
                
                # Clean up temporary files
                shutil.rmtree(temp_dir)
                
                zip_size = os.path.getsize(zip_path)
                
                return {
                    'status': 'success',
                    'file_path': zip_path,
                    'file_name': zip_filename,
                    'file_size': zip_size,
                    'total_videos': len(videos),
                    'successful_downloads': len(successful_files),
                    'failed_downloads': len(videos) - len(successful_files),
                    'error': None
                }
            else:
                # Clean up temp dir
                shutil.rmtree(temp_dir)
                return {'status': 'failed', 'error': 'No videos downloaded successfully'}
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}


# Example usage
if __name__ == "__main__":
    # Create downloader instance
    downloader = YouTubeMP3Downloader(download_dir="downloads/mp3")
    
    # Example 1: Download single video
    """print("\n" + "="*60)
    print("Example 1: Single Video Download")
    print("="*60)
    
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Get video info first (optionalp)
    info = downloader.get_video_info(url)
    
    # Download the video as MP3
    result = downloader.download_mp3(url, quality="best")
    
    if result['status'] == 'success':
        print(f"\n✅ Success! File saved at: {result['file_path']}")
    else:
        print(f"\n❌ Failed: {result['error']}")"""
    
    # Example 2: Download multiple videos
    # Uncomment to test batch download
    """
    print("\n" + "="*60)
    print("Example 2: Batch Download")
    print("="*60)
    
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=9bZkp7q19f0",
    ]
    
    results = downloader.download_multiple(urls, quality="best")
    
    # Print results
    for item in results:
        print(f"\nURL: {item['url']}")
        print(f"Status: {item['result']['status']}")
        if item['result']['status'] == 'success':
            print(f"File: {item['result']['file_name']}")
    """

    # Example 3: Download a video in best quality
    """print("\n" + "="*60)
    print("Example 3: Download Video in Best Quality")
    print("="*60)
    
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Download the video in best quality
    video_result = downloader.download_video(video_url, format_preference="mp4", quality="720p")
    
    if video_result['status'] == 'success':
        print(f"\n✅ Success! Video saved at: {video_result['file_path']}")
    else:
        print(f"\n❌ Failed: {video_result['error']}")"""
    
    # Example 4: Download multiple videos
    # Uncomment to test batch video download
    """
    print("\n" + "="*60)
    print("Example 4: Batch Video Download")
    print("="*60)
    
    video_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=9bZkp7q19f0",
    ]
    
    video_results = downloader.download_multiple_videos(video_urls, format_preference="mp4", quality="best")
    
    # Print results
    for item in video_results:
        print(f"\nURL: {item['url']}")
        print(f"Status: {item['result']['status']}")
        if item['result']['status'] == 'success':
            print(f"File: {item['result']['file_name']}")
    """



