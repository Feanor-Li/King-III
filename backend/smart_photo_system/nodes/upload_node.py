import os
import uuid
from typing import Optional
import aiofiles
from PIL import Image
from .base import BaseNode
from ..models.state import PhotoSystemState


class UploadNode(BaseNode):
    """Node for handling image uploads"""
    
    def __init__(self, upload_dir: str = "/tmp/smart_photo_uploads"):
        super().__init__("UploadNode")
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    async def execute(self, state: PhotoSystemState) -> PhotoSystemState:
        """Process image upload"""
        self._log("Starting image upload processing")
        
        try:
            # If photo_ref already exists, it means upload is complete
            if state.photo_ref and os.path.exists(state.photo_ref):
                self._log(f"Image already exists: {state.photo_ref}")
                return self._update_state(state, current_step="analyze")
            
            # Assumes image has been uploaded via API to temporary location
            # In actual implementation, would get from FastAPI file upload
            self._log("Waiting for image upload...")
            
            # Update state
            state.current_step = "analyze"
            return state
            
        except Exception as e:
            self._log(f"Upload failed: {str(e)}", "ERROR")
            return self._update_state(
                state,
                error_message=f"Image upload failed: {str(e)}",
                current_step="upload"
            )
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file"""
        # Generate unique filename
        file_ext = os.path.splitext(filename)[1] or '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Verify if it's a valid image
        try:
            with Image.open(file_path) as img:
                img.verify()
            self._log(f"Image saved successfully: {file_path}")
            return file_path
        except Exception as e:
            os.remove(file_path)  # Delete invalid file
            raise ValueError(f"Invalid image file: {str(e)}")
    
    def cleanup_temp_files(self, file_paths: list):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self._log(f"Deleted temporary file: {file_path}")
            except Exception as e:
                self._log(f"Failed to delete file {file_path}: {str(e)}", "WARNING")
