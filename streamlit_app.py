import streamlit as st
import os
import time
import threading
from datetime import datetime, timedelta
import json
from ytdlp_service import YouTubeMP3Downloader
from file_manager import FileManager
from ui_components import UIComponents

# Page config
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎵",
    layout="wide"
)

# Initialize session state
if 'downloads' not in st.session_state:
    st.session_state.downloads = {}
if 'file_manager' not in st.session_state:
    st.session_state.file_manager = FileManager(cleanup_minutes=20)

def main():
    st.title("🎵 YouTube Downloader")
    st.markdown("Download YouTube videos as MP3 or Video files")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📥 Download")
        
        # Download type selection
        download_type = UIComponents.download_type_selector()
        
        # Quality selection based on type
        quality = UIComponents.quality_selector(download_type)
        
        # URL input
        urls = UIComponents.url_input_component()
        
        # Download button
        if st.button("🚀 Start Download", disabled=not urls):
            start_download(urls, download_type, quality)
    
    with col2:
        st.header("📁 Available Files")
        display_available_files()

def start_download(urls, download_type, quality):
    """Start download process"""
    try:
        downloader = YouTubeMP3Downloader(download_dir="downloads")
        
        # Create progress placeholder
        progress_container = st.container()
        
        with progress_container:
            st.info(f"Starting download of {len(urls)} file(s)...")
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Determine download function and format
        if download_type == "MP3 Audio":
            if len(urls) == 1:
                result = downloader.download_mp3(urls[0], quality)
                results = [{'url': urls[0], 'result': result}]
            else:
                results = downloader.download_multiple(urls, quality)
        else:
            format_pref = "mp4" if download_type == "MP4 Video" else "mkv"
            if len(urls) == 1:
                result = downloader.download_video(urls[0], format_pref, quality)
                results = [{'url': urls[0], 'result': result}]
            else:
                results = downloader.download_multiple_videos(urls, format_pref, quality)
        
        # Process results
        successful = 0
        failed = 0
        
        for i, item in enumerate(results):
            progress_bar.progress((i + 1) / len(results))
            
            if item['result']['status'] == 'success':
                successful += 1
                # Register file for cleanup
                file_path = item['result']['file_path']
                st.session_state.file_manager.register_file(file_path)
                status_text.success(f"✅ Downloaded: {item['result']['file_name']}")
            else:
                failed += 1
                status_text.error(f"❌ Failed: {item['url']} - {item['result']['error']}")
        
        # Final status
        if successful > 0:
            st.success(f"✅ Download complete! {successful} successful, {failed} failed")
        else:
            st.error("❌ All downloads failed")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def display_available_files():
    """Display available files with download links only"""
    files = st.session_state.file_manager.get_available_files()
    
    if not files:
        st.info("No files available")
        return
    
    for file_info in files:
        file_name = file_info['name']
        file_path = file_info['path']
        file_size = file_info['size']
        time_left = file_info['time_left']
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.write(f"📄 **{file_name}**")
                st.caption(f"Size: {file_size:.1f} MB | Expires in: {time_left}")
            
            with col2:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label="⬇️",
                            data=f.read(),
                            file_name=file_name,
                            key=f"download_{file_name}"
                        )
        
        st.divider()

if __name__ == "__main__":
    main()

