from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum


class RefinementAction(BaseModel):
    """Record of user refinement actions"""
    user_input: str = Field(description="User's natural language input")
    delta: Dict[str, Any] = Field(description="Parameter changes")
    timestamp: str = Field(description="Timestamp")


class CameraParams(BaseModel):
    """Camera parameters"""
    exposure: Optional[float] = None
    aperture: Optional[str] = None  # e.g., "f/1.6", "f/2.8"
    iso: Optional[int] = None
    focus: Optional[str] = None  # e.g., "auto", "macro", "infinity"
    white_balance: Optional[str] = None  # e.g., "auto", "daylight", "cloudy"
    scene_mode: Optional[str] = None  # e.g., "portrait", "landscape", "night"
    
    
class ImageAnalysis(BaseModel):
    """Image analysis results"""
    exposure: Optional[float] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    saturation: Optional[float] = None
    composition: Dict[str, Any] = Field(default_factory=dict)
    color_analysis: Dict[str, Any] = Field(default_factory=dict)
    scene_type: Optional[str] = None
    

class PhotoSystemState(BaseModel):
    """Complete system state"""
    # Original reference photo
    photo_ref: Optional[str] = Field(None, description="Original reference photo path")
    
    # Image analysis results
    analysis: Optional[ImageAnalysis] = Field(None, description="Image analysis results")
    
    # User refinement history
    refinements: List[RefinementAction] = Field(default_factory=list, description="User refinement history")
    
    # Final parameters
    final_params: Optional[CameraParams] = Field(None, description="Final camera parameters")
    
    # Capture results
    captured_photo: Optional[str] = Field(None, description="Final photo path/URL")
    
    # System state
    current_step: str = Field("upload", description="Current processing step")
    error_message: Optional[str] = Field(None, description="Error message")
    session_id: str = Field(description="Session ID")
    
    # Temporary data
    temp_files: List[str] = Field(default_factory=list, description="Temporary files list")
    
    class Config:
        arbitrary_types_allowed = True
