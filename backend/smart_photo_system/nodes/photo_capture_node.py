import os
import uuid
from datetime import datetime
from typing import Optional
import asyncio
import requests
from .base import BaseNode
from ..models.state import PhotoSystemState


class PhotoCaptureNode(BaseNode):
    """Photo capture node"""
    
    def __init__(self, capture_api_endpoint: str = None, output_dir: str = "/tmp/smart_photo_output"):
        super().__init__("PhotoCaptureNode")
        self.capture_api_endpoint = capture_api_endpoint or "http://localhost:8080/iphone-capture"
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    async def execute(self, state: PhotoSystemState) -> PhotoSystemState:
        """Trigger photo capture"""
        self._log("Starting photo capture")
        
        try:
            # Trigger iPhone photo capture
            photo_path = await self._capture_photo()
            
            if photo_path:
                self._log(f"Photo capture successful: {photo_path}")
                
                # Update state
                updated_state = self._update_state(
                    state,
                    captured_photo=photo_path,
                    current_step="completed"
                )
                
                return updated_state
            else:
                raise Exception("Photo capture failed, no photo received")
                
        except Exception as e:
            self._log(f"Photo capture failed: {str(e)}", "ERROR")
            return self._update_state(
                state,
                error_message=f"Photo capture failed: {str(e)}",
                current_step="capture"
            )
    
    async def _capture_photo(self) -> Optional[str]:
        """Execute photo capture operation"""
        self._log("Triggering iPhone photo capture...")
        
        try:
            # Method 1: Trigger capture via HTTP API
            photo_path = await self._try_http_capture()
            if photo_path:
                return photo_path
            
            # Method 2: Trigger capture via iOS Shortcuts
            photo_path = await self._try_shortcuts_capture()
            if photo_path:
                return photo_path
            
            # Method 3: Simulate capture (for development testing)
            return await self._simulate_capture()
            
        except Exception as e:
            self._log(f"Photo capture execution failed: {str(e)}", "ERROR")
            return None
    
    async def _try_http_capture(self) -> Optional[str]:
        """Trigger capture via HTTP API"""
        try:
            payload = {
                "action": "capture_photo",
                "timestamp": datetime.now().isoformat()
            }
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    self.capture_api_endpoint,
                    json=payload,
                    timeout=30  # Photo capture may take longer
                )
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("photo_url"):
                    # Download photo to local
                    return await self._download_photo(result["photo_url"])
            
        except Exception as e:
            self._log(f"HTTP capture API failed: {str(e)}", "DEBUG")
        
        return None
    
    async def _try_shortcuts_capture(self) -> Optional[str]:
        """Trigger capture via iOS Shortcuts"""
        try:
            # Build Shortcuts capture URL
            shortcuts_url = "shortcuts://run-shortcut?name=SmartPhotoCapture"
            
            self._log(f"Trying to capture via Shortcuts: {shortcuts_url}")
            
            # Need actual Shortcuts integration here
            # Currently returns None indicating not implemented
            return None
            
        except Exception as e:
            self._log(f"Shortcuts capture failed: {str(e)}", "DEBUG")
        
        return None
    
    async def _simulate_capture(self) -> Optional[str]:
        """Simulate capture (for development testing)"""
        self._log("Using simulation capture mode")
        
        try:
            # Simulate capture delay
            await asyncio.sleep(2)
            
            # Generate a simulated photo filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captured_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            photo_path = os.path.join(self.output_dir, filename)
            
            # Create a simulated photo file (would be real photo in actual project)
            with open(photo_path, 'w') as f:
                f.write("# This is a simulated photo file\n")
                f.write(f"# Capture time: {datetime.now().isoformat()}\n")
                f.write("# In actual implementation, this should be real photo data\n")
            
            self._log(f"Simulation capture completed: {photo_path}")
            return photo_path
            
        except Exception as e:
            self._log(f"Simulation capture failed: {str(e)}", "ERROR")
            return None
    
    async def _download_photo(self, photo_url: str) -> Optional[str]:
        """Download photo from URL to local"""
        try:
            self._log(f"Downloading photo: {photo_url}")
            
            # Generate local filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captured_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            local_path = os.path.join(self.output_dir, filename)
            
            # Async download
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(photo_url, timeout=30)
            )
            
            if response.status_code == 200:
                # Save photo
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                self._log(f"Photo download successful: {local_path}")
                return local_path
            else:
                self._log(f"Photo download failed, status code: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self._log(f"Photo download failed: {str(e)}", "ERROR")
            return None
    
    async def get_photo_info(self, photo_path: str) -> dict:
        """Get captured photo information"""
        try:
            if not os.path.exists(photo_path):
                return {"error": "Photo file does not exist"}
            
            # Get basic file information
            stat = os.stat(photo_path)
            file_info = {
                "file_path": photo_path,
                "file_size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
            # If it's a real photo file, can add EXIF info extraction
            # try:
            #     from PIL import Image
            #     from PIL.ExifTags import TAGS
            #     
            #     with Image.open(photo_path) as img:
            #         exif = img.getexif()
            #         exif_info = {}
            #         for tag_id, value in exif.items():
            #             tag = TAGS.get(tag_id, tag_id)
            #             exif_info[tag] = value
            #         file_info["exif"] = exif_info
            # except Exception as e:
            #     file_info["exif_error"] = str(e)
            
            return file_info
            
        except Exception as e:
            return {"error": f"Failed to get photo information: {str(e)}"}
    
    def cleanup_photos(self, keep_latest: int = 10):
        """Clean up old photo files"""
        try:
            if not os.path.exists(self.output_dir):
                return
            
            # Get all photo files
            photo_files = []
            for filename in os.listdir(self.output_dir):
                if filename.startswith("captured_"):
                    file_path = os.path.join(self.output_dir, filename)
                    if os.path.isfile(file_path):
                        photo_files.append((file_path, os.path.getctime(file_path)))
            
            # Sort by creation time, keep latest photos
            photo_files.sort(key=lambda x: x[1], reverse=True)
            
            if len(photo_files) > keep_latest:
                for file_path, _ in photo_files[keep_latest:]:
                    try:
                        os.remove(file_path)
                        self._log(f"Deleted old photo: {file_path}")
                    except Exception as e:
                        self._log(f"Failed to delete file {file_path}: {str(e)}", "WARNING")
                        
        except Exception as e:
            self._log(f"Failed to clean up photos: {str(e)}", "ERROR")
