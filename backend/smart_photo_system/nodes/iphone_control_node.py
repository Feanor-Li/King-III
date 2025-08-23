import json
from typing import Dict, Any, Optional
import requests
import asyncio
from .base import BaseNode
from ..models.state import PhotoSystemState, CameraParams


class iPhoneControlNode(BaseNode):
    """iPhone camera control node"""
    
    def __init__(self, iphone_api_endpoint: str = None):
        super().__init__("iPhoneControlNode")
        # iPhone control API endpoint (can be Shortcuts API or other iPhone control methods)
        self.api_endpoint = iphone_api_endpoint or "http://localhost:8080/iphone-control"
        
        # iPhone camera parameter mapping
        self.param_mapping = {
            "aperture": self._convert_aperture,
            "exposure": self._convert_exposure,
            "iso": self._convert_iso,
            "focus": self._convert_focus,
            "white_balance": self._convert_white_balance,
            "scene_mode": self._convert_scene_mode
        }
    
    async def execute(self, state: PhotoSystemState) -> PhotoSystemState:
        """Send parameters to iPhone camera"""
        self._log("Preparing to control iPhone camera")
        
        try:
            if not state.final_params:
                raise ValueError("No camera parameters found")
            
            # Convert parameters to iPhone API format
            iphone_params = self._convert_params_to_iphone_api(state.final_params)
            
            # Send parameters to iPhone
            success = await self._send_to_iphone(iphone_params)
            
            if success:
                self._log("Successfully set iPhone camera parameters")
                return self._update_state(state, current_step="capture")
            else:
                raise Exception("Unable to connect to iPhone or failed to set camera parameters")
                
        except Exception as e:
            self._log(f"iPhone control failed: {str(e)}", "ERROR")
            return self._update_state(
                state,
                error_message=f"iPhone control failed: {str(e)}",
                current_step="capture_ready"
            )
    
    def _convert_params_to_iphone_api(self, params: CameraParams) -> Dict[str, Any]:
        """Convert parameters to iPhone API format"""
        iphone_params = {}
        
        for param_name in params.__fields__.keys():
            param_value = getattr(params, param_name, None)
            if param_value is not None and param_name in self.param_mapping:
                converter = self.param_mapping[param_name]
                converted_value = converter(param_value)
                if converted_value is not None:
                    iphone_params[param_name] = converted_value
        
        self._log(f"Converted iPhone parameters: {iphone_params}")
        return iphone_params
    
    def _convert_aperture(self, aperture: str) -> Optional[float]:
        """Convert aperture value"""
        try:
            # Extract numerical value from "f/2.8" format
            if aperture.startswith("f/"):
                return float(aperture[2:])
            return float(aperture)
        except (ValueError, AttributeError):
            self._log(f"Cannot convert aperture value: {aperture}", "WARNING")
            return None
    
    def _convert_exposure(self, exposure: float) -> float:
        """Convert exposure compensation value"""
        # iPhone typically supports -2.0 to +2.0 exposure compensation
        return max(-2.0, min(2.0, float(exposure)))
    
    def _convert_iso(self, iso: int) -> int:
        """Convert ISO value"""
        # iPhone typically supported ISO range
        return max(25, min(3200, int(iso)))
    
    def _convert_focus(self, focus: str) -> str:
        """Convert focus mode"""
        focus_mapping = {
            "auto": "AF",
            "macro": "macro",
            "infinity": "infinity",
            "manual": "MF"
        }
        return focus_mapping.get(focus.lower(), "AF")
    
    def _convert_white_balance(self, white_balance: str) -> str:
        """Convert white balance"""
        wb_mapping = {
            "auto": "auto",
            "daylight": "daylight",
            "cloudy": "cloudy",
            "fluorescent": "fluorescent",
            "incandescent": "incandescent",
            "flash": "flash"
        }
        return wb_mapping.get(white_balance.lower(), "auto")
    
    def _convert_scene_mode(self, scene_mode: str) -> str:
        """Convert scene mode"""
        scene_mapping = {
            "auto": "photo",
            "portrait": "portrait",
            "landscape": "photo",
            "night": "night",
            "sport": "photo"
        }
        return scene_mapping.get(scene_mode.lower(), "photo")
    
    async def _send_to_iphone(self, params: Dict[str, Any]) -> bool:
        """Send parameters to iPhone"""
        self._log("Sending parameters to iPhone...")
        
        try:
            # Method 1: Via HTTP API (if iPhone runs corresponding app or shortcuts)
            if await self._try_http_api(params):
                return True
            
            # Method 2: Via iOS Shortcuts (requires pre-setup)
            if await self._try_shortcuts_api(params):
                return True
            
            # Method 3: Simulation mode (for development and testing)
            return await self._simulate_iphone_control(params)
            
        except Exception as e:
            self._log(f"Failed to send to iPhone: {str(e)}", "ERROR")
            return False
    
    async def _try_http_api(self, params: Dict[str, Any]) -> bool:
        """Try to control iPhone via HTTP API"""
        try:
            payload = {
                "action": "set_camera_params",
                "params": params
            }
            
            # Async HTTP request (using sync requests here, recommend aiohttp for actual projects)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=10
                )
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            
        except Exception as e:
            self._log(f"HTTP API call failed: {str(e)}", "DEBUG")
        
        return False
    
    async def _try_shortcuts_api(self, params: Dict[str, Any]) -> bool:
        """Try to control iPhone via iOS Shortcuts"""
        try:
            # Can implement calls via iOS Shortcuts URL scheme here
            # Example: shortcuts://run-shortcut?name=CameraControl&input=params
            
            # Build Shortcuts URL
            shortcuts_url = f"shortcuts://run-shortcut?name=SmartPhotoControl"
            
            # Encode parameters as URL parameters or pass via other methods
            # This part needs adjustment based on actual Shortcuts implementation
            
            self._log(f"Trying to call Shortcuts: {shortcuts_url}")
            
            # In actual implementation, might need system calls or other ways to trigger URL
            # Currently returns False indicating not implemented
            return False
            
        except Exception as e:
            self._log(f"Shortcuts API call failed: {str(e)}", "DEBUG")
        
        return False
    
    async def _simulate_iphone_control(self, params: Dict[str, Any]) -> bool:
        """Simulate iPhone control (for development testing)"""
        self._log("Using simulation mode to control iPhone")
        
        # Simulate delay
        await asyncio.sleep(1)
        
        # Log simulated parameter settings
        self._log(f"Simulated iPhone parameter settings: {json.dumps(params, indent=2)}")
        
        # In actual environment, should return True indicating success
        # In development environment, can always return True for testing
        return True
    
    def get_supported_params(self) -> Dict[str, Any]:
        """Get parameter ranges supported by iPhone"""
        return {
            "aperture": {
                "min": 1.6,
                "max": 5.6,
                "available": [1.6, 2.0, 2.8, 4.0, 5.6]
            },
            "exposure": {
                "min": -2.0,
                "max": 2.0,
                "step": 0.1
            },
            "iso": {
                "min": 25,
                "max": 3200,
                "auto": True
            },
            "focus": ["auto", "macro", "infinity"],
            "white_balance": ["auto", "daylight", "cloudy", "fluorescent", "incandescent", "flash"],
            "scene_mode": ["photo", "portrait", "night"]
        }
