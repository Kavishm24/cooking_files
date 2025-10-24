import os
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict

class FileManager:
    """Manages downloaded files and automatic cleanup"""
    
    def __init__(self, cleanup_minutes=20):
        self.cleanup_minutes = cleanup_minutes
        self.registry_file = "file_registry.json"
        self.file_registry = self.load_registry()
    
    def load_registry(self) -> Dict:
        """Load file registry from disk"""
        try:
            if os.path.exists(self.registry_file):
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_registry(self):
        """Save file registry to disk"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.file_registry, f, indent=2)
        except Exception:
            pass
    
    def register_file(self, file_path: str):
        """Register a file for automatic cleanup"""
        if os.path.exists(file_path):
            self.file_registry[file_path] = {
                'created_at': datetime.now().isoformat(),
                'size': os.path.getsize(file_path)
            }
            self.save_registry()
    
    def get_available_files(self) -> List[Dict]:
        """Get list of available files with metadata"""
        files = []
        current_time = datetime.now()
        
        # Clean up expired files first
        self.cleanup_old_files()
        
        for file_path, metadata in self.file_registry.items():
            if os.path.exists(file_path):
                created_at = datetime.fromisoformat(metadata['created_at'])
                expires_at = created_at + timedelta(minutes=self.cleanup_minutes)
                time_left = expires_at - current_time
                
                if time_left.total_seconds() > 0:
                    files.append({
                        'name': os.path.basename(file_path),
                        'path': file_path,
                        'size': metadata['size'] / (1024 * 1024),  # MB
                        'created_at': created_at,
                        'expires_at': expires_at,
                        'time_left': self.format_time_left(time_left)
                    })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created_at'], reverse=True)
        return files
    
    def cleanup_old_files(self) -> int:
        """Remove files older than cleanup_minutes"""
        cleaned_count = 0
        current_time = datetime.now()
        files_to_remove = []
        
        for file_path, metadata in self.file_registry.items():
            created_at = datetime.fromisoformat(metadata['created_at'])
            age = current_time - created_at
            
            if age.total_seconds() > (self.cleanup_minutes * 60):
                # File is too old, remove it
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                    except Exception:
                        pass
                files_to_remove.append(file_path)
        
        # Remove from registry
        for file_path in files_to_remove:
            del self.file_registry[file_path]
        
        if files_to_remove:
            self.save_registry()
        
        return cleaned_count



    def format_time_left(self, time_delta: timedelta) -> str:
        """Format time remaining as human readable string"""
        total_seconds = int(time_delta.total_seconds())
        
        if total_seconds <= 0:
            return "Expired"
        
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_total_files(self) -> int:
        """Get total number of managed files"""
        return len([f for f in self.file_registry.keys() if os.path.exists(f)])
    
    def get_total_size(self) -> float:
        """Get total size of managed files in MB"""
        total_size = 0
        for file_path, metadata in self.file_registry.items():
            if os.path.exists(file_path):
                total_size += metadata['size']
        return total_size / (1024 * 1024)  # Convert to MB

