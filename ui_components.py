import streamlit as st
from typing import List, Dict, Optional

class UIComponents:
    """Reusable UI components for the Streamlit app"""
    
    @staticmethod
    def download_type_selector() -> str:
        """Download type selection component"""
        return st.radio(
            "Choose download type:",
            ["MP3 Audio", "MP4 Video", "MKV Video"],
            horizontal=True,
            help="Select the format you want to download"
        )
    
    @staticmethod
    def quality_selector(download_type: str) -> str:
        """Quality selection component based on download type"""
        if download_type == "MP3 Audio":
            return st.selectbox(
                "Audio Quality:",
                ["best", "good", "worst"],
                help="Choose audio quality"
            )
        else:
            return st.selectbox(
                "Video Quality:",
                ["best", "1080p", "720p", "480p"],
                help="Choose video quality"
            )
    
    @staticmethod
    def url_input_component() -> List[str]:
        """URL input component with single/multiple options"""
        input_method = st.radio(
            "Input method:",
            ["Single URL", "Multiple URLs"],
            horizontal=True
        )
        
        if input_method == "Single URL":
            url = st.text_input(
                "YouTube URL:",
                placeholder="https://www.youtube.com/watch?v=..."
            )
            return [url] if url else []
        else:
            urls_text = st.text_area(
                "YouTube URLs (one per line):",
                height=100,
                placeholder="https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=..."
            )
            return [url.strip() for url in urls_text.split('\n') if url.strip()]
    
    @staticmethod
    def progress_display(current: int, total: int, message: str = ""):
        """Progress display component"""
        if total > 0:
            progress = current / total
            st.progress(progress)
            st.text(f"Progress: {current}/{total} ({progress*100:.1f}%)")
            
            if message:
                st.info(message)
        else:
            st.info("Preparing download...")
    
    @staticmethod
    def file_card(file_info: Dict) -> Optional[str]:
        """Display a file card with download option only"""
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
                if st.button("⬇️ Download", key=f"download_{file_name}"):
                    return "download"
        
        return None
    
    @staticmethod
    def status_message(message_type: str, message: str):
        """Display status messages"""
        if message_type == "success":
            st.success(message)
        elif message_type == "error":
            st.error(message)
        elif message_type == "warning":
            st.warning(message)
        elif message_type == "info":
            st.info(message)
    
    @staticmethod
    def download_status_display(status: str, current_file: str = ""):
        """Display download status with proper messaging"""
        if status == "idle":
            return
        elif status == "starting":
            st.info("🚀 Initializing download...")
        elif status == "downloading":
            st.info(f"⬇️ Downloading: {current_file}")
        elif status == "processing":
            st.info(f"⚙️ Processing: {current_file}")
        elif status == "completed":
            st.success("✅ Download completed!")
        elif status == "error":
            st.error("❌ Download failed!")
    
    @staticmethod
    def stats_display(total_files: int, total_size: float):
        """Display statistics"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Files", total_files)
        
        with col2:
            st.metric("Total Size", f"{total_size:.1f} MB")

