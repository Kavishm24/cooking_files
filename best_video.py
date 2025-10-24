import subprocess
import os
from datetime import datetime
import shutil

def read_links(file_path):
    """Reads links from a given file."""
    with open(file_path, 'r') as file:
        links = file.readlines()
    return [link.strip() for link in links if link.strip()]

def run_command(link):
    """Runs yt-dlp command with optimized settings for best quality video download."""
    # Create downloads directory if it doesn't exist
    downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    
    command = [
        'yt-dlp',
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]',  # Best video and audio
        '--merge-output-format', 'mp4',
        '-o', os.path.join(downloads_dir, '%(title)s.%(ext)s'),  # Output path
        '--format-sort', 'res,fps,codec:h264,size,br,asr',
        '--concurrent-fragments', '4',
        '--retries', '3',
        '--embed-thumbnail',
        '--add-metadata',
        '--no-keep-video',  # Don't keep the video-only file
        '--no-keep-audio',  # Don't keep the audio-only file
        link
    ]
    try:
        print("🔄 Processing download...")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Clean up any leftover .part or .temp files
        for file in os.listdir(downloads_dir):
            if file.endswith(('.part', '.temp', '.f140', '.f137')):
                os.remove(os.path.join(downloads_dir, file))
                
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def log_results(link, output, error, log_file):
    """Logs the output and error of the command to a log file with timestamp."""
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"=== Download Attempt: {datetime.now()} ===\n")
        log.write(f"Link: {link}\n")
        log.write(f"Output: {output}\n")
        if error:
            log.write(f"Error: {error}\n")
        log.write("-" * 50 + "\n\n")

def main():
    input_file = 'links.txt'
    log_file = 'download_log.txt'
    downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

    # Create downloads directory if it doesn't exist
    os.makedirs(downloads_dir, exist_ok=True)

    if not os.path.exists(input_file):
        print(f"❌ The file {input_file} does not exist.")
        return

    open(log_file, 'w').close()
    links = read_links(input_file)
    
    print(f"📂 Downloads will be saved to: {downloads_dir}")
    
    for link in links:
        print(f"⏳ Downloading: {link}")
        output, error = run_command(link)

        if output:
            print("✅ Download successful!")
        if error:
            print(f"❌ Error: {error}")

        log_results(link, output, error, log_file)

    print("🎉 Download process complete!")

if __name__ == "__main__":
    main()