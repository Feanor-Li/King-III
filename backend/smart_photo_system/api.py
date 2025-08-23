import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import asyncio

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .models.state import PhotoSystemState, CameraParams
from .graph import SmartPhotoGraph


# API request/response models
class RefinementRequest(BaseModel):
    session_id: str
    user_input: str


class SessionResponse(BaseModel):
    session_id: str
    current_step: str
    error_message: Optional[str] = None
    

class StatusResponse(BaseModel):
    session_id: str
    current_step: str
    analysis: Optional[Dict[str, Any]] = None
    final_params: Optional[Dict[str, Any]] = None
    refinements: list = []
    captured_photo: Optional[str] = None
    error_message: Optional[str] = None


class SmartPhotoAPI:
    """FastAPI interface for smart photo system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Create FastAPI application
        self.app = FastAPI(
            title="Smart Photo System API",
            description="Smart photo system based on LangGraph",
            version="1.0.0"
        )
        
        # Session storage (production environment should use Redis or database)
        self.sessions: Dict[str, PhotoSystemState] = {}
        
        # Create graph instance
        self.photo_graph = SmartPhotoGraph(config)
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.post("/upload", response_model=SessionResponse)
        async def upload_photo(file: UploadFile = File(...)):
            """Upload reference photo and start analysis"""
            try:
                # Create new session
                session_id = str(uuid.uuid4())
                
                # Validate file type
                if not file.content_type.startswith('image/'):
                    raise HTTPException(status_code=400, detail="Only image files are supported")
                
                # Save uploaded file
                file_content = await file.read()
                saved_path = await self.photo_graph.upload_node.save_uploaded_file(
                    file_content, file.filename
                )
                
                # Create initial state
                state = PhotoSystemState(
                    session_id=session_id,
                    photo_ref=saved_path,
                    current_step="analyze"
                )
                
                # Run analysis step
                analyzed_state = await self.photo_graph.run_single_step(state, "analyze")
                
                # Save session
                self.sessions[session_id] = analyzed_state
                
                return SessionResponse(
                    session_id=session_id,
                    current_step=analyzed_state.current_step,
                    error_message=analyzed_state.error_message
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        
        @self.app.get("/status/{session_id}", response_model=StatusResponse)
        async def get_status(session_id: str):
            """Get session status"""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            state = self.sessions[session_id]
            
            return StatusResponse(
                session_id=session_id,
                current_step=state.current_step,
                analysis=state.analysis.model_dump() if state.analysis else None,
                final_params=state.final_params.model_dump() if state.final_params else None,
                refinements=[r.model_dump() for r in state.refinements],
                captured_photo=state.captured_photo,
                error_message=state.error_message
            )
        
        @self.app.post("/refine", response_model=SessionResponse)
        async def refine_parameters(request: RefinementRequest):
            """Process user's refinement instructions"""
            if request.session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            try:
                state = self.sessions[request.session_id]
                
                # Process refinement
                updated_state = await self.photo_graph.process_refinement(
                    state, request.user_input
                )
                
                # Update session
                self.sessions[request.session_id] = updated_state
                
                return SessionResponse(
                    session_id=request.session_id,
                    current_step=updated_state.current_step,
                    error_message=updated_state.error_message
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")
        
        @self.app.post("/capture/{session_id}", response_model=SessionResponse)
        async def capture_photo(session_id: str, background_tasks: BackgroundTasks):
            """Trigger photo capture"""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            try:
                state = self.sessions[session_id]
                
                # First control iPhone camera
                controlled_state = await self.photo_graph.run_single_step(state, "control")
                
                if controlled_state.error_message:
                    self.sessions[session_id] = controlled_state
                    return SessionResponse(
                        session_id=session_id,
                        current_step=controlled_state.current_step,
                        error_message=controlled_state.error_message
                    )
                
                # Then capture photo
                captured_state = await self.photo_graph.run_single_step(controlled_state, "capture")
                
                # Update session
                self.sessions[session_id] = captured_state
                
                # Background task: clean up old photos
                background_tasks.add_task(self.photo_graph.capture_node.cleanup_photos)
                
                return SessionResponse(
                    session_id=session_id,
                    current_step=captured_state.current_step,
                    error_message=captured_state.error_message
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Photo capture failed: {str(e)}")
        
        @self.app.get("/photo/{session_id}")
        async def get_captured_photo(session_id: str):
            """Get captured photo"""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            state = self.sessions[session_id]
            
            if not state.captured_photo:
                raise HTTPException(status_code=404, detail="No captured photo found")
            
            if not os.path.exists(state.captured_photo):
                raise HTTPException(status_code=404, detail="Photo file does not exist")
            
            return FileResponse(
                state.captured_photo,
                media_type='image/jpeg',
                filename=f"captured_{session_id}.jpg"
            )
        
        @self.app.delete("/session/{session_id}")
        async def delete_session(session_id: str):
            """Delete session and related files"""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            state = self.sessions[session_id]
            
            # Clean up temporary files
            files_to_delete = []
            if state.photo_ref:
                files_to_delete.append(state.photo_ref)
            if state.captured_photo:
                files_to_delete.append(state.captured_photo)
            files_to_delete.extend(state.temp_files)
            
            for file_path in files_to_delete:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Failed to delete file {file_path}: {str(e)}")
            
            # Delete session
            del self.sessions[session_id]
            
            return {"message": "Session deleted"}
        
        @self.app.get("/sessions")
        async def list_sessions():
            """List all active sessions"""
            sessions_info = []
            for session_id, state in self.sessions.items():
                sessions_info.append({
                    "session_id": session_id,
                    "current_step": state.current_step,
                    "has_error": state.error_message is not None,
                    "has_photo": state.captured_photo is not None
                })
            
            return {"sessions": sessions_info}
        
        @self.app.get("/graph/info")
        async def get_graph_info():
            """Get graph workflow information"""
            return {
                "description": self.photo_graph.get_graph_visualization(),
                "supported_steps": self.photo_graph.get_supported_steps()
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "active_sessions": len(self.sessions)
            }
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions"""
        current_time = datetime.now()
        sessions_to_delete = []
        
        for session_id, state in self.sessions.items():
            # Assumes we have creation time, actual implementation needs created_at field in state
            # Simplified version: directly clean all sessions with error status
            if state.error_message and state.current_step in ["upload", "analyze"]:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            try:
                del self.sessions[session_id]
                print(f"Cleaned session: {session_id}")
            except Exception as e:
                print(f"Failed to clean session {session_id}: {str(e)}")


def create_app(config: Dict[str, Any] = None) -> FastAPI:
    """Create FastAPI application"""
    api = SmartPhotoAPI(config)
    return api.app


# Application instance for deployment
app = create_app()
