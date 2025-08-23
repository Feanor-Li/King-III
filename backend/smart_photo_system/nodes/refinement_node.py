import re
from datetime import datetime
from typing import Dict, Any, Optional
from .base import BaseNode
from ..models.state import PhotoSystemState, RefinementAction, CameraParams


class RefinementNode(BaseNode):
    """Node for processing user refinement instructions"""
    
    def __init__(self):
        super().__init__("RefinementNode")
        # Define parameter mapping keywords
        self.param_keywords = {
            "exposure": ["exposure", "bright", "brightness", "dark", "darkness", "lighting"],
            "aperture": ["aperture", "blur", "background", "bokeh", "depth of field", "f/"],
            "iso": ["iso", "grain", "noise", "sensitivity"],
            "focus": ["focusing", "sharp", "clarity", "clear", "macro focus", "infinity focus"],
            "white_balance": ["white balance", "temperature", "warm", "cool", "color temperature", "tint"],
            "scene_mode": ["scene mode", "portrait mode", "landscape mode", "night mode", "sport mode", "macro mode"]
        }
        
        # Define adjustment direction keywords
        self.adjustment_keywords = {
            "increase": ["increase", "more", "higher", "up", "brighter", "boost", "enhance", "raise"],
            "decrease": ["decrease", "less", "lower", "down", "darker", "reduce", "diminish", "drop"]
        }
    
    async def execute(self, state: PhotoSystemState) -> PhotoSystemState:
        """Process refinement instructions"""
        self._log("Preparing to process user refinement")
        
        # If no refinement to process, return directly
        # This method mainly supports loop calls
        if state.current_step == "ready_for_refinement":
            return self._update_state(state, current_step="capture_ready")
        
        return state
    
    async def process_user_input(self, state: PhotoSystemState, user_input: str) -> PhotoSystemState:
        """Process user's natural language input"""
        self._log(f"Processing user input: {user_input}")
        
        try:
            # Parse user instructions
            parsed_adjustments = self._parse_user_input(user_input)
            
            if not parsed_adjustments:
                self._log("No valid adjustment instructions recognized", "WARNING")
                return self._update_state(
                    state,
                    error_message="Unable to understand your instructions, please try more specific descriptions"
                )
            
            # Apply adjustments to current parameters
            new_params = self._apply_adjustments(state.final_params or CameraParams(), parsed_adjustments)
            
            # Create refinement record
            refinement = RefinementAction(
                user_input=user_input,
                delta=parsed_adjustments,
                timestamp=datetime.now().isoformat()
            )
            
            # Update state
            updated_refinements = state.refinements + [refinement]
            
            updated_state = self._update_state(
                state,
                final_params=new_params,
                refinements=updated_refinements,
                current_step="capture_ready"
            )
            
            self._log(f"Applied adjustments: {parsed_adjustments}")
            return updated_state
            
        except Exception as e:
            self._log(f"Failed to process refinement: {str(e)}", "ERROR")
            return self._update_state(
                state,
                error_message=f"Failed to process instructions: {str(e)}"
            )
    
    def _parse_user_input(self, user_input: str) -> Dict[str, Any]:
        """Parse user's natural language input"""
        user_input = user_input.lower()
        adjustments = {}
        
        # Parse exposure adjustment
        exposure_adj = self._parse_exposure_adjustment(user_input)
        if exposure_adj is not None:
            adjustments["exposure"] = exposure_adj
        
        # Parse aperture adjustment
        aperture_adj = self._parse_aperture_adjustment(user_input)
        if aperture_adj:
            adjustments["aperture"] = aperture_adj
        
        # Parse ISO adjustment
        iso_adj = self._parse_iso_adjustment(user_input)
        if iso_adj is not None:
            adjustments["iso"] = iso_adj
        
        # Parse focus adjustment
        focus_adj = self._parse_focus_adjustment(user_input)
        if focus_adj:
            adjustments["focus"] = focus_adj
        
        # Parse white balance adjustment
        wb_adj = self._parse_white_balance_adjustment(user_input)
        if wb_adj:
            adjustments["white_balance"] = wb_adj
        
        # Parse scene mode adjustment
        scene_adj = self._parse_scene_mode_adjustment(user_input)
        if scene_adj:
            adjustments["scene_mode"] = scene_adj
        
        return adjustments
    
    def _parse_exposure_adjustment(self, text: str) -> Optional[float]:
        """Parse exposure adjustment"""
        # Look for explicit numeric adjustments
        exposure_match = re.search(r'(exposure|bright|dark).*?([+-]?\d+\.?\d*)', text)
        if exposure_match:
            return float(exposure_match.group(2))
        
        # Look for directional adjustments
        exposure_keywords = self.param_keywords["exposure"]
        if any(keyword in text for keyword in exposure_keywords):
            if any(keyword in text for keyword in self.adjustment_keywords["increase"]):
                return 0.5  # Increase exposure
            elif any(keyword in text for keyword in self.adjustment_keywords["decrease"]):
                return -0.5  # Decrease exposure
        
        return None
    
    def _parse_aperture_adjustment(self, text: str) -> Optional[str]:
        """Parse aperture adjustment"""
        # Look for explicit f-values
        f_match = re.search(r'f[/\\]?(\d+\.?\d*)', text)
        if f_match:
            return f"f/{f_match.group(1)}"
        
        # Infer aperture based on requirements
        if "blur" in text or "background" in text or "bokeh" in text:
            return "f/1.6"  # Large aperture
        elif "sharp" in text or "depth of field" in text or "clarity" in text:
            return "f/5.6"  # Small aperture
        elif "aperture" in text:
            if any(keyword in text for keyword in self.adjustment_keywords["increase"]):
                return "f/1.6"  # Larger aperture
            elif any(keyword in text for keyword in self.adjustment_keywords["decrease"]):
                return "f/5.6"  # Smaller aperture
        
        return None
    
    def _parse_iso_adjustment(self, text: str) -> Optional[int]:
        """Parse ISO adjustment"""
        # Look for explicit ISO values
        iso_match = re.search(r'iso.*?(\d+)', text)
        if iso_match:
            return int(iso_match.group(1))
        
        # Directional adjustments
        iso_keywords = self.param_keywords["iso"]
        if any(keyword in text for keyword in iso_keywords):
            if any(keyword in text for keyword in self.adjustment_keywords["increase"]):
                return 800  # Increase ISO
            elif any(keyword in text for keyword in self.adjustment_keywords["decrease"]):
                return 200  # Decrease ISO
        
        return None
    
    def _parse_focus_adjustment(self, text: str) -> Optional[str]:
        """Parse focus adjustment"""
        if "macro focus" in text or "macro" in text or "close" in text:
            return "macro"
        elif "infinity focus" in text or "infinity" in text or "far" in text or "distance" in text:
            return "infinity"
        elif "auto focus" in text or "automatic focus" in text:
            return "auto"
        
        return None
    
    def _parse_white_balance_adjustment(self, text: str) -> Optional[str]:
        """Parse white balance adjustment"""
        if "cool" in text or "blue" in text or "cold" in text:
            return "cloudy"
        elif "warm" in text or "yellow" in text or "orange" in text:
            return "incandescent"
        elif "daylight" in text or "sun" in text or "natural" in text:
            return "daylight"
        elif "auto white balance" in text or "automatic white balance" in text:
            return "auto"
        
        return None
    
    def _parse_scene_mode_adjustment(self, text: str) -> Optional[str]:
        """Parse scene mode adjustment"""
        if "portrait mode" in text or "portrait" in text or "people" in text or "person" in text:
            return "portrait"
        elif "landscape mode" in text or "landscape" in text or "scenery" in text or "nature" in text:
            return "landscape"
        elif "night mode" in text or "night scene" in text or ("night" in text and "mode" in text) or "evening" in text:
            return "night"
        elif "sport mode" in text or "sport" in text or "action" in text or "movement" in text:
            return "sport"
        elif "auto scene" in text or "automatic scene" in text:
            return "auto"
        
        return None
    
    def _apply_adjustments(self, current_params: CameraParams, adjustments: Dict[str, Any]) -> CameraParams:
        """Apply adjustments to current parameters"""
        new_params = current_params.model_copy()
        
        for param, value in adjustments.items():
            if param == "exposure":
                # Cumulative exposure adjustment
                current_exp = getattr(new_params, "exposure", 0) or 0
                new_params.exposure = self._clamp_exposure(current_exp + value)
            else:
                # Directly set other parameters
                setattr(new_params, param, value)
        
        return new_params
    
    def _clamp_exposure(self, exposure: float) -> float:
        """Limit exposure value range"""
        return max(-3.0, min(3.0, exposure))
